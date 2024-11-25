from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import openai
import os
from dotenv import load_dotenv
import sqlite3


# 変更
# .envファイルから環境変数をロード
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": 
                             "https://tech0-gen-8-step3-testapp-node1-11.azurewebsites.net:3000",
                             "http://localhost:3000"
                            }}) # CORS設定を更新

@app.route('/', methods=['GET'])
def hello():
    return jsonify({'message': 'Flask start!'})

# SpotifyのAPIキーとシークレット
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET =  os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_TOKEN_URL = 'https://accounts.spotify.com/api/token'


# アクセストークンを取得する関数
def get_spotify_access_token():
    auth_response = requests.post(SPOTIPY_TOKEN_URL, {
        'grant_type': 'client_credentials',
        'client_id': SPOTIPY_CLIENT_ID,
        'client_secret': SPOTIPY_CLIENT_SECRET,
    })
    
    # トークンが正しく取得できたか確認
    if auth_response.status_code != 200:
        raise Exception(f"Failed to get access token: {auth_response.text}")
    
    auth_response_data = auth_response.json()
    return auth_response_data['access_token']

def get_db_connection():
    conn = sqlite3.connect('karaoke.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register-performance', methods=['POST'])
def register_performance():
    try:
        print(request.get_json())
        data = request.get_json()
        person_id = data['person_id']
        song_id = data['song_id']  # ここで受け取るのはSpotifyのsong_id
        title = data.get('title')   # 曲のタイトルを受け取る
        artist = data.get('artist')  # アーティスト名を受け取る


        # データベースに接続
        conn = get_db_connection()
        cur = conn.cursor()

        # songs テーブルから song_id を確認
        cur.execute('SELECT * FROM songs WHERE song_id = ?', (song_id,))
        song = cur.fetchone()
        print(song)

        # 曲が存在しない場合、新しく追加する
        if not song:
            # title = 'なし'
            # artist = 'なし'
            cur.execute('INSERT INTO songs (song_id, title, artist) VALUES (?, ?, ?)', (song_id, title, artist))
            # cur.execute('INSERT INTO songs (song_id) VALUES (?)', (song_id))
            conn.commit()  # 曲情報をコミットして保存
            print(f"Added new song: {song_id}")

        # performances テーブルに挿入
        cur.execute('INSERT INTO performances (person_id, song_id) VALUES (?, ?)', (person_id, song_id))

        # コミットして変更を保存
        conn.commit()

        return jsonify({'message': 'Performance registered successfully'}), 201

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()  # 最後に接続を閉じる



# Spotify APIを使って曲を検索する関数
@app.route('/search', methods=['GET'])
def search_tracks():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400

    # トークンを取得
    token = get_spotify_access_token()
    
    headers = {
        'Authorization': f'Bearer {token}'  # ここでトークンをヘッダーに含める
    }
    
    search_url = 'https://api.spotify.com/v1/search'
    params = {
        'q': query,
        'type': 'track',
        'limit': 10
    }
    
    # Spotify APIにリクエストを送る
    response = requests.get(search_url, headers=headers, params=params)
    
    # レスポンスが正しく取得できたか確認
    if response.status_code != 200:
        return jsonify({'error': f"Failed to search: {response.text}"}), response.status_code
    
    data = response.json()

    # 必要な情報を抽出
    results = []
    for item in data['tracks']['items']:
        results.append({
            'id': item['id'],  # Spotifyのtrack IDを追加
            'title': item['name'],
            'artist': item['artists'][0]['name'],
            'image_url': item['album']['images'][0]['url'],
            'spotify_url': item['external_urls']['spotify']
        })

    return jsonify(results)

# people テーブルからデータ取得
@app.route('/people', methods=['GET'])
def get_people():
    try:
        # データベースに接続
        conn = get_db_connection()
        cur = conn.cursor()

        # people テーブルから全てのレコードを取得
        cur.execute('SELECT * FROM people')
        rows = cur.fetchall()

        # 結果をリストに変換
        people = []
        for row in rows:
            people.append({
                'id': row['id'],
                'name': row['name'],
                'email': row['email']
                # 必要に応じて他のフィールドも追加
            })

        return jsonify(people), 200

    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()  # 最後に接続を閉じる

# 登録した曲を確認
@app.route('/performances/<int:person_id>', methods=['GET'])
def get_performances(person_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # person_id に基づいて performances テーブルからデータを取得
        cur.execute('''
            SELECT performances.id, performances.song_id, performances.date, songs.title, songs.artist
            FROM performances
            JOIN songs ON performances.song_id = songs.song_id
            WHERE performances.person_id = ?
        ''', (person_id,))
        
        performances = cur.fetchall()

        # 結果をリストに変換
        result = []
        for performance in performances:
            result.append({
                'id': performance['id'],
                'song_id': performance['song_id'],
                'date': performance['date'],
                'title': performance['title'],
                'artist': performance['artist']
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port,debug=True)


