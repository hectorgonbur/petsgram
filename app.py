import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import itertools

# -------------------------------------------------------------------
# Configuración inicial y utilidades de persistencia
# -------------------------------------------------------------------
DATA_DIR = Path("data")
BETS_DIR = DATA_DIR / "bets"
CONFIG_FILE = DATA_DIR / "config.json"
STATS_FILE = DATA_DIR / "statistics.json"

for d in [DATA_DIR, BETS_DIR]:
    d.mkdir(exist_ok=True)

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"sports": ["Fútbol", "Baloncesto", "Tenis"], "leagues": {}}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_sports():
    return load_config().get("sports", [])

def add_sport(sport):
    config = load_config()
    if sport not in config["sports"]:
        config["sports"].append(sport)
        save_config(config)

def load_leagues(sport):
    config = load_config()
    return config.get("leagues", {}).get(sport, [])

def add_league(sport, league):
    config = load_config()
    if "leagues" not in config:
        config["leagues"] = {}
    if sport not in config["leagues"]:
        config["leagues"][sport] = []
    if league not in config["leagues"][sport]:
        config["leagues"][sport].append(league)
        save_config(config)

def save_bet(bet_data, name=None):
    if name is None:
        name = f"bet_{len(list(BETS_DIR.glob('*.json')))+1}"
    filepath = BETS_DIR / f"{name}.json"
    with open(filepath, "w") as f:
        json.dump(bet_data, f, indent=2)
    return filepath

def load_bet(name):
    filepath = BETS_DIR / f"{name}.json"
    if filepath.exists():
        with open(filepath, "r") as f:
            return json.load(f)
    return None

def update_statistics(bet_data):
    # Placeholder: acumula estadísticas simples en STATS_FILE
    stats = {}
    if STATS_FILE.exists():
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    # Aquí se podrían agregar conteos por equipo, liga, etc.
    stats["last_bet"] = bet_data
    stats["total_bets"] = stats.get("total_bets", 0) + 1
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

# -------------------------------------------------------------------
# Funciones auxiliares para generación de columnas y filtros
# -------------------------------------------------------------------
def generar_combinaciones(jugadas):
    """Genera todas las combinaciones posibles a partir de la lista de signos jugados.
    jugadas: lista de strings como "1", "X2", "1X2", etc."""
    opciones = []
    for j in jugadas:
        if j == "1":
            opciones.append(["1"])
        elif j == "X":
            opciones.append(["X"])
        elif j == "2":
            opciones.append(["2"])
        elif j == "1X":
            opciones.append(["1", "X"])
        elif j == "X2":
            opciones.append(["X", "2"])
        elif j == "1X2":
            opciones.append(["1", "X", "2"])
        else:
            opciones.append([j])  # fallback
    return list(itertools.product(*opciones))

def aplicar_filtros(combinaciones, bases, filtros):
    """Aplica filtros a las combinaciones y devuelve las que cumplen.
    filtros: dict con rangos para base, signos, consecutivos, interrupciones."""
    # Por simplicidad, solo implementamos filtro BASE como ejemplo
    # En un desarrollo completo se implementarían todos
    if not filtros.get("base_activo", False):
        return combinaciones
    min_base, max_base = filtros.get("base_min", 0), filtros.get("base_max", len(bases))
    resultado = []
    for comb in combinaciones:
        aciertos_base = sum(1 for i, signo in enumerate(comb) if signo == bases[i])
        if min_base <= aciertos_base <= max_base:
            resultado.append(comb)
    return resultado

