from flask import Flask, request, jsonify, send_from_directory
from scraper import run_scraper
import os
import json

app = Flask(__name__, static_folder='../frontend')

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    keyword = data.get('keyword')
    pages = data.get('pages', 1)
    
    if not keyword:
        return jsonify({'error': 'Keyword is required'}), 400

    products = run_scraper(keyword, pages)
    return jsonify(products)

if __name__ == "__main__":
    from backend import app
    app.run(host='0.0.0.0', port=8000)
