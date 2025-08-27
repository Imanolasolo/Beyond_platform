import streamlit as st
import jwt
import datetime
import sqlite3
from pathlib import Path

# ========================
# CONFIGURACIÓN JWT
# ========================
JWT_SECRET = "super_secret_key"
JWT_ALGORITHM = "HS256"

# ========================
# BASE DE DATOS
# ========================
DB_PATH = Path("beyond.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Tabla de usuarios
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    role TEXT
                )''')
    conn.commit()
    conn.close()

def check_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

# ========================
# JWT HELPERS
# ========================
def create_token(username, role):
    payload = {
        "username": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        st.error("⚠️ Sesión expirada. Por favor, inicie sesión de nuevo.")
        return None
    except jwt.InvalidTokenError:
        return None

# ========================
# MÓDULOS
# ========================
def dashboard_module(user):
    st.subheader("📊 Panel de Control")
    st.write(f"Bienvenido **{user['username']}**, rol: {user['role']}")

def crud_module():
    st.subheader("🗄️ CRUDs")
    st.info("Aquí irán los formularios para crear, leer, actualizar y borrar datos.")

def beyond_videos():
    st.subheader("🎥 Beyond Videos")
    st.info("Aquí podrás cargar y ver videos de YouTube.")

def beyond_podcasts():
    st.subheader("🎙️ Beyond Podcasts")
    st.info("Aquí irán los podcasts.")

def beyond_summit():
    st.subheader("🌍 Beyond Summit")
    st.info("Módulo de eventos y conferencias.")

# ========================
# LOGIN & APP WRAPPER
# ========================
def login_screen():
    st.title("🔑 Beyond Summit Next Gen")
    st.subheader("Iniciar Sesión")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Login"):
        user = check_user(username, password)
        if user:
            token = create_token(user[1], user[3])  # username, role
            st.session_state["token"] = token
            st.success("✅ Login exitoso")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")

def main_app(user):
    st.sidebar.title("📍 Navegación")
    option = st.sidebar.radio("Ir a:", ["Dashboard", "CRUDs", "Beyond Videos", "Beyond Podcasts", "Beyond Summit"])

    if option == "Dashboard":
        dashboard_module(user)
    elif option == "CRUDs":
        crud_module()
    elif option == "Beyond Videos":
        beyond_videos()
    elif option == "Beyond Podcasts":
        beyond_podcasts()
    elif option == "Beyond Summit":
        beyond_summit()

# ========================
# ENTRYPOINT
# ========================
def main():
    init_db()

    if "token" not in st.session_state:
        login_screen()
    else:
        decoded = verify_token(st.session_state["token"])
        if decoded:
            user = {"username": decoded["username"], "role": decoded["role"]}
            main_app(user)
        else:
            login_screen()

if __name__ == "__main__":
    main()