# -------------------------------------------------------------------
# Página: Apuesta Simple
# -------------------------------------------------------------------
def page_apuesta_simple():
    st.header("Apuesta Simple")
    # Inicializar estado
    if "simple_eventos" not in st.session_state:
        st.session_state.simple_eventos = 1
    if "simple_datos" not in st.session_state:
        st.session_state.simple_datos = []

    col1, col2 = st.columns([1, 1])
    with col1:
        num = st.number_input("Eventos", min_value=1, max_value=30,
                              value=st.session_state.simple_eventos, step=1,
                              key="simple_num")
        st.session_state.simple_eventos = num
    with col2:
        # Contador de eventos ganados (se calcula después de introducir resultados)
        ganados = 0
        for ev in st.session_state.simple_datos:
            if ev.get("resultado") == ev.get("base"):
                ganados += 1
        color = "green" if ganados == num else "inherit"
        st.markdown(f"<h3 style='color:{color}'>{ganados}/{num}</h3>", unsafe_allow_html=True)

    # Ajustar lista de datos al número de eventos
    while len(st.session_state.simple_datos) < num:
        st.session_state.simple_datos.append({})
    while len(st.session_state.simple_datos) > num:
        st.session_state.simple_datos.pop()

    # Renderizar cada evento
    for i in range(num):
        with st.expander(f"Evento {i+1}", expanded=True):
            ev = st.session_state.simple_datos[i]
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                deporte = st.selectbox("Deporte", load_sports() + ["Otro..."],
                                       key=f"simple_deporte_{i}",
                                       index=load_sports().index(ev.get("deporte")) if ev.get("deporte") in load_sports() else 0)
                if deporte == "Otro...":
                    new_deporte = st.text_input("Nuevo deporte", key=f"simple_new_deporte_{i}")
                    if new_deporte and st.button("Añadir", key=f"simple_add_deporte_{i}"):
                        add_sport(new_deporte)
                        st.rerun()
                ev["deporte"] = deporte
            with col_b:
                ligas = load_leagues(ev.get("deporte", ""))
                liga = st.selectbox("Liga", ligas + ["Otro..."],
                                    key=f"simple_liga_{i}",
                                    index=ligas.index(ev.get("liga")) if ev.get("liga") in ligas else 0)
                if liga == "Otro...":
                    new_liga = st.text_input("Nueva liga", key=f"simple_new_liga_{i}")
                    if new_liga and st.button("Añadir", key=f"simple_add_liga_{i}"):
                        add_league(ev.get("deporte", ""), new_liga)
                        st.rerun()
                ev["liga"] = liga
            with col_c:
                fecha = st.date_input("Fecha", value=ev.get("fecha", datetime.today()),
                                      key=f"simple_fecha_{i}")
                ev["fecha"] = fecha.isoformat()
            with col_d:
                hora = st.time_input("Hora", value=ev.get("hora", datetime.now().time()),
                                     key=f"simple_hora_{i}")
                ev["hora"] = hora.isoformat()

            col_e, col_f, col_g, col_h = st.columns(4)
            with col_e:
                local = st.text_input("Local", value=ev.get("local", ""), key=f"simple_local_{i}")
                ev["local"] = local
            with col_f:
                res_local = st.number_input("Goles Local", min_value=0, step=1,
                                            value=ev.get("res_local", 0), key=f"simple_res_local_{i}")
                ev["res_local"] = res_local
            with col_g:
                res_visit = st.number_input("Goles Visitante", min_value=0, step=1,
                                            value=ev.get("res_visit", 0), key=f"simple_res_visit_{i}")
                ev["res_visit"] = res_visit
            with col_h:
                visit = st.text_input("Visitante", value=ev.get("visit", ""), key=f"simple_visit_{i}")
                ev["visit"] = visit

            # Determinar resultado real
            if res_local > res_visit:
                resultado = "1"
            elif res_local < res_visit:
                resultado = "2"
            else:
                resultado = "X"
            ev["resultado"] = resultado

            col_i, col_j, col_k, col_l, col_m = st.columns(5)
            with col_i:
                odd1 = st.number_input("1", min_value=1.0, step=0.01, format="%.2f",
                                       value=ev.get("odd1", 1.0), key=f"simple_odd1_{i}")
                ev["odd1"] = odd1
            with col_j:
                oddx = st.number_input("X", min_value=1.0, step=0.01, format="%.2f",
                                       value=ev.get("oddx", 1.0), key=f"simple_oddx_{i}")
                ev["oddx"] = oddx
            with col_k:
                odd2 = st.number_input("2", min_value=1.0, step=0.01, format="%.2f",
                                       value=ev.get("odd2", 1.0), key=f"simple_odd2_{i}")
                ev["odd2"] = odd2
            with col_l:
                base = st.selectbox("Base", ["1", "X", "2"],
                                    index=["1","X","2"].index(ev.get("base","1")),
                                    key=f"simple_base_{i}")
                ev["base"] = base
            with col_m:
                bola = "🟢" if resultado == base else "🔴" if resultado else "⚪"
                st.markdown(f"### {bola}")

    # Totales
    st.divider()
    col_monto, col_bruta, col_neta = st.columns(3)
    with col_monto:
        monto = st.number_input("Monto jugado", min_value=0.0, step=1.0, format="%.2f",
                                key="simple_monto")
    with col_bruta:
        if monto > 0 and st.session_state.simple_datos:
            producto = 1.0
            for ev in st.session_state.simple_datos:
                if ev["base"] == "1":
                    producto *= ev["odd1"]
                elif ev["base"] == "X":
                    producto *= ev["oddx"]
                else:
                    producto *= ev["odd2"]
            ganancia_bruta = producto * monto
            st.metric("Ganancia Bruta", f"{ganancia_bruta:.2f}")
        else:
            ganancia_bruta = 0
            st.metric("Ganancia Bruta", "0.00")
    with col_neta:
        ganancia_neta = ganancia_bruta - monto
        st.metric("Ganancia Neta", f"{ganancia_neta:.2f}")

    if st.button("REGISTRAR", key="simple_registrar"):
        bet_data = {
            "tipo": "simple",
            "fecha": datetime.now().isoformat(),
            "eventos": st.session_state.simple_datos,
            "monto": monto,
            "ganancia_bruta": ganancia_bruta,
            "ganancia_neta": ganancia_neta
        }
        save_bet(bet_data)
        update_statistics(bet_data)
        st.success("Apuesta registrada")

