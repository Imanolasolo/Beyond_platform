import sqlite3

DB_PATH = "beyond.db"

def like_video(user_id, video_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO video_likes (user_id, video_id) VALUES (?, ?)", (user_id, video_id))
        conn.commit()
    finally:
        conn.close()

def unlike_video(user_id, video_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM video_likes WHERE user_id = ? AND video_id = ?", (user_id, video_id))
        conn.commit()
    finally:
        conn.close()

def get_video_likes(video_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM video_likes WHERE video_id = ?", (video_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def user_liked_video(user_id, video_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM video_likes WHERE user_id = ? AND video_id = ?", (user_id, video_id))
    liked = cursor.fetchone() is not None
    conn.close()
    return liked

def like_podcast(user_id, podcast_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO podcast_likes (user_id, podcast_id) VALUES (?, ?)", (user_id, podcast_id))
        conn.commit()
    finally:
        conn.close()

def unlike_podcast(user_id, podcast_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM podcast_likes WHERE user_id = ? AND podcast_id = ?", (user_id, podcast_id))
        conn.commit()
    finally:
        conn.close()

def get_podcast_likes(podcast_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM podcast_likes WHERE podcast_id = ?", (podcast_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def user_liked_podcast(user_id, podcast_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM podcast_likes WHERE user_id = ? AND podcast_id = ?", (user_id, podcast_id))
    liked = cursor.fetchone() is not None
    conn.close()
    return liked
