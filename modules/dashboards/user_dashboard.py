import streamlit as st
from modules.beyond_videos.video_manager import fetch_all_videos
from modules.beyond_podcasts.podcast_manager import fetch_all_podcasts
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
            cols = st.columns(3)
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
