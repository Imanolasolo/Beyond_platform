import streamlit as st
from modules.beyond_videos.video_manager import fetch_all_videos
from modules.beyond_podcasts.podcast_manager import fetch_all_podcasts
from db.likes import like_video, unlike_video, get_video_likes, user_liked_video
import jwt
import os

def show_user_dashboard():
    st.header("👤 Panel de Usuario")

    # Botón de cerrar sesión
    if st.button("Cerrar sesión", key="logout_user_btn"):
        st.session_state["token"] = None
        st.rerun()

    acciones = ["Videoteca", "Podcast", "Beyond Summit"]
    accion = st.selectbox("¿Qué deseas explorar?", acciones)

    if accion == "Videoteca":
        st.subheader("🎬 Videoteca")
        st.info("Aquí se mostrarán los videos disponibles para el usuario.")
        videos = fetch_all_videos()
        if not videos:
            st.write("No hay videos disponibles.")
        else:
            # Mostrar videos en filas de 3
            for i in range(0, len(videos), 3):
                row_videos = videos[i:i+3]
                cols = st.columns(3)
                # Obtener user_id del token si existe
                user_id = None
                if "token" in st.session_state and st.session_state["token"]:
                    try:
                        payload = jwt.decode(st.session_state["token"], "super_secret_key", algorithms=["HS256"])
                        user_id = payload.get("user_id")
                    except Exception:
                        user_id = None
                for idx, vid in enumerate(row_videos):
                    vid_id, title, url, desc = vid
                    with cols[idx]:
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
                                if st.button(f"❤️ Quitar me gusta ({likes})", key=f"unlike_video_user_{vid_id}"):
                                    unlike_video(user_id, vid_id)
                                    st.rerun()
                            else:
                                if st.button(f"🤍 Me gusta ({likes})", key=f"like_video_user_{vid_id}"):
                                    like_video(user_id, vid_id)
                                    st.rerun()
                        else:
                            likes = get_video_likes(vid_id)
                            st.write(f"👍 {likes} me gusta")
                st.markdown("---")
    elif accion == "Podcast":
        st.subheader("🎧 Podcast")
        st.info("Aquí se mostrarán los podcasts disponibles para el usuario.")
        podcasts = fetch_all_podcasts()
        if not podcasts:
            st.write("No hay podcasts disponibles.")
        else:
            cols = st.columns(3)
            for idx, pod in enumerate(podcasts):
                pid, title, url, desc = pod
                with cols[idx % 3]:
                    st.markdown(f"**{title}**")
                    if url.startswith("http"):
                        st.video(url, format="video/mp4", start_time=0)
                    if desc:
                        st.caption(desc)
    elif accion == "Beyond Summit":
        st.subheader("🏔️ Beyond Summit")
        st.info("Aquí se mostrarán los eventos Beyond Summit.")
        # Aquí puedes agregar la lógica para mostrar los summits al usuario
