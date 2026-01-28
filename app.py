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

# Variable para saber qué perfil ver (Navegación interna)
if 'perfil_destino' not in st.session_state:
    st.session_state['perfil_destino'] = None

# --- 3. MENÚ LATERAL INTELIGENTE ---
# Si queremos cambiar de página por código, necesitamos un truco con el 'key'
if 'menu_actual' not in st.session_state:
    st.session_state['menu_actual'] = "El Parque 🌳 (Feed)"

# Callback para actualizar el menú manual
def actualizar_menu():
    st.session_state['menu_actual'] = st.session_state.nav_radio

menu = st.sidebar.radio(
    "Navegación", 
    ["El Parque 🌳 (Feed)", "Nuevo Post 📸", "Encontrar Amigo 🔎"],
    key="nav_radio", # Clave para vincularlo al estado
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
            st.session_state['perfil_destino'] = None # Reseteamos destino
            st.balloons()

# --- 5. SECCIÓN: EL FEED (Con redirección) ---
elif menu == "El Parque 🌳 (Feed)":
    st.header("Comunidad")
    
    # Reseteamos la búsqueda al entrar al parque
    # (Opcional: Si quieres que recuerde, borra esta línea)
    # st.session_state['perfil_destino'] = None 
    
    if not st.session_state['posts']:
        st.info("El parque está vacío.")
    else:
        filtro = st.multiselect("Filtrar por mood:", ["🐶 Feliz", "🤪 Loco", "😴 Dormilón", "😎 Cool", "🥺 Tierno"])
        posts_a_mostrar = [p for p in st.session_state['posts'] if not filtro or p['emocion'] in filtro]
        
        for i, post in enumerate(reversed(posts_a_mostrar)):
            with st.container(border=True):
                # CABECERA INTERACTIVA
                c1, c2 = st.columns([0.7, 0.3])
                c1.subheader(f"{post['emocion']} | {post['nombre']}")
                c2.caption(f"{post['fecha']}")
                
                # FOTO
                st.image(post['foto'], use_container_width=True)
                st.write(f"**{post['nombre']} dice:** {post['mensaje']}")
                st.markdown("---")
                
                # BOTONES
                cl, cp, cs = st.columns(3)
                
                # Like
                if cl.button(f"🐾 {post['likes']}", key=f"like_{i}"):
                    post['likes'] += 1
                    st.rerun()
                
                # Botón PERFIL (La magia ocurre aquí)
                # Al hacer clic, configuramos el destino y recargamos la página forzando el menú
                if cp.button(f"👤 Ver Perfil", key=f"perfil_{i}"):
                    st.session_state['perfil_destino'] = post['nombre']
                    # NOTA: En Streamlit puro, cambiar el radio button programáticamente es complejo.
                    # Usaremos un mensaje visual y la variable de estado para la próxima vez que clic en el menú,
                    # O simplemente mostramos un link directo.
                    # Truco simple: Mensaje Toast + Instrucción (Más estable)
                    # O Truco avanzado: Forzar cambio de página (puede ser inestable en algunas versiones)
                    st.info(f"¡Yendo al perfil de {post['nombre']}! Ve a la pestaña 'Encontrar Amigo'")
                    
                cs.button("🔗", key=f"share_{i}")

# --- 6. SECCIÓN: ENCONTRAR AMIGO (Dinámica) ---
elif menu == "Encontrar Amigo 🔎":
    st.header("Perfil de Mascota")
    
    # Obtenemos lista de nombres
    nombres_unicos = list(set([p['nombre'] for p in st.session_state['posts']]))
    
    if not nombres_unicos:
        st.warning("No hay mascotas aún.")
    else:
        # LÓGICA DE SELECCIÓN AUTOMÁTICA
        # Si venimos del feed (hay un destino guardado) y ese destino existe:
        idx_seleccion = 0
        if st.session_state['perfil_destino'] in nombres_unicos:
            idx_seleccion = nombres_unicos.index(st.session_state['perfil_destino'])
        
        # El Selectbox ahora intenta seleccionar automáticamente lo que guardamos
        seleccionado = st.selectbox(
            "Buscar amigo:", 
            nombres_unicos, 
            index=idx_seleccion
        )
        
        # Actualizamos la variable de destino por si el usuario cambia el selectbox manualmente
        st.session_state['perfil_destino'] = seleccionado

        # --- MOSTRAR EL PERFIL ---
        posts_mascota = [p for p in st.session_state['posts'] if p['nombre'] == seleccionado]
        
        st.markdown("---")
        col_avatar, col_info = st.columns([0.3, 0.7])
        with col_avatar:
            st.title("🐶") 
        with col_info:
            st.title(seleccionado)
            st.caption(f"Perfil verificado de {seleccionado}")
        
        # Stats
        m1, m2 = st.columns(2)
        m1.metric("Fotos", len(posts_mascota))
        m1.metric("Huellitas Totales", sum([p['likes'] for p in posts_mascota]))
        
        st.subheader("📸 Recuerdos")
        cols = st.columns(3)
        for index, post in enumerate(posts_mascota):
            with cols[index % 3]: 
                st.image(post['foto'], use_container_width=True)
                st.caption(post['fecha'])
