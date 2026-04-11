"""
Heyd Media App - Social Media Platform
Built with Python Flask & Django concepts
Author: Harivasanth Arava
"""

from flask import Flask, render_template, request
from flask import redirect, url_for, session, jsonify
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'heyd_media_secret_key'

# Database Configuration
DB_CONFIG = {
    'host':     os.environ.get('DB_HOST', 'localhost'),
    'user':     os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'root123'),
    'database': os.environ.get('DB_NAME', 'heydmediadb')
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

# ── HOME / FEED ──
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, u.username, u.profile_pic
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
        """)
        posts = cursor.fetchall()
        conn.close()
    except:
        posts = []
    return render_template('index.html',
                           posts=posts,
                           user=session['user'])

# ── SIGNUP ──
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email    = request.form['email']
        password = request.form['password']
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('signup.html', error=str(e))
    return render_template('signup.html')

# ── LOGIN ──
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE email=%s AND password=%s",
                (email, password)
            )
            user = cursor.fetchone()
            conn.close()
            if user:
                session['user'] = user['username']
                session['user_id'] = user['id']
                return redirect(url_for('home'))
            else:
                return render_template('login.html',
                                       error='Invalid credentials')
        except Exception as e:
            return render_template('login.html', error=str(e))
    return render_template('login.html')

# ── LOGOUT ──
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── UPLOAD POST ──
@app.route('/upload', methods=['POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))
    caption = request.form.get('caption', '')
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (user_id, caption) VALUES (%s, %s)",
            (session['user_id'], caption)
        )
        conn.commit()
        conn.close()
    except:
        pass
    return redirect(url_for('home'))

# ── LIKE POST ──
@app.route('/like/<int:post_id>')
def like(post_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'})
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO likes (post_id, user_id) VALUES (%s, %s)",
            (post_id, session['user_id'])
        )
        conn.commit()
        conn.close()
        return jsonify({'status': 'liked'})
    except:
        return jsonify({'status': 'already liked'})

# ── COMMENT ──
@app.route('/comment/<int:post_id>', methods=['POST'])
def comment(post_id):
    if 'user' not in session:
        return redirect(url_for('login'))
    text = request.form.get('comment', '')
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO comments (post_id, user_id, text) VALUES (%s, %s, %s)",
            (post_id, session['user_id'], text)
        )
        conn.commit()
        conn.close()
    except:
        pass
    return redirect(url_for('home'))

# ── FOLLOW ──
@app.route('/follow/<int:follow_id>')
def follow(follow_id):
    if 'user' not in session:
        return jsonify({'error': 'Not logged in'})
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO followers (follower_id, following_id) VALUES (%s, %s)",
            (session['user_id'], follow_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'status': 'following'})
    except:
        return jsonify({'status': 'already following'})

# ── PROFILE ──
@app.route('/profile/<username>')
def profile(username):
    if 'user' not in session:
        return redirect(url_for('login'))
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,))
        user = cursor.fetchone()
        cursor.execute(
            "SELECT * FROM posts WHERE user_id=%s ORDER BY created_at DESC",
            (user['id'],))
        posts = cursor.fetchall()
        conn.close()
    except:
        user = {'username': username}
        posts = []
    return render_template('profile.html',
                           profile_user=user,
                           posts=posts)

# ── HEALTH CHECK ──
@app.route('/health')
def health():
    return jsonify({
        "status": "running",
        "app": "Heyd Media App",
        "author": "Harivasanth Arava"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