# -------------------------------------------------------------------
# Página: Apuesta Múltiple
# -------------------------------------------------------------------
def page_apuesta_multiple():
    st.header("Apuesta Múltiple")
    # Similar a simple pero con campo JUGADA y generación de columnas
    # Inicializar estado
    if "multi_eventos" not in st.session_state:
        st.session_state.multi_eventos = 1
    if "multi_datos" not in st.session_state:
        st.session_state.multi_datos = []
    if "multi_aciertos_min" not in st.session_state:
        st.session_state.multi_aciertos_min = 0
    if "multi_aciertos_max" not in st.session_state:
        st.session_state.multi_aciertos_max = 0

    col1, col2 = st.columns([1, 1])
    with col1:
        num = st.number_input("Eventos", min_value=1, max_value=30,
                              value=st.session_state.multi_eventos, step=1,
                              key="multi_num")
        st.session_state.multi_eventos = num
    with col2:
        # Aquí se mostrará el máximo de aciertos de las columnas generadas
        st.markdown("**Aciertos máximos:** (se actualiza al generar)")
        # Por ahora placeholder
        st.info("Genera columnas para ver contador")

    # Rango de aciertos base
    col_min, col_and, col_max = st.columns([2,1,2])
    with col_min:
        min_aciertos = st.number_input("Aciertos mínimos", min_value=0, max_value=num,
                                       value=st.session_state.multi_aciertos_min, step=1,
                                       key="multi_min")
        st.session_state.multi_aciertos_min = min_aciertos
    with col_and:
        st.markdown("<h1 style='text-align: center;'>A</h1>", unsafe_allow_html=True)
    with col_max:
        max_aciertos = st.number_input("Aciertos máximos", min_value=0, max_value=num,
                                       value=st.session_state.multi_aciertos_max, step=1,
                                       key="multi_max")
        st.session_state.multi_aciertos_max = max_aciertos

    # Ajustar lista de datos
    while len(st.session_state.multi_datos) < num:
        st.session_state.multi_datos.append({})
    while len(st.session_state.multi_datos) > num:
        st.session_state.multi_datos.pop()

    # Renderizar eventos (similar a simple pero con JUGADA y BASE)
    for i in range(num):
        with st.expander(f"Evento {i+1}", expanded=True):
            ev = st.session_state.multi_datos[i]
            # Deporte, liga, fecha, hora (igual que simple)
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                deporte = st.selectbox("Deporte", load_sports() + ["Otro..."],
                                       key=f"multi_deporte_{i}",
                                       index=load_sports().index(ev.get("deporte")) if ev.get("deporte") in load_sports() else 0)
                if deporte == "Otro...":
                    new_deporte = st.text_input("Nuevo deporte", key=f"multi_new_deporte_{i}")
                    if new_deporte and st.button("Añadir", key=f"multi_add_deporte_{i}"):
                        add_sport(new_deporte)
                        st.rerun()
                ev["deporte"] = deporte
            with col_b:
                ligas = load_leagues(ev.get("deporte", ""))
                liga = st.selectbox("Liga", ligas + ["Otro..."],
                                    key=f"multi_liga_{i}",
                                    index=ligas.index(ev.get("liga")) if ev.get("liga") in ligas else 0)
                if liga == "Otro...":
                    new_liga = st.text_input("Nueva liga", key=f"multi_new_liga_{i}")
                    if new_liga and st.button("Añadir", key=f"multi_add_liga_{i}"):
                        add_league(ev.get("deporte", ""), new_liga)
                        st.rerun()
                ev["liga"] = liga
            with col_c:
                fecha = st.date_input("Fecha", value=ev.get("fecha", datetime.today()),
                                      key=f"multi_fecha_{i}")
                ev["fecha"] = fecha.isoformat()
            with col_d:
                hora = st.time_input("Hora", value=ev.get("hora", datetime.now().time()),
                                     key=f"multi_hora_{i}")
                ev["hora"] = hora.isoformat()

            col_e, col_f, col_g, col_h = st.columns(4)
            with col_e:
                local = st.text_input("Local", value=ev.get("local", ""), key=f"multi_local_{i}")
                ev["local"] = local
            with col_f:
                res_local = st.number_input("Goles Local", min_value=0, step=1,
                                            value=ev.get("res_local", 0), key=f"multi_res_local_{i}")
                ev["res_local"] = res_local
            with col_g:
                res_visit = st.number_input("Goles Visitante", min_value=0, step=1,
                                            value=ev.get("res_visit", 0), key=f"multi_res_visit_{i}")
                ev["res_visit"] = res_visit
            with col_h:
                visit = st.text_input("Visitante", value=ev.get("visit", ""), key=f"multi_visit_{i}")
                ev["visit"] = visit

            # Determinar resultado real
            if res_local > res_visit:
                resultado = "1"
            elif res_local < res_visit:
                resultado = "2"
            else:
                resultado = "X"
            ev["resultado"] = resultado

            col_i, col_j, col_k, col_l, col_m = st.columns(5)
            with col_i:
                odd1 = st.number_input("1", min_value=1.0, step=0.01, format="%.2f",
                                       value=ev.get("odd1", 1.0), key=f"multi_odd1_{i}")
                ev["odd1"] = odd1
            with col_j:
                oddx = st.number_input("X", min_value=1.0, step=0.01, format="%.2f",
                                       value=ev.get("oddx", 1.0), key=f"multi_oddx_{i}")
                ev["oddx"] = oddx
            with col_k:
                odd2 = st.number_input("2", min_value=1.0, step=0.01, format="%.2f",
                                       value=ev.get("odd2", 1.0), key=f"multi_odd2_{i}")
                ev["odd2"] = odd2
            with col_l:
                # JUGADA: puede ser 1, X, 2 o combinaciones
                jugada = st.text_input("JUGADA", value=ev.get("jugada", "1"), key=f"multi_jugada_{i}")
                ev["jugada"] = jugada
            with col_m:
                base = st.selectbox("BASE", ["1", "X", "2"],
                                    index=["1","X","2"].index(ev.get("base","1")),
                                    key=f"multi_base_{i}")
                ev["base"] = base

    # Monto total
    monto_total = st.number_input("MONTO", min_value=0.0, step=1.0, format="%.2f", key="multi_monto")

    # Botón para generar columnas
    if st.button("GENERAR COLUMNAS", key="multi_generar"):
        jugadas = [ev.get("jugada", "1") for ev in st.session_state.multi_datos]
        combinaciones = generar_combinaciones(jugadas)
        st.session_state["multi_combinaciones"] = combinaciones
        st.session_state["multi_monto_total"] = monto_total
        st.success(f"Se generaron {len(combinaciones)} columnas")

    # Mostrar columnas si existen
    if "multi_combinaciones" in st.session_state:
        combinaciones = st.session_state["multi_combinaciones"]
        monto_total = st.session_state.get("multi_monto_total", 0)
        num_cols = len(combinaciones)
        st.subheader(f"COLUMNAS GENERADAS ({num_cols})")
        for idx, comb in enumerate(combinaciones):
            cols = st.columns([3,1,1,1])
            with cols[0]:
                st.write(" ".join(comb))
            # Calcular cuota de la columna según las odds de cada evento
            cuota_columna = 1.0
            for j, signo in enumerate(comb):
                ev = st.session_state.multi_datos[j]
                if signo == "1":
                    cuota_columna *= ev.get("odd1", 1)
                elif signo == "X":
                    cuota_columna *= ev.get("oddx", 1)
                else:
                    cuota_columna *= ev.get("odd2", 1)
            monto_por_columna = monto_total / num_cols if num_cols > 0 else 0
            bruta = cuota_columna * monto_por_columna
            neta = bruta - monto_por_columna
            with cols[1]:
                st.write(f"Bruta: {bruta:.2f}")
            with cols[2]:
                st.write(f"Neta: {neta:.2f}")
            with cols[3]:
                # Determinar si la columna acierta dentro del rango base
                aciertos = sum(1 for j, signo in enumerate(comb) if signo == st.session_state.multi_datos[j].get("base"))
                if st.session_state.multi_aciertos_min <= aciertos <= st.session_state.multi_aciertos_max:
                    st.markdown("🟢")
                else:
                    st.markdown("🔴")

    st.divider()
    if st.button("REGISTRAR", key="multi_registrar"):
        # Guardar la apuesta múltiple
        bet_data = {
            "tipo": "multiple",
            "fecha": datetime.now().isoformat(),
            "eventos": st.session_state.multi_datos,
            "monto": monto_total,
            "aciertos_rango": [st.session_state.multi_aciertos_min, st.session_state.multi_aciertos_max],
            "columnas": st.session_state.get("multi_combinaciones", [])
        }
        save_bet(bet_data)
        update_statistics(bet_data)
        st.success("Apuesta múltiple registrada")

