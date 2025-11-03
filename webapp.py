import os
from flask import Flask, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, 'vk_app')

app = Flask(__name__, static_folder=APP_DIR, static_url_path='')


@app.route('/')
def index():
    # Корневая стартовая страница из репозитория
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/app')
def app_index():
    # Явный маршрут для мини‑приложения
    return send_from_directory(APP_DIR, 'index.html')


@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(APP_DIR, path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))


