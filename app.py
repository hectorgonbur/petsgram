import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
st.set_page_config(page_title="Petsgram", page_icon="🐾", layout="centered")

# Estilos CSS
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
            emocion = st.selectbox("¿Cómo se siente?", 
                                 ["🐶 Feliz", "🤪 Loco", "😴 Dormilón", "😎 Cool", "🥺 Tierno"])
        
        # CAMBIO 1: Ahora dice "Descripción"
        mensaje = st.text_area("Descripción")
        foto = st.file_uploader("Sube la foto", type=['jpg', 'png', 'jpeg'])
        
        submitted = st.form_submit_button("¡Publicar en el parque!")
        
        if submitted and foto:
            nuevo_post = {
                "nombre": nombre,
                "emocion": emocion,
                "mensaje": mensaje,
                "foto": foto,
                "fecha": datetime.now().strftime("%H:%M"),
                "likes": 0,
                "comentarios": [] # Lista vacía para guardar futuros comentarios
            }
            st.session_state['posts'].append(nuevo_post)
            st.success("¡Guau! Publicado.")
            st.balloons()

# --- 5. SECCIÓN: EL FEED ---
elif menu == "El Parque 🌳 (Feed)":
    
    # SUGERENCIA EXTRA: Filtro por emoción
    st.header("Comunidad")
    filtro = st.multiselect("Filtrar por estado de ánimo:", 
                            ["🐶 Feliz", "🤪 Loco", "😴 Dormilón", "😎 Cool", "🥺 Tierno"])
    
    if not st.session_state['posts']:
        st.info("El parque está vacío. ¡Sube la primera foto!")
    else:
        # Lógica del filtro: Si hay filtro seleccionado, mostramos solo esos. Si no, todos.
        posts_a_mostrar = [p for p in st.session_state['posts'] if not filtro or p['emocion'] in filtro]
        
        # Loop para mostrar posts
        for i, post in enumerate(reversed(posts_a_mostrar)):
            
            with st.container(border=True):
                # CABECERA
                c1, c2 = st.columns([0.7, 0.3])
                c1.subheader(f"{post['emocion']} | {post['nombre']}")
                c2.caption(f"{post['fecha']}")
                
                # FOTO
                st.image(post['foto'], use_container_width=True)
                
                # DESCRIPCIÓN
                st.write(f"**{post['nombre']} dice:** {post['mensaje']}")
                
                st.markdown("---") # Línea divisoria
                
                # --- BARRA DE ACCIONES (Like, Comentar, Compartir) ---
                col_like, col_comment, col_share = st.columns(3)
                
                with col_like:
                    # Botón de Huellita con contador
                    if st.button(f"🐾 {post['likes']}", key=f"like_{i}"):
                        post['likes'] += 1
                        st.rerun() # Recargamos para ver el número subir
                
                with col_comment:
                    # Botón fake que solo indica acción visual por ahora
                    st.button("💬 Comentar", key=f"btn_comment_{i}")
                
                with col_share:
                    if st.button("🔗 Compartir", key=f"share_{i}"):
                        st.toast("¡Enlace copiado al portapapeles!", icon="📋")

                # --- SECCIÓN DE COMENTARIOS ---
                # Un pequeño formulario dentro de la tarjeta para agregar comentarios
                with st.expander(f"Ver comentarios ({len(post['comentarios'])})"):
                    for c in post['comentarios']:
                        st.text(f"👤 {c}")
                    
                    # Input para nuevo comentario
                    nuevo_comentario = st.text_input("Escribe algo...", key=f"input_comment_{i}")
                    if st.button("Enviar", key=f"send_comment_{i}"):
                        if nuevo_comentario:
                            post['comentarios'].append(nuevo_comentario)
                            st.rerun()
