from flask import Flask, request, jsonify, send_from_directory
from scraper import run_scraper
import os
import json
from flask_cors import CORS  # ✅ استيراد CORS

app = Flask(__name__, static_folder='../frontend')
CORS(app)  # ✅ تفعيل CORS للسماح بالاتصال من أي مصدر

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
    port = int(os.environ.get("PORT", 10000))  # ✅ ضبط المنفذ تلقائيًا إذا كان محدد في البيئة
    app.run(host='0.0.0.0', port=port)
