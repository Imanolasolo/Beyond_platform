import streamlit as st
import sqlite3

DB_PATH = "beyond.db"

def save_podcast(title, url, description=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO podcasts (title, url, description) VALUES (?, ?, ?)",
        (title, url, description)
    )
    conn.commit()
    conn.close()

def update_podcast(pid, new_title, new_desc):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE podcasts SET title = ?, description = ? WHERE id = ?",
        (new_title, new_desc, pid)
    )
    conn.commit()
    conn.close()

def fetch_all_podcasts():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, url, description FROM podcasts")
    podcasts = cursor.fetchall()
    conn.close()
    return podcasts

def admin_podcasts_crud():
    st.subheader("🎧 Gestión de Videopodcasts")
    acciones = ["Cargar/Crear videopodcast", "Modificar datos videopodcast", "Borrar videopodcast", "Ver videopodcasts guardados"]
    accion = st.selectbox("Selecciona una acción:", acciones)

    if accion == "Cargar/Crear videopodcast":
        st.info("Formulario para cargar o crear un nuevo videopodcast.")
        title = st.text_input("Título del videopodcast")
        description = st.text_area("Descripción (opcional)")
        youtube_url = st.text_input("Pega la URL de YouTube aquí")
        if st.button("Guardar videopodcast desde YouTube"):
            if title and youtube_url:
                save_podcast(title, youtube_url, description)
                st.success("Videopodcast de YouTube guardado.")
            else:
                st.warning("Debes ingresar un título y una URL de YouTube.")
    elif accion == "Modificar datos videopodcast":
        st.info("Selecciona un videopodcast para modificar sus datos.")
        podcasts = fetch_all_podcasts()
        if not podcasts:
            st.write("No hay videopodcasts guardados.")
        else:
            podcast_titles = [p[1] for p in podcasts]
            selected_podcast_title = st.selectbox("Selecciona un videopodcast:", podcast_titles)
            podcast_data = next((p for p in podcasts if p[1] == selected_podcast_title), None)
            if podcast_data:
                pid, title, url, desc = podcast_data
                new_title = st.text_input("Nuevo título", value=title)
                new_desc = st.text_area("Nueva descripción", value=desc)
                if st.button("Actualizar videopodcast"):
                    update_podcast(pid, new_title, new_desc)
                    st.success("Datos del videopodcast actualizados.")
    elif accion == "Borrar videopodcast":
        st.info("Selecciona un videopodcast para eliminarlo.")
        podcasts = fetch_all_podcasts()
        if not podcasts:
            st.write("No hay videopodcasts guardados.")
        else:
            podcast_titles = [p[1] for p in podcasts]
            selected_podcast_title = st.selectbox("Selecciona un videopodcast:", podcast_titles)
            podcast_data = next((p for p in podcasts if p[1] == selected_podcast_title), None)
            if podcast_data:
                pid, title, url, desc = podcast_data
                if st.button("Eliminar videopodcast"):
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM podcasts WHERE id = ?", (pid,))
                    conn.commit()
                    conn.close()
                    st.success("Videopodcast eliminado.")
    elif accion == "Ver videopodcasts guardados":
        st.info("Lista de videopodcasts guardados:")
        podcasts = fetch_all_podcasts()
        if not podcasts:
            st.write("No hay videopodcasts guardados.")
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
