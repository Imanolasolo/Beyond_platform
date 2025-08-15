# app.py
"""
IDEAverse Mini Platform – Streamlit + SQLite + JWT

Features
- Admin creates users (roles: admin, user) and uploads YouTube links.
- Auth with username+password -> JWT stored in session.
- Users (previously created by admin) can log in and watch videos.
- Single-file app; auto-initializes DB and a default admin.

Setup
1) pip install streamlit pyjwt
2) streamlit run app.py

Default admin
- username: admin
- password: Admin@123  (change after first login)

Security notes
- Passwords hashed with PBKDF2-HMAC (stdlib, no extra deps)
- JWT secret persisted in secret.key (auto-generated first run)
"""

import os
import sqlite3
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Tuple

import streamlit as st
import jwt  # PyJWT

# -----------------------------
# Config
# -----------------------------
DB_PATH = "platform.db"
SECRET_PATH = "secret.key"
TOKEN_EXP_MINUTES = 60 * 24  # 24h
JWT_ALG = "HS256"
PASSWORD_HASH_ITERATIONS = 200_000

st.set_page_config(page_title="IDEAverse – Mini Platform", page_icon="🎥", layout="wide")

# -----------------------------
# Helpers – Security
# -----------------------------

def load_or_create_secret(path: str = SECRET_PATH) -> bytes:
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    secret = os.urandom(32)
    with open(path, "wb") as f:
        f.write(secret)
    return secret

SECRET = load_or_create_secret()


def pbkdf2_hash(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
    """Return (salt_b64, hash_b64)."""
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_HASH_ITERATIONS)
    return base64.b64encode(salt).decode(), base64.b64encode(dk).decode()


def verify_password(password: str, salt_b64: str, hash_b64: str) -> bool:
    salt = base64.b64decode(salt_b64.encode())
    dk_check = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_HASH_ITERATIONS)
    return hmac.compare_digest(base64.b64encode(dk_check).decode(), hash_b64)


def create_token(username: str, role: str) -> str:
    exp = datetime.utcnow() + timedelta(minutes=TOKEN_EXP_MINUTES)
    payload = {"sub": username, "role": role, "exp": exp}
    return jwt.encode(payload, SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET, algorithms=[JWT_ALG])
    except jwt.ExpiredSignatureError:
        st.warning("Tu sesión expiró. Inicia sesión nuevamente.")
    except jwt.InvalidTokenError:
        st.error("Token inválido.")
    return None

