import streamlit as st

st.set_page_config(page_title="TC Contrast Pro", page_icon="☢️", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# 🔒 SISTEMA DE SEGURIDAD (BARRERA DE ACCESO)
# ==========================================
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔒 Acceso Restringido")
    st.markdown("Esta calculadora es de uso privado. Ingrese su clave para continuar.")
    
    pin_ingresado = st.text_input("PIN de seguridad:", type="password")
    
    if st.button("Ingresar"):
        # ACÁ PODÉS CAMBIAR EL "1234" POR LA CLAVE QUE QUIERAS
        if pin_ingresado == "1234":  
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("❌ PIN incorrecto. Acceso denegado.")
            
    st.stop() # Esto frena la carga del resto de la página si no hay PIN
# ==========================================

# (A PARTIR DE ACÁ, CARGA LA APP SOLO SI EL PIN ES CORRECTO)

with st.sidebar:
    st.title("⚙️ Ajustes Especiales")
    modo_pediatrico = st.toggle("👶 Activar Modo Pediátrico")
    if modo_pediatrico: st.warning("Cálculo por peso estricto (1.5 - 2.0 ml/kg). Presión reducida.")
    st.markdown("---")
    sumar_purga = st.toggle("💧 Sumar 15 ml (Purgado de tubuladura)")
    if sumar_purga: st.info("Se suman 15 ml al volumen final para compensar el espacio muerto.")
    st.markdown("---")
    st.markdown("### 📚 Guía de Emergencias")
    with st.expander("🚨 Extravasación de Contraste"):
        st.write("1. Detener inyección.\n2. Aspirar líquido residual.\n3. Retirar catéter.\n4. Elevar extremidad.\n5. Aplicar frío/calor.")
    with st.expander("💊 Premedicación"):
        st.write("- Prednisona: 50 mg VO (13, 7 y 1h antes).\n- Difenhidramina: 50 mg IV/IM 1h antes.")

st.title("☢️ Asistente de Dosificación y Física TC")
st.markdown("Cálculo avanzado de masa magra, caudales, tiempos de retardo y parámetros físicos del tubo.")
st.markdown("---")

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("👤 Paciente")
    peso = st.number_input("Peso Total (kg)", 3.0, 250.0, 75.0, 0.5)
    altura = st.number_input("Altura (cm)", 40.0, 220.0, 170.0, 1.0, disabled=modo_pediatrico)
    edad = st.number_input("Edad (años)", 1, 120, 40, 1)
    sexo = st.radio("Sexo Biológico", ["Hombre", "Mujer"], horizontal=True, disabled=modo_pediatrico)

with col2:
    st.subheader("💉 Hardware y Vía")
    tomografo = st.selectbox("Tomógrafo (Cortes)", ["16 Cortes (Estándar)", "64 Cortes (Rápido)", "128+ Cortes (Ultrarrápido)"], index=1)
    inyector = st.selectbox("Tipo de Inyector", ["Doble Cabezal (Contraste + Suero)", "Cabezal Simple (Solo Contraste)"])
    tipo_via = st.selectbox("Naturaleza de la Vía", [
        "Periférica Estándar (Abocath común)", 
        "Periférica Alta Presión (Fenestrada)", 
        "Power PICC / Port-a-Cath (Violeta)", 
        "Vía Central Estándar (CVC/Silicona)"
    ])
    cateter = st.selectbox("Calibre (Gauge)", ["18G (Verde)", "20G (Rosa)", "22G (Azul)", "24G (Amarillo)"])
    marca_contraste = st.selectbox("Marca del Fármaco", ["Omnipaque", "Optiray", "Iomeron", "Telebrix", "Xenetix", "Genérico"])
    
with col3:
    st.subheader("🧪 Estudio y Contraste")
    concentracion = st.selectbox("Concentración (mgI/ml)", [300, 320, 350, 370, 400], index=2)
    region = st.selectbox("Región Anatómica", [
        "Abdomen y Pelvis", "Solo Abdomen", "Solo Pelvis", "Tórax, Abdomen y Pelvis (TAP)",
        "Tórax (Solo)", "Cerebro", "Cuello", "Urotomografía (Uro-TC)",
        "Angio - Pulmonar (TEP)", "Angio - Aorta / Vasos de Cuello", "Angio - Miembros Inferiores", "Musculoesquelético / Partes Blandas"
    ])
    patologia = st.selectbox("Protocolo Clínico", ["Rutina / Estándar", "Oncológico (Multifásico)", "Estudio Arterial Puro", "Urgencia / Trauma"])

st.markdown("---")
st.subheader("🩸 Función Renal - CKD-EPI 2021 (Opcional)")
tiene_laboratorio = st.checkbox("El paciente cuenta con análisis de Creatinina sérica")

alerta_renal = False
egfr = None
lab_texto = "Sin laboratorio previo"

if tiene_laboratorio:
    creatinina = st.number_input("Creatinina (mg/dL)", 0.1, 15.0, 0.9, 0.1)
    kappa, alpha, factor_sexo = (0.7, -0.241, 1.012) if sexo == "Mujer" else (0.9, -0.302, 1.0)
    scr_kappa = creatinina / kappa
    egfr = 142 * (min(scr_kappa, 1) ** alpha) * (max(scr_kappa, 1) ** -1.200) * (0.9938 ** edad) * factor_sexo
    lab_texto = f"Creatinina: {creatinina} mg/dL (eGFR: {egfr:.1f})"
    
    if egfr >= 60: st.success(f"**eGFR: {egfr:.1f}** - Riesgo Bajo.")
    elif 30 <= egfr < 60: st.warning(f"**eGFR: {egfr:.1f}** - Precaución. Evaluar nefroprotección.")
    else: 
        st.error(f"**ALERTA CRÍTICA: eGFR {egfr:.1f} (<30)**. Contraindicación relativa.")
        alerta_renal = True

st.markdown("---")

# LÍMITES DE CATÉTER Y VÍA
limites_cateter = {"18G (Verde)": 6.5, "20G (Rosa)": 5.0, "22G (Azul)": 3.0, "24G (Amarillo)": 1.5}
flujo_max_cateter = limites_cateter[cateter]
bloqueo_via_central = False
alerta_picc = False

if "Vía Central Estándar" in tipo_via:
    flujo_max_cateter = 0.0
    bloqueo_via_central = True
elif "Power PICC" in tipo_via:
    flujo_max_cateter = min(flujo_max_cateter, 5.0)
    alerta_picc = True

flujo_sugerido = 3.0
fases_info = ""
mapa_fisiologico = ""

# LÓGICA DE PROTOCOLOS Y MAPA FISIOLÓGICO
if "TEP" in region:
    mg_kg_lbw, flujo_sugerido = 400, 4.5
    fases_info = "- **Fase Arterial Pulmonar:** Bolus Tracking en Tronco Pulmonar (Disparo a los **10 - 12 segundos**)."
    kvp_sugerido = "80 - 100 kVp" if (peso if not modo_pediatrico else 40) < 85 else "120 kVp"
    mapa_fisiologico = "- **0 a 5 seg:** Vena Cava Superior.\n- **10 a 12 seg:** Pico en Arteria Pulmonar.\n- **15 a 18 seg:** Retorno venoso a aurícula izquierda."
elif "Aorta" in region:
    mg_kg_lbw, flujo_sugerido = 550, 4.5
    fases_info = "- **Fase Arterial Pura:** Utilizar *Bolus Tracking* en Aorta descendente (Umbral 120 - 150 HU)."
    kvp_sugerido = "80 - 100 kVp" if (peso if not modo_pediatrico else 40) < 85 else "120 kVp"
    mapa_fisiologico = "- **10 a 12 seg:** Circulación pulmonar.\n- **18 a 22 seg:** Pico máximo en Aorta.\n- **25 a 30 seg:** Distribución a mesentéricas y renales."
elif "Miembros Inferiores" in region:
    mg_kg_lbw, flujo_sugerido, kvp_sugerido = 550, 4.0, "80 - 100 kVp"
    fases_info = "- **Arterial Periférica:** Bolus Tracking en Aorta abdominal distal o Ilíacas."
    mapa_fisiologico = "- **20 a 25 seg:** Bifurcación ilíaca.\n- **30 a 40 seg:** Arterias femorales y poplíteas.\n- **45 a 60 seg:** Vasos tibiales y pedios."
elif "Urotomografía" in region:
    mg_kg_lbw, flujo_sugerido, kvp_sugerido = 500, 3.0, "120 kVp"
    fases_info = "- **Sin Contraste:** Para litiasis.\n- **Fase Nefrográfica:** A los **90 - 100 segundos**.\n- **Fase Excretora (Uro):** **10 a 15 minutos**."
    mapa_fisiologico = "- **35 a 40 seg:** Fase Corticomedular.\n- **90 a 100 seg:** Fase Nefrográfica (riñón homogéneo).\n- **10 a 15 min:** Fase Excretora (cálices, uréteres, vejiga)."
elif "TAP" in region or "Abdomen" in region or "Pelvis" in region:
    mg_kg_lbw, flujo_sugerido, kvp_sugerido = (500 if "TAP" in region or "Oncológico" in patologia else 450), 3.0, "120 kVp"
    if "Solo Pelvis" in region:
        fases_info = "- **Fase Venosa/Tardía:** Disparo a los **70 - 90 segundos**."
    elif "Oncológico" in patologia:
        fases_info = "- **Trifásico:** Arterial Tardía (**35-40s**) | Portal (**70s**) | Tardía (**3-5 min**)."
    else:
        fases_info = "- **Fase Portal / Venosa Única:** Disparo a los **65 - 75 segundos**."
    mapa_fisiologico = "- **18 a 22 seg:** Arterial Temprana.\n- **35 a 40 seg:** Arterial Tardía (Hígado/Páncreas).\n- **65 a 75 seg:** Fase Portal (Máximo realce venoso hepático).\n- **3 a 5 min:** Equilibrio."
elif "Cerebro" in region:
    mg_kg_lbw, flujo_sugerido, kvp_sugerido = 400, 2.0, "120 - 140 kVp (Cerebro)"
    fases_info = "- **Retardo Prolongado:** Esperar **3 a 5 minutos** post-inyección."
    mapa_fisiologico = "- **15 a 20 seg:** Polígono de Willis.\n- **40 a 50 seg:** Capilares cerebrales.\n- **3 a 5 min:** Evaluación de rotura de barrera hematoencefálica (BHE)."
elif "Cuello" in region:
    mg_kg_lbw, flujo_sugerido, kvp_sugerido = 400, 2.0, "120 kVp"
    fases_info = "- **Fase Venosa Cuello:** Disparo a los **65 - 70 segundos**."
    mapa_fisiologico = "- **15 a 20 seg:** Carótidas.\n- **35 a 40 seg:** Glándulas tiroides/salivares.\n- **60 a 70 seg:** Venas yugulares y ganglios."
else:
    mg_kg_lbw, flujo_sugerido, kvp_sugerido = 400, 2.5, "120 kVp"
    fases_info = "- **Fase Venosa Estándar:** Disparo a los **60 - 70 segundos**."
    mapa_fisiologico = "- **20 a 30 seg:** Llenado arterial.\n- **60 a 80 seg:** Retorno venoso y tejidos blandos."

# LÓGICA DE CORTES DEL TOMÓGRAFO
factor_volumen = 1.0
alerta_tomografo = ""

if "128+" in tomografo:
    factor_volumen = 0.85
    volumen_salina = 50 if "Doble" in inyector else 0
    if not modo_pediatrico: flujo_sugerido += 0.5
    if "Miembros Inferiores" in region:
        alerta_tomografo = "⚠️ **Equipo Ultrarrápido (128+):** Reduzca el Pitch (velocidad de camilla) o aumente el retardo. Si la máquina avanza muy rápido, le ganará a la sangre y escaneará piernas sin yodo."
    else:
        alerta_tomografo = "⚡ **Equipo Ultrarrápido (128+):** Volumen reducido 15%. Flujo aumentado para compactar el bolo."
        if "Simple" in inyector: alerta_tomografo += " Al no tener inyector doble para empujar con suero, preste máxima atención al retardo."
elif "64" in tomografo:
    factor_volumen = 0.90
    volumen_salina = 40 if "Doble" in inyector else 0
    alerta_tomografo = "⚡ **Equipo Rápido (64):** Volumen reducido 10%. Optimización activa."
else:
    factor_volumen = 1.0
    volumen_salina = 30 if "Doble" in inyector else 0
    alerta_tomografo = "🐢 **Equipo Estándar (16):** Volumen al 100% necesario para mantener el realce durante todo el barrido."

if modo_pediatrico:
    lbw_texto = "N/A"
    volumen_final = min(peso * 1.5, 80.0)
    flujo_sugerido = 1.0 if peso < 15 else 2.0
    fases_info = "- **Monofásico:** Adaptar tiempos al ritmo respiratorio del infante."
    kvp_sugerido = "70 - 80 kVp (Radioprotección estricta)"
else:
    # -- MASA LIBRE DE GRASA (JANMAHASATIAN) --
    altura_m = altura / 100
    imc = peso / (altura_m ** 2) if altura_m > 0 else 0
    
    if sexo == "Hombre":
        lbw = (9270 * peso) / (6680 + (216 * imc))
    else:
        lbw = (9270 * peso) / (8780 + (244 * imc))
        
    lbw = max(lbw, 35.0) 
    lbw_texto = f"{lbw:.1f} kg"
    volumen_final = min(((lbw * mg_kg_lbw) * factor_volumen) / concentracion, 130)

if sumar_purga: volumen_final += 15.0

# APLICACIÓN FINAL DE LÍMITES (Seguridad)
alerta_cateter = False
if flujo_sugerido > flujo_max_cateter:
    flujo_sugerido = flujo_max_cateter
    alerta_cateter = True

if st.button("🚀 Calcular Protocolo Definitivo", type="primary", use_container_width=True):
    
    if bloqueo_via_central:
        st.error("🛑 **ALERTA LETAL DE BIOSEGURIDAD: PROHIBIDO USAR INYECTOR AUTOMÁTICO.**\nEl paciente posee una Vía Central Estándar (CVC/Silicona). La presión del inyector causará el estallido interno del catéter, provocando una embolia o taponamiento cardíaco. **Coloque una vía periférica nueva o inyecte manualmente a baja presión.**")
        flujo_sugerido = 0.0
    else:
        reporte_texto = f"""ESTUDIO: TC de {region} ({patologia})
PACIENTE: {peso} kg, {edad} años. {lab_texto}.
EQUIPO Y VÍA: Tomógrafo de {tomografo.split()[0]} cortes. Vía {tipo_via.split('(')[0].strip()} {cateter}.
CONTRASTE: {volumen_final:.0f} ml de {marca_contraste} ({concentracion} mgI/ml).
INYECCIÓN: Caudal de {flujo_sugerido:.1f} ml/s. Suero Fisiológico: {volumen_salina} ml.
RADIOPROTECCIÓN: Modulación activada. CTDIvol: ______ DLP: ______"""

        if alerta_renal: st.error("⚠️ ESTUDIO OBSERVADO POR RIESGO RENAL. Consulte con el médico.")
        st.info(alerta_tomografo)
        
        if alerta_picc: 
            st.warning("⚠️ **Power PICC / Port-a-Cath:** Flujo máximo fijado en 5.0 ml/s por protocolo. Verifique que la sigla 'Max 5ml/sec' esté impresa en la luz lila del catéter del paciente.")
        elif alerta_cateter: 
            st.warning(f"⚠️ **Atención Física:** Flujo reducido a **{flujo_max_cateter} ml/s** para evitar extravasación y rotura en esta vía.")
        
        # ACÁ ESTÁ EL CAMBIO DE LAS TARJETAS CON BORDE
        r1, r2, r3, r4 = st.columns(4)
        with r1.container(border=True):
            st.metric("Peso Magro (LBW)", lbw_texto)
        with r2.container(border=True):
            st.metric("Volumen a Cargar", f"{volumen_final:.0f} ml")
        with r3.container(border=True):
            st.metric("Velocidad (Flujo)", f"{flujo_sugerido:.1f} ml/s")
        with r4.container(border=True):
            st.metric("Suero (Flush)", f"{volumen_salina} ml")
        
        st.markdown("### ⏱️ Cronograma de Disparo (Scan Delay)")
        st.info(f"{fases_info}")
        with st.expander("📍 Mapa Fisiológico del Contraste (Recorrido Promedio)"):
            st.markdown(f"*(Basado en pacientes con gasto cardíaco normal)*\n{mapa_fisiologico}")
        
        st.markdown("### ⚡ Parámetros Físicos Sugeridos")
        t1, t2 = st.columns(2)
        with t1.container(border=True):
            st.success(f"**Tensión del Tubo:** {kvp_sugerido}")
        with t2.container(border=True):
            st.success(f"**Corriente (mAs):** Modulación Automática (ATCM) activada.")
        
        st.markdown("---")
        st.subheader("📋 Resumen Automático (HIS / RIS)")
        st.code(reporte_texto, language='text')