# -------------------------------------------------------------------
# Página: Jugadas (Sistemas)
# -------------------------------------------------------------------
def page_jugadas():
    st.header("Jugadas (Sistemas)")
    # Muy similar a apuesta múltiple pero sin campo BASE
    # Inicializar estado
    if "sis_jugadas_eventos" not in st.session_state:
        st.session_state.sis_jugadas_eventos = 1
    if "sis_jugadas_datos" not in st.session_state:
        st.session_state.sis_jugadas_datos = []

    col1, col2 = st.columns([1, 1])
    with col1:
        num = st.number_input("Eventos", min_value=1, max_value=30,
                              value=st.session_state.sis_jugadas_eventos, step=1,
                              key="sis_jugadas_num")
        st.session_state.sis_jugadas_eventos = num
    with col2:
        st.info("Contador de aciertos se actualizará en Columnas")

    while len(st.session_state.sis_jugadas_datos) < num:
        st.session_state.sis_jugadas_datos.append({})
    while len(st.session_state.sis_jugadas_datos) > num:
        st.session_state.sis_jugadas_datos.pop()

    for i in range(num):
        with st.expander(f"Evento {i+1}", expanded=True):
            ev = st.session_state.sis_jugadas_datos[i]
            # Deporte, liga, fecha, hora
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                deporte = st.selectbox("Deporte", load_sports() + ["Otro..."],
                                       key=f"sis_jugadas_deporte_{i}",
                                       index=load_sports().index(ev.get("deporte")) if ev.get("deporte") in load_sports() else 0)
                if deporte == "Otro...":
                    new_deporte = st.text_input("Nuevo deporte", key=f"sis_jugadas_new_deporte_{i}")
                    if new_deporte and st.button("Añadir", key=f"sis_jugadas_add_deporte_{i}"):
                        add_sport(new_deporte)
                        st.rerun()
                ev["deporte"] = deporte
            with col_b:
                ligas = load_leagues(ev.get("deporte", ""))
                liga = st.selectbox("Liga", ligas + ["Otro..."],
                                    key=f"sis_jugadas_liga_{i}",
                                    index=ligas.index(ev.get("liga")) if ev.get("liga") in ligas else 0)
                if liga == "Otro...":
                    new_liga = st.text_input("Nueva liga", key=f"sis_jugadas_new_liga_{i}")
                    if new_liga and st.button("Añadir", key=f"sis_jugadas_add_liga_{i}"):
                        add_league(ev.get("deporte", ""), new_liga)
                        st.rerun()
                ev["liga"] = liga
            with col_c:
                fecha = st.date_input("Fecha", value=ev.get("fecha", datetime.today()),
                                      key=f"sis_jugadas_fecha_{i}")
                ev["fecha"] = fecha.isoformat()
            with col_d:
                hora = st.time_input("Hora", value=ev.get("hora", datetime.now().time()),
                                     key=f"sis_jugadas_hora_{i}")
                ev["hora"] = hora.isoformat()

            col_e, col_f, col_g, col_h = st.columns(4)
            with col_e:
                local = st.text_input("Local", value=ev.get("local", ""), key=f"sis_jugadas_local_{i}")
                ev["local"] = local
            with col_f:
                res_local = st.number_input("Goles Local", min_value=0, step=1,
                                            value=ev.get("res_local", 0), key=f"sis_jugadas_res_local_{i}")
                ev["res_local"] = res_local
            with col_g:
                res_visit = st.number_input("Goles Visitante", min_value=0, step=1,
                                            value=ev.get("res_visit", 0), key=f"sis_jugadas_res_visit_{i}")
                ev["res_visit"] = res_visit
            with col_h:
                visit = st.text_input("Visitante", value=ev.get("visit", ""), key=f"sis_jugadas_visit_{i}")
                ev["visit"] = visit

            # Resultado
            if res_local > res_visit:
                resultado = "1"
            elif res_local < res_visit:
                resultado = "2"
            else:
                resultado = "X"
            ev["resultado"] = resultado

            col_i, col_j, col_k, col_l = st.columns(4)
            with col_i:
                odd1 = st.number_input("1", min_value=1.0, step=0.01, format="%.2f",
                                       value=ev.get("odd1", 1.0), key=f"sis_jugadas_odd1_{i}")
                ev["odd1"] = odd1
            with col_j:
                oddx = st.number_input("X", min_value=1.0, step=0.01, format="%.2f",
                                       value=ev.get("oddx", 1.0), key=f"sis_jugadas_oddx_{i}")
                ev["oddx"] = oddx
            with col_k:
                odd2 = st.number_input("2", min_value=1.0, step=0.01, format="%.2f",
                                       value=ev.get("odd2", 1.0), key=f"sis_jugadas_odd2_{i}")
                ev["odd2"] = odd2
            with col_l:
                jugada = st.text_input("JUGADA", value=ev.get("jugada", "1"), key=f"sis_jugadas_jugada_{i}")
                ev["jugada"] = jugada

    monto = st.number_input("MONTO", min_value=0.0, step=1.0, format="%.2f", key="sis_jugadas_monto")
    st.session_state["sis_jugadas_monto"] = monto

    if st.button("REGISTRAR", key="sis_jugadas_registrar"):
        bet_data = {
            "tipo": "jugadas_sistema",
            "fecha": datetime.now().isoformat(),
            "eventos": st.session_state.sis_jugadas_datos,
            "monto": monto
        }
        save_bet(bet_data)
        update_statistics(bet_data)
        st.success("Jugada registrada")