# -----------------------------
# DB
# -----------------------------

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','user')),
            created_at TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        );
        """
    )

    # Ensure default admin exists
    cur.execute("SELECT id FROM users WHERE username=?", ("admin",))
    if cur.fetchone() is None:
        salt, ph = pbkdf2_hash("Admin@123")
        cur.execute(
            "INSERT INTO users (username, salt, password_hash, role, created_at) VALUES (?,?,?,?,?)",
            ("admin", salt, ph, "admin", datetime.utcnow().isoformat()),
        )
        conn.commit()
    conn.close()


init_db()

# -----------------------------
# Auth State
# -----------------------------
if "token" not in st.session_state:
    st.session_state.token = None


def get_current_user() -> Optional[dict]:
    token = st.session_state.token
    if not token:
        return None
    payload = decode_token(token)
    return payload


# -----------------------------
# UI – Components
# -----------------------------

def login_box():
    st.header("Iniciar sesión")
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Entrar")
        if submitted:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT username, salt, password_hash, role FROM users WHERE username=?", (username,))
            row = cur.fetchone()
            conn.close()
            if row and verify_password(password, row[1], row[2]):
                token = create_token(row[0], row[3])
                st.session_state.token = token
                st.success("¡Login exitoso!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")


def logout_button():
    if st.button("Cerrar sesión"):
        st.session_state.token = None
        st.rerun()


# Admin Pages

def admin_users_page():
    st.subheader("👤 Gestión de usuarios")
    tab1, tab2 = st.tabs(["Crear usuario", "Listado / eliminar"]) 

    with tab1:
        with st.form("create_user_form"):
            username = st.text_input("Usuario nuevo")
            pwd = st.text_input("Contraseña", type="password")
            role = st.selectbox("Rol", ["user", "admin"], index=0)
            submitted = st.form_submit_button("Crear usuario")
        if submitted:
            if not username or not pwd:
                st.warning("Usuario y contraseña son obligatorios")
            else:
                try:
                    salt, ph = pbkdf2_hash(pwd)
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO users (username, salt, password_hash, role, created_at) VALUES (?,?,?,?,?)",
                        (username, salt, ph, role, datetime.utcnow().isoformat()),
                    )
                    conn.commit()
                    conn.close()
                    st.success(f"Usuario '{username}' creado")
                except sqlite3.IntegrityError:
                    st.error("Ese nombre de usuario ya existe")

    with tab2:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, username, role, created_at FROM users ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        st.dataframe(
            [{"id": r[0], "username": r[1], "role": r[2], "created_at": r[3]} for r in rows],
            use_container_width=True,
        )
        user_id_to_delete = st.number_input("ID a eliminar (no podrás borrar tu propio usuario en uso)", min_value=0, step=1)
        if st.button("Eliminar usuario"):
            current = get_current_user()
            if current:
                # Prevent deleting yourself
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("SELECT username FROM users WHERE id=?", (user_id_to_delete,))
                row = cur.fetchone()
                if row and row[0] == current.get("sub"):
                    st.warning("No puedes eliminar tu propio usuario mientras estás logueado.")
                else:
                    cur.execute("DELETE FROM users WHERE id=?", (user_id_to_delete,))
                    conn.commit()
                    st.success("Usuario eliminado (si existía)")
                conn.close()


def admin_videos_page():
    st.subheader("🎬 Gestión de videos (YouTube)")
    tab1, tab2 = st.tabs(["Agregar video", "Listado / eliminar"]) 

    with tab1:
        with st.form("add_video_form"):
            title = st.text_input("Título")
            url = st.text_input("URL de YouTube (https://...)")
            desc = st.text_area("Descripción (opcional)")
            submitted = st.form_submit_button("Guardar")
        if submitted:
            if not title or not url:
                st.warning("Título y URL son obligatorios")
            else:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO videos (title, url, description, created_at) VALUES (?,?,?,?)",
                    (title, url, desc, datetime.utcnow().isoformat()),
                )
                conn.commit()
                conn.close()
                st.success("Video agregado")

    with tab2:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, title, url, description, created_at FROM videos ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()

        for (vid, title, url, desc, created_at) in rows:
            with st.expander(f"#{vid} · {title}"):
                st.write(desc or "Sin descripción")
                st.write(f"Agregado: {created_at}")
                # Preview embed
                st.video(url)
                if st.button("Eliminar", key=f"del_{vid}"):
                    conn = get_conn()
                    cur = conn.cursor()
                    cur.execute("DELETE FROM videos WHERE id=?", (vid,))
                    conn.commit()
                    conn.close()
                    st.success("Eliminado")
                    st.rerun()


# User page

def user_videos_page():
    st.subheader("🎥 Biblioteca de videos")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, url, description, created_at FROM videos ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        st.info("Aún no hay videos. Vuelve más tarde.")
        return

    # Filters
    q = st.text_input("Buscar por título o descripción")

    def matches(row):
        if not q:
            return True
        target = (row[1] + " " + (row[3] or "")).lower()
        return q.lower() in target

    filtered = [r for r in rows if matches(r)]
    for (vid, title, url, desc, created_at) in filtered:
        with st.container(border=True):
            st.markdown(f"**{title}** · _{created_at}_")
            if desc:
                st.caption(desc)
            st.video(url)


# -----------------------------
# Main Layout
# -----------------------------

def main():
    user = get_current_user()

    with st.sidebar:
        st.markdown("### IDEAverse 🎥")
        if user:
            st.markdown(f"**Usuario:** {user.get('sub')}  ")
            st.markdown(f"**Rol:** {user.get('role')}")
            st.divider()
            if user.get("role") == "admin":
                page = st.radio("Navegación", ["Inicio", "Usuarios", "Videos"]) 
            else:
                page = st.radio("Navegación", ["Inicio", "Videos"]) 
            st.divider()
            logout_button()
        else:
            st.info("Inicia sesión para continuar")

    if not user:
        login_box()
        return

    # Authorized area
    st.title("IDEAverse – Mini Platform")

    # Route handling based on sidebar selection
    if user.get("role") == "admin":
        # Read radio selection from sidebar safely
        # Fallback to 'Inicio' if not set
        sel = st.session_state.get("_radio", None)
        # But streamlit stores radio internally; use local variable `page` from sidebar via state hacks is flaky.
        # Instead, recompute here by mirroring the sidebar logic minimally:
        # For simplicity, derive from query params if present
        qp = st.query_params
        page_param = qp.get("page", ["Inicio"]) if isinstance(qp.get("page"), list) else qp.get("page", "Inicio")
        # We'll just display all admin pages in tabs on main to avoid mismatch
        tab_inicio, tab_users, tab_videos = st.tabs(["Inicio", "Usuarios", "Videos"])
        with tab_inicio:
            st.success("Bienvenido, admin. Usa las pestañas para gestionar usuarios y videos.")
        with tab_users:
            admin_users_page()
        with tab_videos:
            admin_videos_page()
    else:
        tab_inicio, tab_videos = st.tabs(["Inicio", "Videos"])
        with tab_inicio:
            st.success("Bienvenido. Explora los videos disponibles.")
        with tab_videos:
            user_videos_page()


if __name__ == "__main__":
    main()
