import streamlit as st
import sqlite3
import os
from db.likes import like_video, unlike_video, get_video_likes, user_liked_video
import jwt

DB_PATH = "beyond.db"

def save_video(title, url, description=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO videos (title, url, description) VALUES (?, ?, ?)",
        (title, url, description)
    )
    conn.commit()
    conn.close()

def update_video(vid_id, new_title, new_desc):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE videos SET title = ?, description = ? WHERE id = ?",
        (new_title, new_desc, vid_id)
    )
    conn.commit()
    conn.close()

def fetch_all_videos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, url, description FROM videos")
    videos = cursor.fetchall()
    conn.close()
    return videos

def admin_videos_crud():
    st.subheader("🎬 Gestión de Videos")
    acciones = ["Cargar/Crear video", "Modificar datos video", "Borrar video", "Ver videos guardados"]
    accion = st.selectbox("Selecciona una acción:", acciones)

    if accion == "Cargar/Crear video":
        st.info("Formulario para cargar o crear un nuevo video.")
        title = st.text_input("Título del video")
        description = st.text_area("Descripción (opcional)")
        youtube_url = st.text_input("Pega la URL de YouTube aquí")
        if st.button("Guardar video desde YouTube"):
            if title and youtube_url:
                save_video(title, youtube_url, description)
                st.success("Video de YouTube guardado.")
            else:
                st.warning("Debes ingresar un título y una URL de YouTube.")
    elif accion == "Modificar datos video":
        st.info("Selecciona un video para modificar sus datos.")
        videos = fetch_all_videos()
        if not videos:
            st.write("No hay videos guardados.")
        else:
            video_titles = [v[1] for v in videos]
            selected_video_title = st.selectbox("Selecciona un video:", video_titles)
            video_data = next((v for v in videos if v[1] == selected_video_title), None)
            if video_data:
                vid_id, title, url, desc = video_data
                new_title = st.text_input("Nuevo título", value=title)
                new_desc = st.text_area("Nueva descripción", value=desc)
                if st.button("Actualizar video"):
                    update_video(vid_id, new_title, new_desc)
                    st.success("Datos del video actualizados.")
    elif accion == "Borrar video":
        st.info("Selecciona un video para eliminarlo.")
        videos = fetch_all_videos()
        if not videos:
            st.write("No hay videos guardados.")
        else:
            video_titles = [v[1] for v in videos]
            selected_video_title = st.selectbox("Selecciona un video:", video_titles)
            video_data = next((v for v in videos if v[1] == selected_video_title), None)
            if video_data:
                vid_id, title, url, desc = video_data
                if st.button("Eliminar video"):
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM videos WHERE id = ?", (vid_id,))
                    conn.commit()
                    conn.close()
                    st.success("Video eliminado.")
    elif accion == "Ver videos guardados":
        st.info("Lista de videos guardados:")
        videos = fetch_all_videos()
        if not videos:
            st.write("No hay videos guardados.")
        else:
            cols = st.columns(3)
            # Obtener user_id del token si existe
            user_id = None
            if "token" in st.session_state and st.session_state["token"]:
                try:
                    payload = jwt.decode(st.session_state["token"], "super_secret_key", algorithms=["HS256"])
                    user_id = payload.get("user_id")
                except Exception:
                    user_id = None
            for idx, vid in enumerate(videos):
                vid_id, title, url, desc = vid
                with cols[idx % 3]:
                    st.markdown(f"**{title}**")
                    if url.startswith("http"):
                        st.video(url, format="video/mp4", start_time=0)
                    else:
                        try:
                            if os.path.exists(url):
                                with open(url, "rb") as f:
                                    st.video(f)
                            else:
                                st.write("No se pudo cargar el video local.")
                        except Exception:
                            st.write("No se pudo cargar el video local.")
                    if desc:
                        st.caption(desc)
                    # Mostrar likes y botón si hay usuario logueado
                    if user_id:
                        likes = get_video_likes(vid_id)
                        liked = user_liked_video(user_id, vid_id)
                        if liked:
                            if st.button(f"❤️ Quitar me gusta ({likes})", key=f"unlike_video_{vid_id}"):
                                unlike_video(user_id, vid_id)
                                st.experimental_rerun()
                        else:
                            if st.button(f"🤍 Me gusta ({likes})", key=f"like_video_{vid_id}"):
                                like_video(user_id, vid_id)
                                st.experimental_rerun()
                    else:
                        likes = get_video_likes(vid_id)
                        st.write(f"👍 {likes} me gusta")