# -------------------------------------------------------------------
# Página: Filtros
# -------------------------------------------------------------------
def page_filtros():
    st.header("Filtros")
    st.markdown("**SISTEMA JUGADO**")
    # Cargar datos de la página Jugadas (si existen)
    datos_jugadas = st.session_state.get("sis_jugadas_datos", [])
    if not datos_jugadas:
        st.warning("No hay datos de Jugadas. Ve a Sistemas > Jugadas primero.")
        return

    # Mostrar lista de partidos con sus signos y base seleccionable
    st.subheader("Partidos")
    bases = []
    for i, ev in enumerate(datos_jugadas):
        cols = st.columns([2,2,2,2])
        with cols[0]:
            st.write(ev.get("local", ""))
        with cols[1]:
            st.write(ev.get("visit", ""))
        with cols[2]:
            st.write(ev.get("jugada", "1"))
        with cols[3]:
            base = st.selectbox(f"Base {i+1}", ["1","X","2"],
                                key=f"filtro_base_{i}",
                                index=["1","X","2"].index(ev.get("base","1")))
            bases.append(base)
            # Guardar base en los datos de jugadas para uso posterior
            ev["base"] = base
    st.session_state["sis_jugadas_datos"] = datos_jugadas  # actualizar

    st.divider()
    st.subheader("FILTROS SISTEMA")

    # Filtro BASE (rango de aciertos de base)
    st.markdown("**Filtro BASE**")
    col_min, col_max = st.columns(2)
    with col_min:
        base_min = st.number_input("Mín aciertos BASE", min_value=0, max_value=len(datos_jugadas),
                                   value=0, step=1, key="filtro_base_min")
    with col_max:
        base_max = st.number_input("Máx aciertos BASE", min_value=0, max_value=len(datos_jugadas),
                                   value=len(datos_jugadas), step=1, key="filtro_base_max")

    # Filtro SIGNOS (cantidad de cada signo)
    st.markdown("**Filtro SIGNOS**")
    col_1, col_x, col_2 = st.columns(3)
    with col_1:
        min_1 = st.number_input("1 mín", min_value=0, max_value=len(datos_jugadas), value=0, key="filtro_1_min")
        max_1 = st.number_input("1 máx", min_value=0, max_value=len(datos_jugadas), value=len(datos_jugadas), key="filtro_1_max")
    with col_x:
        min_x = st.number_input("X mín", min_value=0, max_value=len(datos_jugadas), value=0, key="filtro_x_min")
        max_x = st.number_input("X máx", min_value=0, max_value=len(datos_jugadas), value=len(datos_jugadas), key="filtro_x_max")
    with col_2:
        min_2 = st.number_input("2 mín", min_value=0, max_value=len(datos_jugadas), value=0, key="filtro_2_min")
        max_2 = st.number_input("2 máx", min_value=0, max_value=len(datos_jugadas), value=len(datos_jugadas), key="filtro_2_max")

    # Filtro CONSECUTIVOS
    st.markdown("**Filtro CONSECUTIVOS**")
    col_c1, col_cx, col_c2 = st.columns(3)
    with col_c1:
        cons_1_min = st.number_input("1 consec mín", min_value=0, max_value=len(datos_jugadas), value=0, key="cons_1_min")
        cons_1_max = st.number_input("1 consec máx", min_value=0, max_value=len(datos_jugadas), value=len(datos_jugadas), key="cons_1_max")
    with col_cx:
        cons_x_min = st.number_input("X consec mín", min_value=0, max_value=len(datos_jugadas), value=0, key="cons_x_min")
        cons_x_max = st.number_input("X consec máx", min_value=0, max_value=len(datos_jugadas), value=len(datos_jugadas), key="cons_x_max")
    with col_c2:
        cons_2_min = st.number_input("2 consec mín", min_value=0, max_value=len(datos_jugadas), value=0, key="cons_2_min")
        cons_2_max = st.number_input("2 consec máx", min_value=0, max_value=len(datos_jugadas), value=len(datos_jugadas), key="cons_2_max")

    # Filtro INTERRUPCIONES
    st.markdown("**Filtro INTERRUPCIONES**")
    interrupciones_min = st.number_input("Interrupciones mín", min_value=0, max_value=len(datos_jugadas), value=0, key="inter_min")
    interrupciones_max = st.number_input("Interrupciones máx", min_value=0, max_value=len(datos_jugadas), value=len(datos_jugadas), key="inter_max")

    # Guardar configuración de filtros en sesión
    st.session_state["filtros_config"] = {
        "base_min": base_min, "base_max": base_max,
        "signos_1": (min_1, max_1),
        "signos_x": (min_x, max_x),
        "signos_2": (min_2, max_2),
        "consecutivos_1": (cons_1_min, cons_1_max),
        "consecutivos_x": (cons_x_min, cons_x_max),
        "consecutivos_2": (cons_2_min, cons_2_max),
        "interrupciones": (interrupciones_min, interrupciones_max)
    }
    st.success("Filtros guardados")

