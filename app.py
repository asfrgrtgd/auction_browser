from flask import Flask, render_template, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/auction', methods=['POST'])
def auction():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSONデータがありません"}), 400

    # フロントエンドから送信された API キーを取得
    api_key = data.get("api_key")
    if not api_key:
        return jsonify({"error": "APIキーが指定されていません"}), 400

    search = data.get("search", "")
    sort = data.get("sort", "")
    page = data.get("page", 1)

    target_url = f"https://api.donutsmp.net/v1/auction/list/{page}"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {"search": search, "sort": sort}

    try:
        response = requests.post(target_url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # アイテムの個数を追加
        if 'result' in data:
            for item in data['result']:
                if 'item' in item:
                    # デフォルトの個数を1に設定
                    item['item']['count'] = item['item'].get('count', 1)
                    
        # Shulker Boxの場合、必要な情報のみを保持
        if 'auctions' in data:
            for auction in data['auctions']:
                if 'item' in auction and auction['item'].get('id', '').endswith('shulker_box'):
                    # 必要な情報のみを保持する新しい辞書を作成
                    filtered_auction = {
                        'item': auction['item'],
                        'price': auction['price'],
                        'end_time': auction['end_time'],
                        'seller': auction['seller']
                    }
                    # item内のcontentsを削除
                    if 'contents' in filtered_auction['item']:
                        del filtered_auction['item']['contents']
                    
                    # 元のオークションデータを必要な情報のみに置き換え
                    auction.clear()
                    auction.update(filtered_auction)
        
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
