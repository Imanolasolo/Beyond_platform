import sqlite3

def init_db():
    conn = sqlite3.connect("beyond.db")
    cursor = conn.cursor()

    # Tabla de roles
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)

    # Insertar roles por defecto si no existen
    default_roles = ["admin", "user free", "user premium", "coach"]
    for role in default_roles:
        cursor.execute("INSERT OR IGNORE INTO roles (name) VALUES (?)", (role,))

    # Tabla de usuarios (role ahora referencia a roles.name)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user free',
        FOREIGN KEY (role) REFERENCES roles(name)
    )
    """)

    # Tabla de videos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        description TEXT
    )
    """)

    # Tabla de podcasts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS podcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        description TEXT
    )
    """)

    # Tabla de summits
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS summits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        description TEXT
    )
    """)

    # Tabla de likes para videos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS video_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        video_id INTEGER NOT NULL,
        UNIQUE(user_id, video_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (video_id) REFERENCES videos(id)
    )
    """)

    # Tabla de likes para podcasts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS podcast_likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        podcast_id INTEGER NOT NULL,
        UNIQUE(user_id, podcast_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (podcast_id) REFERENCES podcasts(id)
    )
    """)

    # Crear un admin inicial si no existe
    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin")
        )

    conn.commit()
    conn.close()
    print("✅ Base de datos inicializada con éxito.")

if __name__ == "__main__":
    init_db()
