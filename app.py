import sqlite3
from flask import Flask, request, redirect, url_for, render_template_string, flash

app = Flask(__name__)
app.secret_key = 'odev_gizli_anahtari'
DATABASE = 'veritabanı.db'

def init_db():
    """Veritabanını ve kullanıcılar tablosunu oluşturur."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# HTML Şablonları (Tek dosyada birleştirmek için string olarak tanımlandı)
BASE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Ödev Uygulaması</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        .container { max-width: 400px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h2 { text-align: center; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background-color: #007BFF; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background-color: #0056b3; }
        .message { color: green; text-align: center; margin-bottom: 10px; }
        .error { color: red; text-align: center; margin-bottom: 10px; }
        .nav { text-align: center; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

INDEX_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', """
<h2>Ana Sayfa</h2>
<p>Başarıyla giriş yaptınız!</p>
<p>Hoş geldiniz, <strong>{{ username }}</strong>!</p>
<div class="nav">
    <a href="/logout">Çıkış Yap</a>
</div>
""")

LOGIN_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', """
<h2>Giriş Yap</h2>
<form method="POST" action="/login">
    <input type="text" name="username" placeholder="Kullanıcı Adı" required>
    <input type="password" name="password" placeholder="Şifre" required>
    <button type="submit">Giriş Yap</button>
</form>
<div class="nav">
    Hesabınız yok mu? <a href="/register">Kaydolun</a>
</div>
""")

REGISTER_HTML = BASE_HTML.replace('{% block content %}{% endblock %}', """
<h2>Üye Ol</h2>
<form method="POST" action="/register">
    <input type="text" name="username" placeholder="Kullanıcı Adı" required>
    <input type="password" name="password" placeholder="Şifre" required>
    <button type="submit">Kaydol</button>
</form>
<div class="nav">
    Zaten üye misiniz? <a href="/login">Giriş Yapın</a>
</div>
""")

@app.route('/')
def index():
    # Giriş yapmamış kullanıcıları giriş sayfasına yönlendir
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # Açık metin (plain text) şifre
        
        try:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                # Şifre doğrudan/açık metin olarak kaydediliyor
                cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
                print(f">>> YENİ KULLANICI KAYDI -> Kullanıcı Adı: {username} | Şifre: {password}")
            flash('Başarıyla kayıt oldunuz! Şimdi giriş yapabilirsiniz.', 'message')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Bu kullanıcı adı zaten alınmış.', 'error')
            
    return render_template_string(REGISTER_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            # Açık metin karşılaştırması yapılıyor
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            
        if user:
            flash('Giriş başarılı!', 'message')
            return render_template_string(INDEX_HTML, username=username)
        else:
            flash('Hatalı kullanıcı adı veya şifre.', 'error')
            
    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    flash('Başarıyla çıkış yaptınız.', 'message')
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Veritabanını oluştur
    init_db()
    print("SQLite Veritabanı başarıyla hazırlandı.")
    # Uygulamayı lokalde çalıştırmak için (Colab harici kullanımda aktiftir)
app.run(debug=True)
