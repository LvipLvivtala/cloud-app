import os
import time
import psycopg2
from flask import Flask

app = Flask(__name__)

# Параметры подключения к PostgreSQL из переменных окружения Docker Compose
DB_HOST = os.environ.get("DB_HOST", "db")
DB_NAME = os.environ.get("DB_NAME", "cloudshop")
DB_USER = os.environ.get("DB_USER", "clouduser")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "cloudpassword")

def get_db_connection():
    """Подключение к базе данных с повторными попытками при старте"""
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            time.sleep(2)
    raise Exception("Не удалось подключиться к базе данных PostgreSQL")

def init_db():
    """Создание таблицы products (ЛР 5) и таблиц для доп. заданий"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # 1. Создаем таблицу товаров из Лабораторной работы №5
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            category VARCHAR(50),
            price DECIMAL(10,2),
            quantity INTEGER
        );
    """)
    
    # 2. Создаем таблицу заказов из дополнительного задания ЛР 5
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_name VARCHAR(100),
            product_id INTEGER,
            quantity INTEGER,
            order_date DATE
        );
    """)
    
    # 3. Наполняем таблицу начальными данными, если она пустая
    cur.execute("SELECT COUNT(*) FROM products;")
    if cur.fetchone()[0] == 0:
        initial_products = [
            ('Laptop Lenovo', 'Computer', 750000, 10),
            ('Mouse Logitech', 'Accessories', 25000, 50),
            ('Keyboard Logitech', 'Accessories', 45000, 30),
            ('Monitor Samsung', 'Monitor', 180000, 15),
            ('SSD 1TB', 'Storage', 70000, 20)
        ]
        cur.executemany(
            """
            INSERT INTO products (name, category, price, quantity)
            VALUES (%s, %s, %s, %s);
            """,
            initial_products
        )
        
    conn.commit()
    cur.close()
    conn.close()

# Главная страница (ЛР 7): вывод списка товаров из PostgreSQL
@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, category, price, quantity FROM products ORDER BY id;")
    products = cur.fetchall()
    cur.close()
    conn.close()
    
    items_html = ""
    for item in products:
        prod_id, name, category, price, quantity = item
        items_html += f"<li><b>{name}</b> ({category}) — {price} тенге (Остаток: {quantity} шт.)</li>\n"
    
    return f"""
    <h1>CloudShop</h1>
    <h2>Cloud Technologies Laboratory</h2>
    <h3>Список товаров из базы данных PostgreSQL (ЛР №5):</h3>
    <ul>
        {items_html}
    </ul>
    <hr>
    <h3>Навигация (ЛР №6):</h3>
    <ul>
        <li><a href="/about">About Us</a></li>
        <li><a href="/contact">Contact Page</a></li>
    </ul>
    """

# Страница About (ЛР 6)
@app.route("/about")
def about():
    return """
    <h1>About Us</h1>
    <p>My name is Yerakh</p>
    <a href="/">Back to Home</a>
    """

# Страница Contact (ЛР 6)
@app.route("/contact")
def contact():
    return """
    <h1>Contact Page</h1>
    <p>Email: support@cloudshop.kz</p>
    <a href="/">Back to Home</a>
    """

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
