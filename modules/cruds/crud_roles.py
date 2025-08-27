import streamlit as st
from db.connection import fetch_all, fetch_one, execute_query

def show_roles_crud():
    st.subheader("🔑 Gestión de Roles")

    action = st.radio(
        "Selecciona una acción",
        ["Ver roles", "Crear rol", "Modificar rol", "Eliminar rol"],
        horizontal=True
    )

    if action == "Ver roles":
        roles = fetch_all("SELECT id, name FROM roles")
        st.table(roles)

    elif action == "Crear rol":
        with st.form("create_role_form"):
            new_role = st.text_input("Nombre del nuevo rol")
            submitted = st.form_submit_button("Crear rol")
            if submitted:
                if new_role:
                    try:
                        execute_query(
                            "INSERT INTO roles (name) VALUES (?)",
                            (new_role,)
                        )
                        st.success(f"Rol '{new_role}' creado correctamente.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error al crear rol: {e}")
                else:
                    st.warning("El nombre del rol no puede estar vacío.")

    elif action == "Modificar rol":
        roles = fetch_all("SELECT id, name FROM roles")
        role_ids = [r["id"] for r in roles] if roles else []
        if role_ids:
            selected_id = st.selectbox("Selecciona rol por ID", role_ids)
            role_data = fetch_one("SELECT name FROM roles WHERE id = ?", (selected_id,))
            if role_data:
                with st.form("edit_role_form"):
                    edit_name = st.text_input("Nuevo nombre de rol", value=role_data["name"])
                    edit_submitted = st.form_submit_button("Actualizar rol")
                    if edit_submitted:
                        try:
                            execute_query(
                                "UPDATE roles SET name=? WHERE id=?",
                                (edit_name, selected_id)
                            )
                            st.success("Rol actualizado correctamente.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error al actualizar rol: {e}")
        else:
            st.info("No hay roles para modificar.")

    elif action == "Eliminar rol":
        roles = fetch_all("SELECT id, name FROM roles")
        role_ids = [r["id"] for r in roles] if roles else []
        if role_ids:
            del_id = st.selectbox("Selecciona rol a eliminar por ID", role_ids, key="delete_role")
            if st.button("Eliminar rol"):
                try:
                    execute_query("DELETE FROM roles WHERE id=?", (del_id,))
                    st.success("Rol eliminado correctamente.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error al eliminar rol: {e}")
        else:
            st.info("No hay roles para eliminar.")
