import sqlite3

# データベースに接続
conn = sqlite3.connect('karaoke.db')

# カーソルを作成
cursor = conn.cursor()

# peopleテーブルにデータを挿入
cursor.execute("INSERT INTO people (name, age, email) VALUES (?, ?, ?)", ('Taro', 25, 'Hanaco@example.com'))
cursor.execute("INSERT INTO people (name, age, email) VALUES (?, ?, ?)", ('Hanaco', 25, 'Hanaco@example.com'))

# songsテーブルにデータを挿入
cursor.execute("INSERT INTO songs (song_id, title, artist) VALUES (?, ?, ?)", ('01IZAuQsBO00iLKFO9LsFf', '愛を伝えたいだとか', 'Aimyon'))

# performancesテーブルにデータを挿入
cursor.execute("INSERT INTO performances (person_id, song_id) VALUES (?, ?)", (1, '01IZAuQsBO00iLKFO9LsFf'))

# コミットして変更を保存
conn.commit()

# 接続を閉じる
conn.close()

print("データが挿入されました")
