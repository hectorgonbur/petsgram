import streamlit as st
from datetime import datetime

# --- 1. CONFIGURACIÓN ESTRUCTURAL ---
st.set_page_config(page_title="Petsgram", page_icon="🐾", layout="centered")

st.markdown("""
    <style>
    .stApp { max-width: 600px; margin: 0 auto; }
    div.stButton > button { width: 100%; border-radius: 20px; }
    </style>
""", unsafe_allow_html=True)

st.title("🐾 Petsgram")

# --- 2. BASE DE DATOS (EN MEMORIA) ---
# Inicializamos las listas si no existen
if 'posts' not in st.session_state:
    st.session_state['posts'] = []

# Aquí guardaremos los perfiles: 
# Estructura: {'Benji': {'bio': 'Soy un perro feliz', 'avatar': foto, 'seguidores': [], 'siguiendo': []}}
if 'usuarios' not in st.session_state:
    st.session_state['usuarios'] = {}

# Variable para saber quién está logueado
if 'usuario_actual' not in st.session_state:
    st.session_state['usuario_actual'] = None

# Variable de navegación interna
if 'perfil_destino' not in st.session_state:
    st.session_state['perfil_destino'] = None


# --- 3. BARRA LATERAL: GESTIÓN DE IDENTIDAD ---
st.sidebar.header("🐶 Identidad")

# Lógica de "Login" simple para pruebas
nombres_registrados = list(st.session_state['usuarios'].keys())

if not nombres_registrados:
    st.sidebar.warning("¡No hay mascotas! Crea la primera.")
    modo_acceso = "Crear Cuenta"
else:
    # Selector para cambiar de usuario (Simula Login)
    modo_acceso = st.sidebar.radio("Opciones:", ["Iniciar Sesión", "Crear Cuenta"])

if modo_acceso == "Crear Cuenta":
    st.sidebar.subheader("Registro")
    with st.sidebar.form("registro_form"):
        nuevo_user = st.text_input("Nombre de Usuario")
        nueva_bio = st.text_area("Biografía (Gustos, hobbies)")
        submit_registro = st.form_submit_button("¡Unirse!")
        
        if submit_registro and nuevo_user:
            if nuevo_user in st.session_state['usuarios']:
                st.sidebar.error("¡Ese nombre ya existe!")
            else:
                # CREAMOS EL PERFIL VACÍO
                st.session_state['usuarios'][nuevo_user] = {
                    'bio': nueva_bio,
                    'seguidores': [], # Lista de nombres que me siguen
                    'siguiendo': []   # Lista de nombres que sigo
                }
                st.session_state['usuario_actual'] = nuevo_user
                st.sidebar.success(f"¡Bienvenido {nuevo_user}!")
                st.rerun()

elif modo_acceso == "Iniciar Sesión":
    # Selector para elegir quién eres hoy
    usuario_seleccionado = st.sidebar.selectbox("¿Quién eres hoy?", nombres_registrados)
    if st.sidebar.button("Ingresar como este usuario"):
        st.session_state['usuario_actual'] = usuario_seleccionado
        st.rerun()

# MOSTRAR QUIÉN SOY
if st.session_state['usuario_actual']:
    st.sidebar.write("---")
    st.sidebar.success(f"Hola, **{st.session_state['usuario_actual']}** 🟢")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['usuario_actual'] = None
        st.rerun()


# --- 4. NAVEGACIÓN PRINCIPAL ---
# Si no estás logueado, bloqueamos la app (Solo ves el registro)
if not st.session_state['usuario_actual']:
    st.info("👈 Por favor, crea una cuenta o inicia sesión en el menú de la izquierda para entrar al parque.")
    st.stop() # Detiene la ejecución aquí

# Si ya entró, mostramos el menú completo
menu = st.sidebar.radio(
    "Menú Principal", 
    ["El Parque 🌳", "Nuevo Post 📸", "Mi Perfil 🏠", "Explorar Amigos 🔎"]
)


# --- 5. SECCIÓN: NUEVO POST (Ahora automático) ---
if menu == "Nuevo Post 📸":
    st.header(f"Publicar como {st.session_state['usuario_actual']}")
    
    with st.form("post_form", clear_on_submit=True):
        # YA NO PEDIMOS NOMBRE, LO TOMAMOS DE LA SESIÓN
        c1, c2 = st.columns([0.2, 0.8])
        c1.write("👤")
        c2.write(f"**{st.session_state['usuario_actual']}**")
        
        emocion = st.selectbox("Mood", ["🐶 Feliz", "🤪 Loco", "😴 Dormilón", "😎 Cool", "🥺 Tierno"])
        mensaje = st.text_area("¿Qué está pasando?")
        foto = st.file_uploader("Foto", type=['jpg', 'png', 'jpeg'])
        
        submitted = st.form_submit_button("¡Publicar!")
        
        if submitted and foto:
            nuevo_post = {
                "nombre": st.session_state['usuario_actual'], # Autor automático
                "emocion": emocion,
                "mensaje": mensaje,
                "foto": foto,
                "fecha": datetime.now().strftime("%H:%M"),
                "likes": 0,
                "comentarios": []
            }
            st.session_state['posts'].append(nuevo_post)
            st.success("¡Publicado!")
            st.balloons()