# -------------------------------------------------------------------
# Página: Columnas
# -------------------------------------------------------------------
def page_columnas():
    st.header("Columnas Generadas")
    # Verificar que existen datos de jugadas y filtros
    datos_jugadas = st.session_state.get("sis_jugadas_datos", [])
    filtros = st.session_state.get("filtros_config", {})
    if not datos_jugadas:
        st.warning("No hay datos de Jugadas. Ve a Sistemas > Jugadas primero.")
        return
    if not filtros:
        st.warning("No hay filtros configurados. Ve a Sistemas > Filtros primero.")
        return

    if st.button("GENERA COLUMNAS", key="col_generar"):
        jugadas = [ev.get("jugada", "1") for ev in datos_jugadas]
        bases = [ev.get("base", "1") for ev in datos_jugadas]
        combinaciones = generar_combinaciones(jugadas)
        # Aplicar filtros (solo filtro BASE como ejemplo)
        # En una implementación completa se aplicarían todos los filtros
        min_base = filtros.get("base_min", 0)
        max_base = filtros.get("base_max", len(bases))
        combinaciones_filtradas = []
        for comb in combinaciones:
            aciertos_base = sum(1 for i, signo in enumerate(comb) if signo == bases[i])
            if min_base <= aciertos_base <= max_base:
                combinaciones_filtradas.append(comb)
        st.session_state["columnas_generadas"] = combinaciones_filtradas
        st.session_state["columnas_monto"] = st.session_state.get("sis_jugadas_monto", 0)
        st.success(f"Se generaron {len(combinaciones_filtradas)} columnas después de filtros")

    if "columnas_generadas" in st.session_state:
        combinaciones = st.session_state["columnas_generadas"]
        monto_total = st.session_state.get("columnas_monto", 0)
        num_cols = len(combinaciones)
        monto_por_columna = monto_total / num_cols if num_cols > 0 else 0

        st.subheader(f"COLUMNAS GENERADAS ({num_cols})")
        for idx, comb in enumerate(combinaciones):
            cols = st.columns([3,1,1,1])
            with cols[0]:
                st.write(" ".join(comb))
            # Calcular cuota y ganancias
            cuota = 1.0
            for i, signo in enumerate(comb):
                ev = datos_jugadas[i]
                if signo == "1":
                    cuota *= ev.get("odd1", 1)
                elif signo == "X":
                    cuota *= ev.get("oddx", 1)
                else:
                    cuota *= ev.get("odd2", 1)
            bruta = cuota * monto_por_columna
            neta = bruta - monto_por_columna
            with cols[1]:
                st.write(f"Bruta: {bruta:.2f}")
            with cols[2]:
                st.write(f"Neta: {neta:.2f}")
            with cols[3]:
                # Determinar si la columna acierta todos (para bola verde)
                aciertos = sum(1 for i, signo in enumerate(comb) if signo == datos_jugadas[i].get("resultado"))
                if aciertos == len(comb):
                    st.markdown("🟢")
                elif aciertos == 0:
                    st.markdown("🔴")
                else:
                    st.markdown("⚪")

