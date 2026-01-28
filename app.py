import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
st.set_page_config(page_title="Petsgram", page_icon="🐾", layout="centered")

# Estilos CSS para que se vea limpio (como app móvil)
st.markdown("""
    <style>
    .stApp { max-width: 600px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🐾 Petsgram")

# --- 2. GESTIÓN DE ESTADO (MEMORIA) ---
if 'posts' not in st.session_state:
    st.session_state['posts'] = []

# --- 3. MENÚ LATERAL ---
menu = st.sidebar.radio("Navegación", ["El Parque 🌳 (Feed)", "Nuevo Post 📸"])

# --- 4. SECCIÓN: SUBIR FOTO ---
if menu == "Nuevo Post 📸":
    st.header("Crear Publicación")
    
    with st.form("post_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre")
        with col2:
            # ¡Aquí vuelve tu idea de los emojis! Define el "Mood" de la foto
            emocion = st.selectbox("¿Cómo se siente?", 
                                 ["🐶 Feliz", "🤪 Loco", "😴 Dormilón", "😎 Cool", "🥺 Tierno"])
        
        mensaje = st.text_area("Pie de foto")
        foto = st.file_uploader("Sube la foto", type=['jpg', 'png', 'jpeg'])
        
        submitted = st.form_submit_button("¡Publicar en el parque!")
        
        if submitted and foto:
            nuevo_post = {
                "nombre": nombre,
                "emocion": emocion,
                "mensaje": mensaje,
                "foto": foto,
                "fecha": datetime.now().strftime("%H:%M"),
                "likes": 0 # Inicializamos el contador de huellitas
            }
            st.session_state['posts'].append(nuevo_post)
            st.success("¡Guau! Publicado.")
            st.balloons()

# --- 5. SECCIÓN: EL FEED ---
elif menu == "El Parque 🌳 (Feed)":
    st.header("Comunidad")
    
    if not st.session_state['posts']:
        st.info("El parque está vacío. ¡Sube la primera foto!")
    else:
        # Loop para mostrar cada post
        # Usamos 'enumerate' para tener un ID único para cada botón de huellita
        for i, post in enumerate(reversed(st.session_state['posts'])):
            
            with st.container(border=True):
                # CABECERA: El Emoji + El Nombre (Tu idea de identidad)
                st.subheader(f"{post['emocion']}  |  {post['nombre']}")
                st.caption(f"Subido a las {post['fecha']}")
                
                # FOTO
                st.image(post['foto'], use_container_width=True)
                
                # PIE DE FOTO
                st.write(f"**{post['nombre']} dice:** {post['mensaje']}")
                
                # INTERACCIÓN: LA HUELLITA
                # Creamos columnas para que el botón no sea gigante
                col_a, col_b = st.columns([0.3, 0.7])
                
                with col_a:
                    # El botón necesita una "key" única para saber a qué foto pertenece
                    if st.button(f"🐾 Dar Huellita", key=f"like_{i}"):
                        st.write("¡Diste amor! ❤️")
                        # Nota: En esta versión simple sin base de datos, 
                        # el like es visual para el usuario en el momento.
