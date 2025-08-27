import streamlit as st
from modules.cruds.crud_users import show_users_crud
from modules.cruds.crud_roles import show_roles_crud
from modules.beyond_videos.video_manager import admin_videos_crud  # Importar desde video_manager
from modules.beyond_podcasts.podcast_manager import admin_podcasts_crud  # Importar desde podcast_manager

def show_admin_dashboard():
    st.header("📊 Panel de Administración")
    
    # Mejor manejo de logout usando solo session_state
    if st.button("Cerrar sesión", key="logout_btn"):
        st.session_state["token"] = None
        st.rerun()

    menu = ["Usuarios", "Roles", "Videos", "Podcasts"]
    choice = st.selectbox("Selecciona una sección para administrar:", menu)

    if choice == "Usuarios":
        show_users_crud()
    elif choice == "Roles":
        show_roles_crud()
    elif choice == "Videos":
        admin_videos_crud()  # Llamar a la función importada
    elif choice == "Podcasts":
        admin_podcasts_crud()  # Llamar a la función importada

