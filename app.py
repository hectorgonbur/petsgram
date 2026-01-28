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

# --- 3. MENÚ LATERAL (Ahora con 3 opciones) ---
menu = st.sidebar.radio("Navegación", ["El Parque 🌳 (Feed)", "Nuevo Post 📸", "Perfiles 🐕"])

# --- 4. SECCIÓN: SUBIR FOTO ---
if menu == "Nuevo Post 📸":
    st.header("Crear Publicación")
    with st.form("post_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre de la mascota")
        with col2:
            emocion = st.selectbox("Mood", ["🐶 Feliz", "🤪 Loco", "😴 Dormilón", "😎 Cool", "🥺 Tierno"])
        mensaje = st.text_area("Descripción")
        foto = st.file_uploader("Sube la foto", type=['jpg', 'png', 'jpeg'])
        submitted = st.form_submit_button("¡Publicar!")
        
        if submitted and foto and nombre:
            nuevo_post = {
                "nombre": nombre, # Importante: Usaremos esto para agrupar el perfil
                "emocion": emocion,
                "mensaje": mensaje,
                "foto": foto,
                "fecha": datetime.now().strftime("%H:%M"),
                "likes": 0,
                "comentarios": []
            }
            st.session_state['posts'].append(nuevo_post)
            st.success("¡Guau! Publicado.")
            st.balloons()

# --- 5. SECCIÓN: EL FEED ---
elif menu == "El Parque 🌳 (Feed)":
    st.header("Comunidad")
    if not st.session_state['posts']:
        st.info("El parque está vacío.")
    else:
        # Filtro opcional
        filtro = st.multiselect("Filtrar por mood:", ["🐶 Feliz", "🤪 Loco", "😴 Dormilón", "😎 Cool", "🥺 Tierno"])
        posts_a_mostrar = [p for p in st.session_state['posts'] if not filtro or p['emocion'] in filtro]
        
        for i, post in enumerate(reversed(posts_a_mostrar)):
            with st.container(border=True):
                c1, c2 = st.columns([0.7, 0.3])
                c1.subheader(f"{post['emocion']} | {post['nombre']}")
                c2.caption(f"{post['fecha']}")
                st.image(post['foto'], use_container_width=True)
                st.write(f"**{post['nombre']} dice:** {post['mensaje']}")
                st.markdown("---")
                
                # Botones de acción
                cl, cc, cs = st.columns(3)
                if cl.button(f"🐾 {post['likes']}", key=f"like_{i}"):
                    post['likes'] += 1
                    st.rerun()
                cc.button("💬", key=f"comm_{i}")
                cs.button("🔗", key=f"share_{i}")
                
                # Comentarios
                if post['comentarios']:
                    with st.expander(f"Comentarios ({len(post['comentarios'])})"):
                        for c in post['comentarios']:
                            st.text(f"👤 {c}")

# --- 6. SECCIÓN NUEVA: PERFILES ---
elif menu == "Perfiles 🐕":
    st.header("Perfiles de Mascotas")
    
    # Paso 1: Encontrar a todas las mascotas únicas que han publicado
    if not st.session_state['posts']:
        st.warning("No hay mascotas registradas aún. ¡Sube una foto primero!")
    else:
        # Obtenemos la lista de nombres únicos (usando set)
        nombres_unicos = list(set([p['nombre'] for p in st.session_state['posts']]))
        
        # Paso 2: Seleccionar a quién queremos ver
        seleccionado = st.selectbox("¿De quién quieres ver el perfil?", nombres_unicos)
        
        # Paso 3: Filtrar los posts de ESA mascota
        posts_mascota = [p for p in st.session_state['posts'] if p['nombre'] == seleccionado]
        
        # --- DISEÑO DEL PERFIL ---
        st.markdown("---")
        
        # Encabezado del Perfil
        col_avatar, col_info = st.columns([0.3, 0.7])
        
        with col_avatar:
            # Usamos un emoji gigante o la última foto como avatar
            st.title("🐶") 
        
        with col_info:
            st.title(seleccionado)
            st.caption("Ciudadano de Petsgram")
        
        # Métricas (Stats) - ¡Esto le da el toque profesional!
        total_likes = sum([p['likes'] for p in posts_mascota])
        total_fotos = len(posts_mascota)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Publicaciones", total_fotos)
        m1.metric("Huellitas", total_likes)
        m3.metric("Seguidores", "Coming Soon") # Placeholder para el futuro
        
        st.markdown("---")
        st.subheader("📸 Galería de Fotos")
        
        # Galería en Cuadrícula (Grid)
        # Mostramos las fotos en filas de 3
        cols = st.columns(3)
        for index, post in enumerate(posts_mascota):
            # Lógica matemática para distribuir en columnas: 0, 1, 2, 0, 1, 2...
            with cols[index % 3]: 
                st.image(post['foto'], use_container_width=True)
                st.caption(post['emocion'])