# --- 6. SECCIÓN: EL PARQUE (Feed) ---
elif menu == "El Parque 🌳":
    st.header("Comunidad")
    
    if not st.session_state['posts']:
        st.info("Nadie ha publicado aún.")
    else:
        for i, post in enumerate(reversed(st.session_state['posts'])):
            with st.container(border=True):
                # CABECERA
                c1, c2 = st.columns([0.7, 0.3])
                # El nombre es un botón para ir al perfil de ese usuario
                if c1.button(f"👤 {post['nombre']} | {post['emocion']}", key=f"user_feed_{i}"):
                    st.session_state['perfil_destino'] = post['nombre']
                    st.info(f"Ve a la pestaña 'Explorar Amigos' para ver a {post['nombre']}")
                
                c2.caption(post['fecha'])
                st.image(post['foto'], use_container_width=True)
                st.write(f"**{post['nombre']}**: {post['mensaje']}")
                st.markdown("---")
                
                # INTERACCIONES
                col_a, col_b = st.columns(2)
                if col_a.button(f"🐾 {post['likes']} Huellitas", key=f"like_{i}"):
                    post['likes'] += 1
                    st.rerun()
                
                with st.expander(f"Comentarios ({len(post['comentarios'])})"):
                    for c in post['comentarios']:
                        st.text(c)
                    # Comentar con tu usuario actual
                    nuevo_com = st.text_input("Escribe...", key=f"comm_input_{i}")
                    if st.button("Enviar", key=f"comm_send_{i}"):
                        post['comentarios'].append(f"{st.session_state['usuario_actual']}: {nuevo_com}")
                        st.rerun()


# --- 7. SECCIÓN: MI PERFIL (Gestión propia) ---
elif menu == "Mi Perfil 🏠":
    yo = st.session_state['usuario_actual']
    datos_yo = st.session_state['usuarios'][yo]
    
    st.header(f"Perfil de {yo}")
    
    # MÉTRICAS DE SEGUIDORES
    col1, col2, col3 = st.columns(3)
    col1.metric("Seguidores", len(datos_yo['seguidores']))
    col2.metric("Siguiendo", len(datos_yo['siguiendo']))
    
    # Contar mis posts
    mis_posts = [p for p in st.session_state['posts'] if p['nombre'] == yo]
    col3.metric("Posts", len(mis_posts))
    
    st.markdown("---")
    st.subheader("Sobre mí")
    st.info(datos_yo['bio'])
    
    st.subheader("Mis Fotos")
    cols = st.columns(3)
    for idx, p in enumerate(mis_posts):
        with cols[idx % 3]:
            st.image(p['foto'], use_container_width=True)


# --- 8. SECCIÓN: EXPLORAR AMIGOS (Buscar y Seguir) ---
elif menu == "Explorar Amigos 🔎":
    st.header("Buscar Mascotas")
    
    lista_usuarios = list(st.session_state['usuarios'].keys())
    
    # Pre-selección si venimos de un clic
    idx = 0
    if st.session_state['perfil_destino'] in lista_usuarios:
        idx = lista_usuarios.index(st.session_state['perfil_destino'])
        
    seleccionado = st.selectbox("Buscar:", lista_usuarios, index=idx)
    
    # MOSTRAR PERFIL DEL OTRO
    if seleccionado:
        datos_otro = st.session_state['usuarios'][seleccionado]
        yo = st.session_state['usuario_actual']
        
        st.markdown("---")
        c_izq, c_der = st.columns([0.4, 0.6])
        
        with c_izq:
            st.title("🐶") # Aquí iría el avatar
        
        with c_der:
            st.title(seleccionado)
            st.write(datos_otro['bio'])
            
            # --- LÓGICA DE SEGUIR (DAR LA PATITA) ---
            if seleccionado != yo: # No puedo seguirme a mí mismo
                
                # Verificamos si YA lo sigo
                if seleccionado in st.session_state['usuarios'][yo]['siguiendo']:
                    # Botón para Dejar de Seguir
                    if st.button(f"❌ Dejar de seguir a {seleccionado}"):
                        st.session_state['usuarios'][yo]['siguiendo'].remove(seleccionado)
                        st.session_state['usuarios'][seleccionado]['seguidores'].remove(yo)
                        st.rerun()
                else:
                    # Botón para Seguir
                    if st.button(f"🐾 Seguir (Dar patita) a {seleccionado}"):
                        st.session_state['usuarios'][yo]['siguiendo'].append(seleccionado)
                        st.session_state['usuarios'][seleccionado]['seguidores'].append(yo)
                        st.success(f"¡Ahora sigues a {seleccionado}!")
                        st.rerun()
            else:
                st.caption("Este es tu perfil (míralo en la pestaña 'Mi Perfil')")

        # ESTADÍSTICAS DEL OTRO
        m1, m2 = st.columns(2)
        m1.metric("Seguidores", len(datos_otro['seguidores']))
        m2.metric("Siguiendo", len(datos_otro['siguiendo']))
        
        st.subheader(f"Muro de {seleccionado}")
        posts_otro = [p for p in st.session_state['posts'] if p['nombre'] == seleccionado]
        
        cg = st.columns(3)
        for idx, p in enumerate(posts_otro):
            with cg[idx % 3]:
                st.image(p['foto'], use_container_width=True)
