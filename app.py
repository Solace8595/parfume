"""
app.py - отображение страницы подбора парфюма
"""

from flask import Flask, render_template

# Создание приложения
app = Flask(__name__)

# Главная страница
@app.route('/')
def index():
    # Просто отображаем HTML файл
    return render_template('index.html')

# Запуск
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Сервер подбора парфюма запущен")
    print("📌 Адрес: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)