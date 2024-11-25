import sqlite3

def create_db():
    # データベースに接続（存在しない場合は作成される）
    conn = sqlite3.connect('karaoke.db')
    cursor = conn.cursor()

    # people テーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,  -- 年齢を格納するカラム
            email TEXT NOT NULL
        )
    ''')

    # songs テーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id TEXT NOT NULL,  -- Spotifyの曲IDを格納
            title TEXT NOT NULL,
            artist TEXT
        )
    ''')

    # performances テーブルを作成
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS performances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER,
            song_id TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(person_id) REFERENCES people(id),
            FOREIGN KEY(song_id) REFERENCES songs(song_id)
        )
    ''')

    # コミットして変更を保存
    conn.commit()
    # 接続を閉じる
    conn.close()

if __name__ == '__main__':
    create_db()
    print("データベースが作成されました")
