from flask import Flask, render_template, request, jsonify
import uuid

from llm.deepseek import ask_deepseek
from llm.gigachat import ask_gigachat
from llm.perplexity import ask_perplexity
from llm.test import ask_test
from image_parse import delete_saved_image

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json(silent=True) or {}

    gender = (data.get('gender') or '').strip()
    aroma = (data.get('aroma') or '').strip()
    season = (data.get('season') or '').strip()
    associations = (data.get('associations') or '').strip()
    shop = (data.get('shop') or '').strip()
    llm = (data.get('llm') or '').strip()

    if not gender or not aroma or not season or not shop or not llm:
        return jsonify({
            "success": False,
            "error": "Пожалуйста, заполните все обязательные поля."
        }), 400

    request_id = str(uuid.uuid4())

    try:
        if llm == 'deepseek':
            result = ask_deepseek(gender, aroma, season, associations, shop)

        elif llm == 'gigachat':
            result = ask_gigachat(gender, aroma, season, associations, shop)

        elif llm == 'perplexity':
            result = ask_perplexity(gender, aroma, season, associations, shop)

        elif llm == 'test':
            result = ask_test(gender, aroma, season, associations, shop)

        else:
            return jsonify({
                "success": False,
                "error": "Неизвестная модель"
            }), 400

        return jsonify({
            "success": True,
            "request_id": request_id,
            "data": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/result/<request_id>')
def result(request_id):
    return render_template('result.html', request_id=request_id)


@app.route('/cleanup-result', methods=['POST'])
def cleanup_result():
    data = request.get_json(silent=True) or {}
    image_url = data.get('image_url', '')

    delete_saved_image(image_url)

    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(debug=True)