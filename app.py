import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN DE LA PÁGINA (El "Cartel de Obra") ---
st.set_page_config(page_title="Petsgram", page_icon="🐾")

st.title("🐾 Petsgram")
st.write("La red social donde los humanos no importan.")

# --- 2. LOS CIMIENTOS (Base de datos temporal) ---
# En una obra real, esto sería de hormigón (SQL). 
# Aquí, usaremos la "memoria" de la sesión como una estructura temporal.
# Si no existe la lista de posts, la creamos vacía.
if 'posts' not in st.session_state:
    st.session_state['posts'] = []

# --- 3. CIRCULACIÓN (Sidebar / Menú) ---
# Diseñamos la navegación en la barra lateral
menu = st.sidebar.radio("Menú", ["El Parque 🌳 (Feed)", "Nuevo Post 📸"])

# --- 4. ESPACIO 1: NUEVO POST (Área de Carga) ---
if menu == "Nuevo Post 📸":
    st.header("Sube una foto de tu mascota")
    
    # El Formulario: Inputs del usuario
    with st.form("post_form"):
        nombre = st.text_input("Nombre de la mascota (ej: Firulais)")
        mensaje = st.text_area("¿Qué está haciendo? (ej: Persiguiendo su cola)")
        # Por ahora, simulamos la foto con un selector de "emoción" para no complicar con archivos reales hoy
        emocion = st.selectbox("Estado de ánimo", ["🐶 Feliz", "🐱 Gruñón", "😴 Dormilón", "🤪 Loco"])
        
        # El botón de "Confirmar construcción"
        submitted = st.form_submit_button("¡Publicar!")
        
        if submitted:
            # Creamos el "bloque" de datos del post
            nuevo_post = {
                "nombre": nombre,
                "mensaje": mensaje,
                "emocion": emocion,
                "fecha": datetime.now().strftime("%H:%M")
            }
            
            # Lo agregamos a nuestros cimientos (la lista de posts)
            st.session_state['posts'].append(nuevo_post)
            
            st.success("¡Publicado con éxito!")
            st.balloons() # ¡El toque de celebración!

# --- 5. ESPACIO 2: EL PARQUE (El Feed) ---
elif menu == "El Parque 🌳 (Feed)":
    st.header("Últimas novedades del parque")
    
    # Verificamos si hay algo construido
    if len(st.session_state['posts']) == 0:
        st.info("El parque está vacío... ¡Sé el primero en publicar!")
    else:
        # Recorremos la lista de posts (del último al primero para ver lo nuevo arriba)
        for post in reversed(st.session_state['posts']):
            # Usamos un "expander" o contenedor para cada post
            with st.container(border=True):
                # Estructura del Post: Título grande y texto abajo
                st.subheader(f"{post['emocion']} - {post['nombre']}")
                st.write(post['mensaje'])
                st.caption(f"Publicado a las {post['fecha']}")
