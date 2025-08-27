# app.py
import streamlit as st
import jwt
import datetime
from db import db_setup
from db.connection import fetch_one, fetch_all, execute_query

# Clave secreta para JWT
SECRET_KEY = "super_secret_key"

# ===============================
# Inicializar Base de Datos
# ===============================
db_setup.init_db()

# ===============================
# Funciones de autenticación
# ===============================
def create_jwt(user_id, role):
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_jwt(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        st.error("⚠️ Tu sesión ha expirado.")
        return None
    except jwt.InvalidTokenError:
        st.error("⚠️ Token inválido.")
        return None


def login_user(username, password):
    # Hardcodeo para admin/admin123
    if username == "admin" and password == "admin123":
        return {"id": 1, "username": "admin", "role": "admin"}
    query = "SELECT * FROM users WHERE username = ?"
    user = fetch_one(query, (username,))
    if user:
        # Importar aquí para evitar dependencias circulares
        import jwt
        SECRET_KEY = "super_secret_key"
        try:
            decoded = jwt.decode(user["password"], SECRET_KEY, algorithms=["HS256"])
            if decoded.get("pwd") == password:
                return user
        except Exception:
            return None
    return None


# ===============================
# Interfaz Streamlit
# ===============================
st.set_page_config(page_title="Beyond - Dashboard", layout="wide" \
"")
col1, col2 = st.columns([1,8])
with col1:
    st.image("assets/images/logo_beyond.png",width=100,)
with col2:
    st.title("Beyond Platform")
    st.subheader("Tu espacio para crecer, conectar e ir más allá.")
# Guardar sesión en st.session_state
if "token" not in st.session_state:
    st.session_state["token"] = None

if st.session_state["token"] is None:
    # --- Login Form ---

    col1,col2,col3=st.columns([1,1,1])
    with col1:
        st.image("assets/images/pic1.png",width=385)
        with st.expander("¿Qué es Beyond Platform?"):
            st.write("Beyond Platform es tu espacio para aprender, conectar y transformar. No es solo una plataforma, es un ecosistema diseñado para docentes, administradores y estudiantes que buscan ir más allá de lo tradicional. Aquí encuentras contenidos exclusivos, herramientas tecnológicas y experiencias interactivas —como dashboards, podcasts, videos y eventos— que impulsan la innovación educativa y hacen más fácil tu día a día. Con Beyond Platform, la educación deja de ser estática y se convierte en un viaje de crecimiento continuo, adaptado a tus necesidades y con una comunidad que te acompaña en cada paso.")
            
    with col2:
        st.image("assets/images/login_image.png",width=385)
        with st.expander("Inicia sesión"):
            st.subheader("🔐 Iniciar Sesión")
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")

            if st.button("Ingresar"):
                user = login_user(username, password)
                if user:
                    token = create_jwt(user["id"], user["role"])
                    st.session_state["token"] = token
                    st.success(f"Bienvenido {user['username']} 👋")
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
    with col3:
        st.image("assets/images/mad_man.jpg",width=385)
        with st.expander("¿No tienes cuenta?"):
            st.write("Contacta al administrador para crear una cuenta.")

else:
    # --- Dashboard ---
    payload = decode_jwt(st.session_state["token"])
    if payload:
        st.success(f"✅ Sesión activa | Usuario ID: {payload['user_id']} | Rol: {payload['role']}")
        
        if payload["role"] == "admin":
            from modules.dashboards.admin_dashboard import show_admin_dashboard
            show_admin_dashboard()
        elif payload["role"] == "user free":
            from modules.dashboards.user_dashboard import show_user_dashboard
            show_user_dashboard()
        else:
            menu = ["Dashboard", "Usuarios", "Videos", "Salir"]
            choice = st.sidebar.selectbox("Menú", menu)

            if choice == "Dashboard":
                st.write("📊 Bienvenido al panel principal.")
            elif choice == "Usuarios":
                st.write("👤 Gestión de usuarios (CRUD pronto aquí).")
            elif choice == "Videos":
                st.write("🎬 Gestión de videos (CRUD pronto aquí).")
            elif choice == "Salir":
                st.session_state["token"] = None
                st.rerun()
