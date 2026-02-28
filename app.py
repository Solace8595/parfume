from flask import Flask, render_template
from llm.deepseek import ask_deepseek

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test_llm():
    prompt = "Подбери женский сладкий зимний аромат с ванилью"
    return ask_deepseek(prompt)

if __name__ == '__main__':
    print("🚀 Сервер запущен: http://localhost:5000")
    app.run(debug=True)
