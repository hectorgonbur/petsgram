import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
st.set_page_config(page_title="Petsgram", page_icon="🐾", layout="centered")

# Estilos CSS
st.markdown("""
    <style>
    .stApp { max-width: 600px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 20px; }
    /* Un pequeño truco para que el botón del nombre se vea diferente */
    button[kind="secondary"] { border: none; background: transparent; text-align: left; }
    </style>
""", unsafe_allow_html=True)

st.title("🐾 Petsgram")

# --- 2. GESTIÓN DE ESTADO (MEMORIA) ---
if 'posts' not in st.session_state:
    st.session_state['posts'] = []

# Variable memoria para la navegación entre perfiles
if 'perfil_destino' not in st.session_state:
    st.session_state['perfil_destino'] = None

# --- 3. MENÚ LATERAL ---
# Usamos un key para poder detectar cambios si fuera necesario
menu = st.sidebar.radio(
    "Navegación", 
    ["El Parque 🌳 (Feed)", "Nuevo Post 📸", "Encontrar Amigo 🔎"],
)

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
                "nombre": nombre,
                "emocion": emocion,
                "mensaje": mensaje,
                "foto": foto,
                "fecha": datetime.now().strftime("%H:%M"),
                "likes": 0,
                "comentarios": []
            }
            st.session_state['posts'].append(nuevo_post)
            st.success("¡Guau! Publicado.")
            st.session_state['perfil_destino'] = nombre # Auto-seleccionar al propio perro
            st.balloons()

# --- 5. SECCIÓN: EL FEED (Donde ocurre la magia del clic) ---
elif menu == "El Parque 🌳 (Feed)":
    st.header("Comunidad")
    
    if not st.session_state['posts']:
        st.info("El parque está vacío.")
    else:
        filtro = st.multiselect("Filtrar por mood:", ["🐶 Feliz", "🤪 Loco", "😴 Dormilón", "😎 Cool", "🥺 Tierno"])
        posts_a_mostrar = [p for p in st.session_state['posts'] if not filtro or p['emocion'] in filtro]
        
        for i, post in enumerate(reversed(posts_a_mostrar)):
            with st.container(border=True):
                
                # --- CABECERA: AHORA EL NOMBRE ES UN LINK ---
                c1, c2 = st.columns([0.7, 0.3])
                
                with c1:
                    # Usamos un botón que dice el nombre. Si le das clic -> Guardamos destino
                    label_boton = f"👤 {post['nombre']} | {post['emocion']}"
                    if st.button(label_boton, key=f"user_link_{i}", help="Ir al perfil"):
                        st.session_state['perfil_destino'] = post['nombre']
                        st.toast(f"¡Has seleccionado a {post['nombre']}! Ve a la pestaña 'Encontrar Amigo'", icon="👀")
                
                with c2:
                    st.caption(f"{post['fecha']}")
                
                # FOTO
                st.image(post['foto'], use_container_width=True)
                st.write(f"**{post['nombre']} dice:** {post['mensaje']}")
                
                st.markdown("---")
                
                # --- BARRA SOCIAL (RECUPERADA) ---
                col_like, col_comm, col_share = st.columns(3)
                
                # 1. Like
                if col_like.button(f"🐾 {post['likes']}", key=f"like_{i}"):
                    post['likes'] += 1
                    st.rerun()
                
                # 2. Comentar (Solo visual por ahora o abre el expander)
                col_comm.button("💬", key=f"btn_comm_{i}")
                    
                # 3. Compartir
                if col_share.button("🔗", key=f"share_{i}"):
                    st.toast("Link copiado")

                # Sección de Comentarios (Debajo de la barra)
                with st.expander(f"Ver comentarios ({len(post['comentarios'])})"):
                    for c in post['comentarios']:
                        st.text(f"🗣 {c}")
                    nc = st.text_input("Comentar...", key=f"new_comm_{i}")
                    if st.button("Enviar", key=f"send_comm_{i}"):
                        if nc:
                            post['comentarios'].append(nc)
                            st.rerun()

# --- 6. SECCIÓN: ENCONTRAR AMIGO (Buscador) ---
elif menu == "Encontrar Amigo 🔎":
    st.header("Buscador de Mascotas")
    
    nombres_unicos = list(set([p['nombre'] for p in st.session_state['posts']]))
    
    if not nombres_unicos:
        st.warning("No hay mascotas aún.")
    else:
        # LÓGICA DE BÚSQUEDA INTELIGENTE
        # 1. Determinamos qué índice seleccionar en la lista
        idx_seleccion = 0
        if st.session_state['perfil_destino'] in nombres_unicos:
            idx_seleccion = nombres_unicos.index(st.session_state['perfil_destino'])
        
        # 2. EL BUSCADOR (Selectbox permite escribir para buscar)
        seleccionado = st.selectbox(
            "🔍 Escribe el nombre para buscar:", 
            nombres_unicos, 
            index=idx_seleccion
        )
        
        # Actualizamos el estado por si cambiaste manualmente en el buscador
        st.session_state['perfil_destino'] = seleccionado

        # --- MOSTRAR EL PERFIL ---
        posts_mascota = [p for p in st.session_state['posts'] if p['nombre'] == seleccionado]
        
        st.markdown("---")
        # Header del Perfil
        col_pic, col_data = st.columns([0.3, 0.7])
        with col_pic:
            st.title("🐕") # Aquí iría la foto de perfil real en el futuro
        with col_data:
            st.title(seleccionado)
            st.info(f"Viendo el perfil oficial de {seleccionado}")
        
        # Stats
        m1, m2 = st.columns(2)
        m1.metric("Fotos", len(posts_mascota))
        m1.metric("Fans (Likes)", sum([p['likes'] for p in posts_mascota]))
        
        st.subheader("📸 Muro Personal")
        cols = st.columns(3)
        for index, post in enumerate(posts_mascota):
            with cols[index % 3]: 
                st.image(post['foto'], use_container_width=True)
                st.caption(post['fecha'])