# -------------------------------------------------------------------
# Páginas de estadísticas, billetera, guardar y exportar (placeholders funcionales)
# -------------------------------------------------------------------
def page_est_equipos():
    st.header("Estadísticas de Equipos")
    if STATS_FILE.exists():
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
        st.json(stats)
    else:
        st.info("No hay estadísticas aún")

def page_est_jugadas():
    st.header("Estadísticas de Jugadas")
    st.info("Aquí se mostrarán estadísticas de las jugadas registradas")

def page_billetera():
    st.header("Billetera")
    if "wallet" not in st.session_state:
        st.session_state.wallet = 1000.0  # saldo inicial
    st.metric("Saldo actual", f"{st.session_state.wallet:.2f}")
    col1, col2 = st.columns(2)
    with col1:
        ingreso = st.number_input("Ingresar monto", min_value=0.0, step=10.0)
        if st.button("Añadir"):
            st.session_state.wallet += ingreso
            st.rerun()
    with col2:
        retiro = st.number_input("Retirar monto", min_value=0.0, step=10.0)
        if st.button("Retirar") and retiro <= st.session_state.wallet:
            st.session_state.wallet -= retiro
            st.rerun()

def page_guardar():
    st.header("Guardar Apuesta Actual")
    nombre = st.text_input("Nombre del archivo (sin extensión)")
    if st.button("Guardar"):
        # Recopilar datos relevantes de sesión
        bet_data = {
            "timestamp": datetime.now().isoformat(),
            "simple_datos": st.session_state.get("simple_datos", []),
            "multi_datos": st.session_state.get("multi_datos", []),
            "sis_jugadas_datos": st.session_state.get("sis_jugadas_datos", []),
            # ... otros estados
        }
        if nombre:
            save_bet(bet_data, nombre)
        else:
            save_bet(bet_data)
        st.success("Apuesta guardada")

