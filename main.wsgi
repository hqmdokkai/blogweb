from flask import Flask, render_template_string, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Thay đổi khóa bí mật theo yêu cầu

# Cấu hình SQLite3
DATABASE = 'blog_db.sqlite3'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Tạo bảng nếu chưa tồn tại
def create_tables():
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
        ''')

        connection.commit()
    except sqlite3.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        connection.close()

# Tạo bảng khi ứng dụng khởi động
create_tables()

# Template cho trang chính (index)
index_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog của Tôi</title>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
    <style>
        .post-content {
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }
    </style>
</head>
<body>
    <div class="container">
        <p>Xin chào, {{ session['username'] }}!</p>
        <h1 class="my-4">Danh sách bài viết</h1>
        {% if 'username' in session %}
            <p>Chào, {{ session['username'] }}! <a href="{{ url_for('logout') }}">Đăng xuất</a></p>
            {% if session['username'] == 'admin' %}
                <p>
                    <a href="{{ url_for('manage_users') }}" class="btn btn-secondary">Quản lý người dùng</a>
                </p>
            {% endif %}
            <p><a href="{{ url_for('add_post') }}" class="btn btn-primary">Thêm bài viết</a></p>
        {% else %}
            <p><a href="{{ url_for('login') }}" class="btn btn-primary">Đăng nhập</a></p>
            <p><a href="{{ url_for('register') }}" class="btn btn-primary">Đăng ký</a></p>
        {% endif %}
        
        {% if posts %}
            {% for post in posts %}
                <div class="card mb-4">
                    <div class="card-body">
                        <h3 class="card-title">
                            <a href="{{ url_for('post_detail', post_id=post['id']) }}">
                                {{ post['title'] }}
                            </a>
                        </h3>
                        <p class="card-text post-content">{{ post['content'] | safe }}</p>
                        <p class="text-muted">Posted on {{ post['created_at'] }}</p>
                        {% if 'username' in session %}
                            {% if session['username'] == 'admin' or session.get('role') == 'admin' or post['user_id'] == session.get('user_id') %}
                                <form action="{{ url_for('delete_post', post_id=post['id']) }}" method="POST" style="display:inline;">
                                    <button type="submit" class="btn btn-danger btn-sm">Xóa</button>
                                </form>
                            {% endif %}
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        {% else %}
            <p>Không có bài viết nào.</p>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM posts ORDER BY created_at DESC')
    posts = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template_string(index_template, posts=posts)

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if 'username' not in session:
        return "Bạn không có quyền thực hiện hành động này", 403

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content'].replace('\n', '<br>')  # Thay thế ký tự xuống dòng
        username = session['username']

        # Lấy user_id từ username
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user is None:
            cursor.close()
            connection.close()
            return "Người dùng không tồn tại", 404
        
        user_id = user['id']
        
        # Thêm bài viết
        cursor.execute(
            'INSERT INTO posts (title, content, user_id) VALUES (?, ?, ?)',
            (title, content, user_id)
        )
        connection.commit()
        cursor.close()
        connection.close()

        return redirect(url_for('index'))

    return render_template('add_post.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    post = cursor.fetchone()
    cursor.execute('SELECT * FROM comments WHERE post_id = ? ORDER BY created_at DESC', (post_id,))
    comments = cursor.fetchall()
    cursor.close()
    connection.close()
    if post:
        return render_template('post_detail.html', post=post, comments=comments)
    else:
        return "Bài viết không tồn tại", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            session['username'] = user['username']
            session['role'] = user['role']  # Lưu role vào session
            session['user_id'] = user['id']  # Lưu user_id vào session
            return redirect(url_for('index'))
        else:
            return "Tên đăng nhập hoặc mật khẩu không đúng", 401
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect(url_for('login'))
        except sqlite3.Error as err:
            connection.rollback()
            cursor.close()
            connection.close()
            return f"Error: {err}", 400
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    if 'username' not in session:
        return "Bạn không có quyền thực hiện hành động này", 403
    
    username = session.get('username')
    user_role = session.get('role')
    user_id = session.get('user_id')
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Kiểm tra bài viết có thuộc về người dùng hay không
    if user_role == 'admin':
        cursor.execute('SELECT * FROM posts WHERE id = ?', (post_id,))
    else:
        cursor.execute('SELECT * FROM posts WHERE id = ? AND user_id = ?', (post_id, user_id))
    
    post = cursor.fetchone()
    
    if not post:
        cursor.close()
        connection.close()
        return "Bài viết không tồn tại hoặc bạn không có quyền xóa bài viết này", 403
    
    cursor.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('index'))

@app.route('/manage_users', methods=['GET', 'POST'])
def manage_users():
    if 'username' not in session or session['username'] != 'admin':
        return "Bạn không có quyền thực hiện hành động này", 403
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    if request.method == 'POST':
        # Xử lý xóa người dùng
        if 'delete_user' in request.form:
            user_id_to_delete = request.form['delete_user']
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id_to_delete,))
            connection.commit()
        
        # Xử lý thay đổi vai trò
        if 'change_role' in request.form:
            user_id = request.form['user_id']
            new_role = request.form['new_role']
            cursor.execute('UPDATE users SET role = ? WHERE id = ?', (new_role, user_id))
            connection.commit()
    
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    cursor.close()
    connection.close()
    
    return render_template('manage_users.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
