import streamlit as st
from db.connection import fetch_all, fetch_one, execute_query
import jwt

SECRET_KEY = "super_secret_key"

def encrypt_password(password):
    return jwt.encode({"pwd": password}, SECRET_KEY, algorithm="HS256")

def verify_password(stored_password, provided_password):
    try:
        decoded = jwt.decode(stored_password, SECRET_KEY, algorithms=["HS256"])
        return decoded.get("pwd") == provided_password
    except Exception:
        return False

def get_roles():
    roles = fetch_all("SELECT name FROM roles")
    return [r["name"] for r in roles] if roles else ["admin", "user free", "user premium", "coach"]

def show_users_crud():
    st.subheader("👤 Gestión de Usuarios")

    action = st.radio(
        "Selecciona una acción",
        ["Ver usuarios", "Crear usuario", "Modificar usuario", "Eliminar usuario"],
        horizontal=True
    )

    if action == "Ver usuarios":
        users = fetch_all("SELECT id, username, role FROM users")
        st.table(users)

    elif action == "Crear usuario":
        roles = get_roles()
        with st.form("create_user_form"):
            new_username = st.text_input("Usuario")
            new_password = st.text_input("Contraseña", type="password")
            new_role = st.selectbox("Rol", roles)
            submitted = st.form_submit_button("Crear usuario")
            if submitted:
                if new_username and new_password:
                    try:
                        encrypted_pwd = encrypt_password(new_password)
                        execute_query(
                            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                            (new_username, encrypted_pwd, new_role)
                        )
                        st.success(f"Usuario '{new_username}' creado correctamente.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al crear usuario: {e}")
                else:
                    st.warning("Completa todos los campos.")

    elif action == "Modificar usuario":
        users = fetch_all("SELECT id, username, role FROM users")
        user_ids = [u["id"] for u in users] if users else []
        if user_ids:
            selected_id = st.selectbox("Selecciona usuario por ID", user_ids)
            user_data = fetch_one("SELECT username, role FROM users WHERE id = ?", (selected_id,))
            roles = get_roles()
            if user_data:
                with st.form("edit_user_form"):
                    edit_username = st.text_input("Nuevo usuario", value=user_data["username"])
                    edit_role = st.selectbox("Nuevo rol", roles, index=roles.index(user_data["role"]) if user_data["role"] in roles else 0)
                    edit_password = st.text_input("Nueva contraseña (opcional)", type="password")
                    edit_submitted = st.form_submit_button("Actualizar usuario")
                    if edit_submitted:
                        try:
                            if edit_password:
                                encrypted_pwd = encrypt_password(edit_password)
                                execute_query(
                                    "UPDATE users SET username=?, password=?, role=? WHERE id=?",
                                    (edit_username, encrypted_pwd, edit_role, selected_id)
                                )
                            else:
                                execute_query(
                                    "UPDATE users SET username=?, role=? WHERE id=?",
                                    (edit_username, edit_role, selected_id)
                                )
                            st.success("Usuario actualizado correctamente.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al actualizar usuario: {e}")
        else:
            st.info("No hay usuarios para modificar.")

    elif action == "Eliminar usuario":
        users = fetch_all("SELECT id, username FROM users")
        user_ids = [u["id"] for u in users] if users else []
        if user_ids:
            del_id = st.selectbox("Selecciona usuario a eliminar por ID", user_ids, key="delete_user")
            if st.button("Eliminar usuario"):
                try:
                    execute_query("DELETE FROM users WHERE id=?", (del_id,))
                    st.success("Usuario eliminado correctamente.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar usuario: {e}")
        else:
            st.info("No hay usuarios para eliminar.")