def page_exportar():
    st.header("Exportar Datos")
    st.info("Función de exportación a CSV/Excel (pendiente de implementación)")

# -------------------------------------------------------------------
# Navegación principal
# -------------------------------------------------------------------
def main():
    st.sidebar.title("Menú")
    main_option = st.sidebar.selectbox(
        "Selecciona una sección",
        ["APUESTAS", "SISTEMAS", "ESTADÍSTICAS", "GANANCIAS", "ARCHIVOS"],
        key="main_menu"
    )

    if main_option == "APUESTAS":
        sub = st.sidebar.selectbox("Submenú", ["Apuesta Simple", "Apuesta Multiple"], key="sub_apu")
        if sub == "Apuesta Simple":
            page_apuesta_simple()
        else:
            page_apuesta_multiple()
    elif main_option == "SISTEMAS":
        sub = st.sidebar.selectbox("Submenú", ["Jugadas", "Filtros", "Columnas"], key="sub_sis")
        if sub == "Jugadas":
            page_jugadas()
        elif sub == "Filtros":
            page_filtros()
        else:
            page_columnas()
    elif main_option == "ESTADÍSTICAS":
        sub = st.sidebar.selectbox("Submenú", ["Est. Equipos", "Est. Jugadas"], key="sub_est")
        if sub == "Est. Equipos":
            page_est_equipos()
        else:
            page_est_jugadas()
    elif main_option == "GANANCIAS":
        sub = st.sidebar.selectbox("Submenú", ["Billetera"], key="sub_gan")
        page_billetera()
    elif main_option == "ARCHIVOS":
        sub = st.sidebar.selectbox("Submenú", ["Guardar", "Exportar"], key="sub_arc")
        if sub == "Guardar":
            page_guardar()
        else:
            page_exportar()

if __name__ == "__main__":
    main()
