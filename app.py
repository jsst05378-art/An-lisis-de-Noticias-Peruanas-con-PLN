import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import re
from collections import Counter

# ─── Página ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AnalizaPerú | Noticias con PLN",
    page_icon="🗞️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@300;400;600&display=swap');
html, body, [class*="css"] { font-family: 'Source Sans 3', sans-serif; }
.main-title {
    font-family: 'Playfair Display', serif; font-size: 3rem;
    font-weight: 900; color: #C0392B; line-height: 1.1; margin-bottom: 0;
}
.main-subtitle {
    font-size: 1rem; color: #7f8c8d; font-weight: 300;
    margin-top: 0.2rem; margin-bottom: 2rem;
    letter-spacing: 0.08em; text-transform: uppercase;
}
.metric-card {
    background: linear-gradient(135deg,#1a1a2e,#16213e);
    border-radius:12px; padding:1.2rem 1.4rem; color:white;
    border-left:4px solid #C0392B; margin-bottom:0.5rem;
}
.metric-value { font-family:'Playfair Display',serif; font-size:2.2rem; font-weight:700; color:#E74C3C; }
.metric-label { font-size:0.8rem; color:#aaa; text-transform:uppercase; letter-spacing:0.1em; }
.news-card {
    background:white; border-radius:10px; padding:1.2rem 1.4rem;
    margin-bottom:1rem; border-top:3px solid; box-shadow:0 2px 8px rgba(0,0,0,0.08);
}
.news-title { font-weight:600; font-size:1rem; margin-bottom:0.4rem; }
.news-meta  { font-size:0.78rem; color:#888; }
.tag { display:inline-block; padding:2px 10px; border-radius:20px; font-size:0.72rem;
       font-weight:600; text-transform:uppercase; letter-spacing:0.06em; margin-right:4px; }
.tag-positivo { background:#d5f5e3; color:#1e8449; }
.tag-negativo { background:#fadbd8; color:#c0392b; }
.tag-neutro   { background:#eaecee; color:#555; }
.section-header {
    font-family:'Playfair Display',serif; font-size:1.5rem; color:#1a1a2e;
    border-bottom:2px solid #C0392B; padding-bottom:0.3rem; margin-bottom:1.2rem;
}
.stButton>button {
    background:#C0392B !important; color:white !important; border:none !important;
    border-radius:8px !important; font-weight:600 !important; padding:0.6rem 1.6rem !important;
}
.stButton>button:hover { background:#a93226 !important; }
div[data-testid="stSidebar"] { background:#1a1a2e; }
div[data-testid="stSidebar"] * { color:#ecf0f1 !important; }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  MÓDULO 1 — DATOS (exactamente 5 categorías, igual que el notebook)
# ═══════════════════════════════════════════════════════════════════════════════

NOTICIAS_SEED = [
    {
        "titulo": "Alianza Lima y el demoledor récord que conseguirá si vence a FC Cajamarca por el Apertura",
        "descripcion": "Alianza Lima busca sellar una marca sin precedentes en la Liga 1. Un triunfo en Cajamarca activará un registro estadístico imposible de alcanzar. El equipo de Pablo Guede llegaría a 42 puntos y un promedio de 2.47, superando registros históricos del fútbol peruano.",
        "fuente": "Líbero", "url": "https://libero.pe/futbol-peruano/alianza-lima/2026/05/24/alianza-lima-demoledor-record-conseguira-vence-fc-cajamarca-apertura-2196648", "fecha": "24/05/2026",
    },
    {
        "titulo": "Debate de equipos técnicos entre Fuerza Popular y Juntos por el Perú en segunda vuelta",
        "descripcion": "Los equipos técnicos de los partidos Fuerza Popular y Juntos por el Perú debaten de cara a la segunda vuelta presidencial del 7 de junio. El JNE organizó el debate con seis bloques temáticos en Jesús María.",
        "fuente": "RPP Noticias", "url": "https://rpp.pe/politica/elecciones/", "fecha": "24/05/2026",
    },
    {
        "titulo": "Universitario de Deportes empató con CD Moquegua y pierde opciones en la Liga 1",
        "descripcion": "El entrenador Héctor Cúper mostró su decepción. El equipo crema necesita ganar para mantenerse en el Torneo Apertura 2026. Alianza Lima ya es campeón.",
        "fuente": "Líbero", "url": "https://libero.pe/futbol-peruano/universitario", "fecha": "23/05/2026",
    },
    {
        "titulo": "Keiko Fujimori y Roberto Sánchez: segunda vuelta presidencial el 7 de junio de 2026",
        "descripcion": "Los candidatos presidenciales buscan captar el voto de los indecisos. El próximo debate se realizará en la sede del JNE. Las encuestas muestran un escenario muy reñido entre ambas candidaturas.",
        "fuente": "RPP Noticias", "url": "https://rpp.pe/politica/elecciones/", "fecha": "24/05/2026",
    },
    {
        "titulo": "Sporting Cristal vs ADT: partido crucial por el Torneo Apertura Liga 1 2026",
        "descripcion": "Sporting Cristal enfrenta a ADT en duelo vital. El equipo celeste necesita ganar para mantener opciones en la tabla. Zé Ricardo confía en su equipo tras los entrenamientos de la semana.",
        "fuente": "Líbero", "url": "https://libero.pe/futbol-peruano/sporting-cristal", "fecha": "23/05/2026",
    },
    {
        "titulo": "Senamhi activa alerta por lluvias extremas en 65 provincias del Perú",
        "descripcion": "El Senamhi emitió alertas por precipitaciones intensas en la sierra y selva peruana. Las regiones más afectadas incluyen Cusco, Puno y Ayacucho. Se recomienda evitar zonas de riesgo de huaico.",
        "fuente": "RPP Noticias", "url": "https://rpp.pe/actualidad/", "fecha": "24/05/2026",
    },
    {
        "titulo": "Dólar en Perú hoy: tipo de cambio sube ante incertidumbre electoral por segunda vuelta",
        "descripcion": "El tipo de cambio del dólar registró incremento por la incertidumbre del proceso electoral. Los mercados financieros muestran cautela y los analistas advierten volatilidad hasta las elecciones.",
        "fuente": "RPP Noticias", "url": "https://rpp.pe/economia/", "fecha": "24/05/2026",
    },
    {
        "titulo": "Liga 1: tabla de posiciones tras la fecha 16 del Torneo Apertura 2026",
        "descripcion": "Alianza Lima lidera con 39 puntos y ya aseguró el título del Apertura bajo la dirección de Pablo Guede. Universitario y Sporting Cristal pelean por los puestos internacionales.",
        "fuente": "Líbero", "url": "https://libero.pe/futbol-peruano/liga-1", "fecha": "22/05/2026",
    },
    {
        "titulo": "Congreso del Perú debate proyecto de ley sobre seguridad ciudadana ante ola de criminalidad",
        "descripcion": "El Congreso discute medidas legislativas contra la inseguridad. Los legisladores proponen endurecer penas para extorsión y sicariato. La PNP reportó un incremento de delitos violentos en Lima.",
        "fuente": "RPP Noticias", "url": "https://rpp.pe/politica/congreso/", "fecha": "23/05/2026",
    },
    {
        "titulo": "Pablo Guede habló sobre el futuro de Federico Girotti en Alianza Lima",
        "descripcion": "El técnico Pablo Guede elogió el rendimiento de Girotti en el Torneo Apertura y señaló que el club hará lo posible para retener al delantero de cara al Clausura 2026.",
        "fuente": "Líbero", "url": "https://libero.pe/futbol-peruano/alianza-lima", "fecha": "24/05/2026",
    },
    {
        "titulo": "Pedro Francke presenta propuestas económicas de Juntos por el Perú",
        "descripcion": "El exministro Pedro Francke expuso propuestas para incrementar la inversión pública y reformar el sistema tributario. Ismael Benavides de Fuerza Popular cuestionó las propuestas en el debate técnico.",
        "fuente": "RPP Noticias", "url": "https://rpp.pe/politica/elecciones/", "fecha": "24/05/2026",
    },
    {
        "titulo": "Ignacio Buse avanza en Roland Garros y podría enfrentar a Rublev en cuartos",
        "descripcion": "El tenista peruano Ignacio Buse sigue sorprendiendo en Roland Garros. Derrotó a su rival en tres sets y podría enfrentarse al ruso Andrey Rublev en la siguiente ronda del Grand Slam.",
        "fuente": "Líbero", "url": "https://libero.pe/deportes/tenis", "fecha": "23/05/2026",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
#  MÓDULO 2 — PREPROCESAMIENTO
# ═══════════════════════════════════════════════════════════════════════════════

STOPWORDS_ES = {
    "el","la","los","las","un","una","unos","unas","de","del","al","a","ante",
    "bajo","con","contra","desde","en","entre","hacia","hasta","para","por",
    "según","sin","sobre","tras","y","e","o","u","ni","que","se","su","sus",
    "le","les","lo","me","mi","mis","nos","nuestro","nuestra","ya","fue",
    "son","han","más","pero","si","no","es","como","este","esta","estos",
    "estas","ese","esa","esos","esas","aquel","aquella","yo","tú","él","ella",
    "también","así","muy","bien","cuando","donde","quien","cual","cuál","qué",
    "cómo","cuándo","dónde","después","antes","durante","mientras","aunque",
    "porque","sino","pues","luego","entonces","además","incluso","solo",
    "ha","ser","estar","haber","tener","hacer","poder","ir","ver","dar","saber",
    "querer","llegar","pasar","deber","poner","parecer","quedar","creer",
    "llevar","dejar","seguir","encontrar","llamar","venir","pensar","salir",
    "tomar","conocer","vivir","sentir","tratar","mirar","contar","empezar",
    "buscar","existir","entrar","trabajar","escribir","producir","ocurrir",
    "entender","pedir","recibir","recordar","terminar","permitir","aparecer",
    "comenzar","servir","sacar","necesitar","mantener","resultar","leer",
    "cambiar","presentar","crear","abrir","considerar","puede","tiene",
}

def limpiar_texto(texto: str) -> str:
    texto = texto.lower()
    texto = re.sub(r"http\S+|www\S+", "", texto)
    texto = re.sub(r"[^\w\sáéíóúüñ]", " ", texto)
    texto = re.sub(r"\d+", "", texto)
    return re.sub(r"\s+", " ", texto).strip()

def tokenizar(texto: str) -> list:
    return [t for t in texto.split() if len(t) > 2]

def eliminar_stopwords(tokens: list) -> list:
    return [t for t in tokens if t not in STOPWORDS_ES]

def lematizar_simple(token: str) -> str:
    sufijos = [("aciones","ación"),("iendo","er"),("ando","ar"),
               ("aron","ar"),("ados","ado"),("adas","ada"),
               ("mente",""),("ísimo","o"),("ísima","a")]
    for suf, rep in sufijos:
        if token.endswith(suf) and len(token) > len(suf) + 3:
            return token[:-len(suf)] + rep
    return token

def preprocesar(texto: str) -> dict:
    limpio   = limpiar_texto(texto)
    tokens   = tokenizar(limpio)
    sin_stop = eliminar_stopwords(tokens)
    lemas    = [lematizar_simple(t) for t in sin_stop]
    return {
        "texto_limpio": limpio, "tokens": tokens,
        "tokens_sin_stopwords": sin_stop, "lemas": lemas,
        "n_tokens": len(tokens), "n_palabras_utiles": len(sin_stop),
    }

# ═══════════════════════════════════════════════════════════════════════════════
#  MÓDULO 3 — TÉCNICAS PLN
# ═══════════════════════════════════════════════════════════════════════════════

# ── 3.1 Clasificación mejorada con pesos (5 categorías = igual al notebook) ────
# Cada keyword tiene un peso: palabras muy específicas valen más (2),
# palabras genéricas valen menos (1). Esto evita empates y clasificaciones
# incorrectas cuando una noticia mezcla vocabulario de varias categorías.

CATEGORIAS_PESOS = {
    "Política": {
        "elecciones":2,"segunda vuelta":2,"candidato":2,"candidata":2,
        "keiko":2,"fujimori":2,"roberto sánchez":2,"juntos por el perú":2,
        "fuerza popular":2,"jne":2,"jurado nacional":2,"voto":2,
        "congreso":1,"presidente":1,"gobierno":1,"debate presidencial":2,
        "legislativo":1,"senado":1,"ministro":1,"premier":1,
        "partido político":1,"campaña":1,"encuesta":1,
    },
    "Deportes": {
        "alianza lima":2,"universitario":2,"sporting cristal":2,"liga 1":2,
        "torneo apertura":2,"torneo clausura":2,"pablo guede":2,
        "héctor cúper":2,"federico girotti":2,"ignacio buse":2,
        "roland garros":2,"grand slam":2,"fc cajamarca":2,
        "fútbol":1,"gol":1,"partido":1,"cancha":1,"entrenador":1,
        "delantero":1,"portero":1,"defensa":1,"técnico":1,
        "tenis":1,"deporte":1,"campeón":1,"tabla de posiciones":2,
    },
    "Economía": {
        "dólar":2,"tipo de cambio":2,"sol peruano":2,"sunat":2,
        "mercado financiero":2,"banco central":2,"igv":2,"inflación":2,
        "economía":1,"inversión":1,"banco":1,"precio":1,"mercado":1,
        "empleo":1,"tributario":1,"finanzas":1,"exportación":1,
        "importación":1,"pbi":2,"recesión":2,
    },
    "Seguridad": {
        "extorsión":2,"sicariato":2,"crimen organizado":2,"narcotráfico":2,
        "pnp":2,"policía nacional":2,"delito":2,"robo":2,"asesinato":2,
        "criminalidad":2,"inseguridad":2,"banda criminal":2,
        "seguridad ciudadana":2,"homicidio":2,
        "crimen":1,"criminal":1,"delincuencia":1,"violencia":1,
    },
    "Clima": {
        "senamhi":2,"huaico":2,"inundación":2,"terremoto":2,"sismo":2,
        "lluvias extremas":2,"alerta meteorológica":2,"fenómeno del niño":2,
        "lluvia":1,"alerta":1,"clima":1,"temperatura":1,"emergencia":1,
        "precipitación":2,"sequía":2,"helada":2,"nevada":2,
    },
}

def clasificar_categoria(titulo: str, descripcion: str) -> str:
    """
    Clasificador por pesos. Suma el peso de cada keyword encontrado.
    Frases exactas (2+ palabras) se buscan antes que palabras sueltas.
    Devuelve la categoría con mayor score, o 'General' si todas son 0.
    """
    texto = (titulo + " " + descripcion).lower()
    # normalizar: quitar tildes para matching más robusto
    texto_norm = texto  # mantenemos tildes, el diccionario ya las tiene

    scores = {cat: 0 for cat in CATEGORIAS_PESOS}
    for cat, kws in CATEGORIAS_PESOS.items():
        for kw, peso in kws.items():
            if kw in texto_norm:
                scores[cat] += peso

    mejor = max(scores, key=scores.get)
    return mejor if scores[mejor] > 0 else "General"

# ── 3.2 Análisis de sentimiento ─────────────────────────────────────────────────
PALABRAS_POSITIVAS = {
    "récord","campeón","triunfo","victoria","logro","éxito","avance","mejora",
    "positivo","ganó","gana","lidera","destaca","crecimiento","progreso",
    "excelente","histórico","demoledor","sorprende","gran","mejor",
    "refuerza","celebra","avanzó","clasificó","apoya","sobresaliente",
}
PALABRAS_NEGATIVAS = {
    "crisis","corrupción","escándalo","derrota","pérdida","caída","fracaso",
    "problema","conflicto","negativo","malo","peor","pésimo","riesgo","peligro",
    "violencia","crimen","delito","alerta","emergencia","incertidumbre",
    "anticuado","decepción","protesta","impunidad","acusado","ola",
    "extorsión","sicariato","criminalidad","lluvia","sismo","caos",
}

def analizar_sentimiento(titulo: str, descripcion: str) -> dict:
    texto  = (titulo + " " + descripcion).lower()
    tokens = re.findall(r"\b\w+\b", texto)
    pos    = sum(1 for t in tokens if t in PALABRAS_POSITIVAS)
    neg    = sum(1 for t in tokens if t in PALABRAS_NEGATIVAS)
    total  = pos + neg
    if total == 0:
        return {"etiqueta":"Neutro","score":0.0,"positivas":0,"negativas":0}
    score = (pos - neg) / total
    etiqueta = "Positivo" if score > 0.15 else ("Negativo" if score < -0.15 else "Neutro")
    return {"etiqueta":etiqueta,"score":round(score,3),"positivas":pos,"negativas":neg}

# ── 3.3 NER ─────────────────────────────────────────────────────────────────────
PERSONAS = {
    "pablo guede","keiko fujimori","roberto sánchez","pedro francke",
    "ismael benavides","federico girotti","paolo guerrero","héctor cúper",
    "ignacio buse","andrey rublev","zé ricardo","jorge fossati",
}
ORGANIZACIONES = {
    "alianza lima","universitario","sporting cristal","fc cajamarca","adt",
    "fuerza popular","juntos por el perú","jne","senamhi","sunat","pnp",
    "liga 1","rpp","libero","congreso","banco central",
}
LUGARES = {
    "lima","perú","cajamarca","cusco","arequipa","piura","trujillo",
    "huancayo","puno","ayacucho","moquegua","huancavelica","jesús maría",
    "loreto","callao","paris","francia",
}

def extraer_entidades(texto: str) -> dict:
    tl  = texto.lower()
    ent = {"PERSONA":[], "ORGANIZACIÓN":[], "LUGAR":[]}
    for p in PERSONAS:
        if p in tl: ent["PERSONA"].append(p.title())
    for o in ORGANIZACIONES:
        if o in tl: ent["ORGANIZACIÓN"].append(o.title())
    for l in LUGARES:
        if re.search(r"\b" + re.escape(l) + r"\b", tl):
            ent["LUGAR"].append(l.title())
    return {k: list(set(v)) for k, v in ent.items()}

# ── Pipeline ─────────────────────────────────────────────────────────────────────
def analizar_noticia(n: dict) -> dict:
    titulo = n.get("titulo","")
    desc   = n.get("descripcion", titulo)
    texto  = titulo + ". " + desc
    prep   = preprocesar(texto)
    cat    = clasificar_categoria(titulo, desc)
    sent   = analizar_sentimiento(titulo, desc)
    ner    = extraer_entidades(texto)
    freq   = Counter(prep["tokens_sin_stopwords"]).most_common(6)
    return {
        **n,
        "categoria":          cat,
        "sentimiento":        sent["etiqueta"],
        "score_sentimiento":  sent["score"],
        "palabras_pos":       sent["positivas"],
        "palabras_neg":       sent["negativas"],
        "entidades":          ner,
        "n_entidades":        sum(len(v) for v in ner.values()),
        "tokens_utiles":      prep["n_palabras_utiles"],
        "palabras_freq":      freq,
        "texto_limpio":       prep["texto_limpio"],
    }

@st.cache_data(ttl=1800, show_spinner=False)
def cargar_noticias_adicionales():
    extra = []
    try:
        r = requests.get("https://rpp.pe/ultimas-noticias",
                         headers={"User-Agent":"Mozilla/5.0"}, timeout=8)
        soup = BeautifulSoup(r.text, "html.parser")
        for it in soup.select(".story-item__title")[:6]:
            t = it.get_text(strip=True)
            if len(t) > 25:
                extra.append({"titulo":t,"descripcion":t,"fuente":"RPP Noticias",
                               "url":"https://rpp.pe","fecha":"24/05/2026"})
    except Exception:
        pass
    return extra

@st.cache_data(show_spinner=False)
def cargar_y_analizar():
    extras = cargar_noticias_adicionales()
    return [analizar_noticia(n) for n in NOTICIAS_SEED + extras]

# ═══════════════════════════════════════════════════════════════════════════════
#  PALETAS
# ═══════════════════════════════════════════════════════════════════════════════
COLORES_CAT = {
    "Política":"#E74C3C","Deportes":"#2980B9","Economía":"#27AE60",
    "Seguridad":"#8E44AD","Clima":"#F39C12","General":"#7F8C8D",
}
COLORES_SENT = {"Positivo":"#27AE60","Negativo":"#E74C3C","Neutro":"#95A5A6"}

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🗞️ AnalizaPerú")
    st.markdown("*Análisis de noticias peruanas con PLN*")
    st.divider()
    seccion = st.radio("Sección", ["📊 Dashboard","🔍 Analizar texto","📰 Noticias","🧪 Técnicas PLN"],
                       label_visibility="collapsed")
    st.divider()
    st.markdown("**Fuentes**")
    st.markdown("- 🔴 RPP Noticias\n- 🔵 Diario Líbero")
    st.divider()
    st.markdown("**Técnicas PLN**")
    st.markdown("1. Clasificación (5 categorías)\n2. Análisis de sentimiento\n3. NER (entidades)")

# Carga
with st.spinner("Cargando noticias…"):
    noticias = cargar_y_analizar()
df = pd.DataFrame(noticias)

# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if "Dashboard" in seccion:
    st.markdown('<p class="main-title">AnalizaPerú</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Sistema Inteligente de Análisis de Noticias Peruanas · PLN 2026</p>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Noticias analizadas</div></div>', unsafe_allow_html=True)
    with c2:
        pct = round(len(df[df.sentimiento=="Positivo"])/len(df)*100)
        st.markdown(f'<div class="metric-card"><div class="metric-value">{pct}%</div><div class="metric-label">Tono positivo</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df.n_entidades.sum()}</div><div class="metric-label">Entidades detectadas</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df.categoria.nunique()}</div><div class="metric-label">Categorías</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Verificación de clasificación (debug opcional)
    with st.expander("🔎 Ver clasificación detallada por noticia"):
        debug_rows = []
        for n in NOTICIAS_SEED:
            texto = (n["titulo"] + " " + n["descripcion"]).lower()
            scores = {}
            for cat, kws in CATEGORIAS_PESOS.items():
                scores[cat] = sum(peso for kw, peso in kws.items() if kw in texto)
            cat_asig = max(scores, key=scores.get)
            debug_rows.append({"Título": n["titulo"][:60]+"…", "Categoría": cat_asig,
                                **{c: s for c, s in scores.items()}})
        st.dataframe(pd.DataFrame(debug_rows), use_container_width=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown('<p class="section-header">Noticias por categoría</p>', unsafe_allow_html=True)
        cc = df.categoria.value_counts().reset_index()
        cc.columns = ["Categoría","Total"]
        fig = px.bar(cc, x="Total", y="Categoría", orientation="h",
                     color="Categoría", color_discrete_map=COLORES_CAT,
                     template="plotly_white")
        fig.update_layout(showlegend=False, margin=dict(l=0,r=0,t=10,b=0), height=280)
        st.plotly_chart(fig, use_container_width=True)

    with cb:
        st.markdown('<p class="section-header">Distribución de sentimiento</p>', unsafe_allow_html=True)
        sc = df.sentimiento.value_counts().reset_index()
        sc.columns = ["Sentimiento","Total"]
        fig2 = px.pie(sc, values="Total", names="Sentimiento",
                      color="Sentimiento", color_discrete_map=COLORES_SENT,
                      hole=0.5, template="plotly_white")
        fig2.update_layout(margin=dict(l=0,r=0,t=10,b=0), height=280)
        st.plotly_chart(fig2, use_container_width=True)

    # Entidades más frecuentes
    st.markdown('<p class="section-header">Entidades más mencionadas</p>', unsafe_allow_html=True)
    all_p, all_o, all_l = [], [], []
    for _, row in df.iterrows():
        e = row.get("entidades",{})
        all_p.extend(e.get("PERSONA",[]))
        all_o.extend(e.get("ORGANIZACIÓN",[]))
        all_l.extend(e.get("LUGAR",[]))

    ce1,ce2,ce3 = st.columns(3)
    for col, lst, emoji, label in [
        (ce1, all_p, "👤", "Personas"),
        (ce2, all_o, "🏛️", "Organizaciones"),
        (ce3, all_l, "📍", "Lugares"),
    ]:
        with col:
            st.markdown(f"**{emoji} {label}**")
            for nombre, n in Counter(lst).most_common(5):
                st.markdown(f"- {nombre} `×{n}`")

    # Scatter
    st.markdown('<p class="section-header">Sentimiento vs. riqueza de entidades</p>', unsafe_allow_html=True)
    fig3 = px.scatter(df, x="score_sentimiento", y="n_entidades",
                      color="categoria", size="tokens_utiles",
                      hover_data=["titulo","fuente"],
                      color_discrete_map=COLORES_CAT,
                      labels={"score_sentimiento":"Score sentimiento",
                              "n_entidades":"N° entidades","categoria":"Categoría"},
                      template="plotly_white")
    fig3.add_vline(x=0, line_dash="dash", line_color="#aaa")
    fig3.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  ANALIZAR TEXTO
# ═══════════════════════════════════════════════════════════════════════════════
elif "Analizar" in seccion:
    st.markdown('<p class="main-title">Analizar texto</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Ingresa cualquier noticia peruana para analizarla en tiempo real</p>', unsafe_allow_html=True)

    titulo_in = st.text_input("Título", placeholder="Ej: Alianza Lima logra récord histórico…")
    cuerpo_in = st.text_area("Cuerpo / descripción", height=160,
                              placeholder="Pega el texto de la noticia…")

    if st.button("🔍 Analizar con PLN"):
        if not titulo_in.strip():
            st.warning("Ingresa al menos el título.")
        else:
            res = analizar_noticia({"titulo":titulo_in,"descripcion":cuerpo_in or titulo_in,
                                    "fuente":"Manual","url":"","fecha":"Hoy"})
            st.markdown("---")
            st.markdown("### Resultados")
            ca,cb,cc = st.columns(3)
            ca.metric("Categoría", res["categoria"])
            cb.metric("Sentimiento", res["sentimiento"])
            cc.metric("Entidades", res["n_entidades"])

            c1,c2 = st.columns(2)
            with c1:
                st.markdown("**🧹 Preprocesamiento**")
                prep = preprocesar(titulo_in+". "+(cuerpo_in or ""))
                st.json({"tokens_totales":prep["n_tokens"],
                         "palabras_útiles":prep["n_palabras_utiles"],
                         "muestra_lemas":prep["lemas"][:12]})
            with c2:
                st.markdown("**🏷️ Entidades (NER)**")
                for tipo, lista in res["entidades"].items():
                    if lista: st.markdown(f"**{tipo}:** {', '.join(lista)}")

            if res["palabras_freq"]:
                st.markdown("**📊 Palabras más frecuentes**")
                wdf = pd.DataFrame(res["palabras_freq"], columns=["Palabra","Frecuencia"])
                fig_w = px.bar(wdf, x="Frecuencia", y="Palabra", orientation="h",
                               color_discrete_sequence=["#C0392B"], template="plotly_white")
                fig_w.update_layout(height=220, margin=dict(l=0,r=0,t=5,b=0), showlegend=False)
                st.plotly_chart(fig_w, use_container_width=True)

            score = res["score_sentimiento"]
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=round(score*100),
                title={"text":"Score sentimiento (−100 → +100)"},
                gauge={"axis":{"range":[-100,100]},
                       "bar":{"color":"#C0392B"},
                       "steps":[{"range":[-100,-15],"color":"#fadbd8"},
                                 {"range":[-15,15],"color":"#eaecee"},
                                 {"range":[15,100],"color":"#d5f5e3"}]},
            ))
            fig_g.update_layout(height=250, margin=dict(l=20,r=20,t=30,b=0))
            st.plotly_chart(fig_g, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  NOTICIAS
# ═══════════════════════════════════════════════════════════════════════════════
elif "Noticias" in seccion:
    st.markdown('<p class="main-title">Noticias analizadas</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Filtros y detalle de cada noticia procesada</p>', unsafe_allow_html=True)

    cf1,cf2,cf3 = st.columns(3)
    with cf1:
        cats = ["Todas"] + sorted(df.categoria.unique().tolist())
        fc = st.selectbox("Categoría", cats)
    with cf2:
        fs = st.selectbox("Sentimiento", ["Todos","Positivo","Neutro","Negativo"])
    with cf3:
        fuentes = ["Todas"] + sorted(df.fuente.unique().tolist())
        ff = st.selectbox("Fuente", fuentes)

    dff = df.copy()
    if fc != "Todas":  dff = dff[dff.categoria == fc]
    if fs != "Todos":  dff = dff[dff.sentimiento == fs]
    if ff != "Todas":  dff = dff[dff.fuente == ff]

    st.markdown(f"**{len(dff)} noticias**")
    for _, row in dff.iterrows():
        col_b = COLORES_CAT.get(row["categoria"],"#ccc")
        tc = {"Positivo":"tag-positivo","Negativo":"tag-negativo","Neutro":"tag-neutro"}.get(row["sentimiento"],"tag-neutro")
        ents = ""
        for tipo, lista in row["entidades"].items():
            if lista: ents += f"<span style='font-size:.75rem;color:#555'>{tipo}: {', '.join(lista[:3])}</span><br>"
        st.markdown(f"""
        <div class="news-card" style="border-top-color:{col_b}">
            <div class="news-title">{row['titulo']}</div>
            <div class="news-meta">
                📰 {row['fuente']} &nbsp;·&nbsp; 📅 {row['fecha']} &nbsp;·&nbsp;
                <span class="tag" style="background:{col_b}22;color:{col_b}">{row['categoria']}</span>
                <span class="tag {tc}">{row['sentimiento']}</span>
            </div>
            <br>{ents}
        </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TÉCNICAS PLN
# ═══════════════════════════════════════════════════════════════════════════════
elif "Técnicas" in seccion:
    st.markdown('<p class="main-title">Técnicas PLN</p>', unsafe_allow_html=True)
    st.markdown('<p class="main-subtitle">Explicación y demostración de cada técnica aplicada</p>', unsafe_allow_html=True)

    tab1,tab2,tab3,tab4 = st.tabs(["🧹 Preprocesamiento","📂 Clasificación","😊 Sentimiento","🏷️ NER"])

    with tab1:
        st.markdown("### Preprocesamiento de texto")
        st.markdown("Pipeline de 4 etapas: **Limpieza → Tokenización → Stopwords → Lematización**")
        ejemplo = st.selectbox("Noticia de ejemplo:", df.titulo.tolist())
        row_ej  = df[df.titulo == ejemplo].iloc[0]
        texto_ej = row_ej["titulo"] + ". " + row_ej.get("descripcion","")
        prep_ej  = preprocesar(texto_ej)
        c1,c2 = st.columns(2)
        with c1:
            st.markdown("**Texto original:**"); st.info(texto_ej[:300])
            st.markdown("**Texto limpio:**");   st.success(prep_ej["texto_limpio"][:300])
        with c2:
            st.markdown(f"**Tokens ({prep_ej['n_tokens']}):**"); st.code(" | ".join(prep_ej["tokens"][:20]))
            st.markdown(f"**Sin stopwords ({prep_ej['n_palabras_utiles']}):**"); st.code(" | ".join(prep_ej["tokens_sin_stopwords"][:20]))
            st.markdown("**Lemas:**"); st.code(" | ".join(prep_ej["lemas"][:20]))

    with tab2:
        st.markdown("### Clasificación de texto (5 categorías)")
        st.markdown("""
        Clasificador por **diccionario de keywords ponderados**. Cada keyword tiene un peso:
        - **Peso 2** — términos muy específicos (ej: *alianza lima*, *jne*, *senamhi*, *dólar*)
        - **Peso 1** — términos generales (ej: *fútbol*, *banco*, *clima*)
        
        Se suman los pesos y se asigna la categoría con mayor score. Esto evita empates.
        """)
        cat_fuente = df.groupby(["categoria","fuente"]).size().reset_index(name="n")
        fig_cf = px.bar(cat_fuente, x="categoria", y="n", color="fuente",
                        barmode="group", template="plotly_white",
                        color_discrete_sequence=["#C0392B","#2980B9"],
                        labels={"categoria":"Categoría","n":"Noticias","fuente":"Fuente"})
        fig_cf.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_cf, use_container_width=True)

        st.markdown("**Keywords con mayor peso por categoría:**")
        for cat, kws in CATEGORIAS_PESOS.items():
            top = [k for k,v in kws.items() if v==2][:6]
            st.markdown(f"- **{cat}:** {', '.join(top)}")

    with tab3:
        st.markdown("### Análisis de Sentimiento")
        st.markdown("Léxico de polaridad · Score = (pos − neg) / total · Umbral ±0.15")
        fig_box = px.box(df, x="sentimiento", y="score_sentimiento",
                         color="sentimiento", color_discrete_map=COLORES_SENT,
                         template="plotly_white")
        fig_box.update_layout(height=300, showlegend=False, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_box, use_container_width=True)

        sent_cat = df.groupby(["categoria","sentimiento"]).size().reset_index(name="n")
        fig_sc2 = px.bar(sent_cat, x="categoria", y="n", color="sentimiento",
                         barmode="stack", color_discrete_map=COLORES_SENT,
                         template="plotly_white", labels={"categoria":"Categoría","n":"Noticias"})
        fig_sc2.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig_sc2, use_container_width=True)

    with tab4:
        st.markdown("### Reconocimiento de Entidades (NER)")
        st.markdown("Gazeteer del contexto peruano: **👤 Personas · 🏛️ Organizaciones · 📍 Lugares**")
        all_ent = []
        for _, row in df.iterrows():
            for tipo, lista in row["entidades"].items():
                for e in lista:
                    all_ent.append({"Entidad":e,"Tipo":tipo,"Categoría":row["categoria"]})
        df_ent = pd.DataFrame(all_ent)
        if not df_ent.empty:
            top_e = df_ent.Entidad.value_counts().head(12).reset_index()
            top_e.columns = ["Entidad","Menciones"]
            top_e = top_e.merge(df_ent[["Entidad","Tipo"]].drop_duplicates(), on="Entidad")
            fig_ner = px.bar(top_e, x="Menciones", y="Entidad", orientation="h",
                             color="Tipo",
                             color_discrete_map={"PERSONA":"#E74C3C","ORGANIZACIÓN":"#2980B9","LUGAR":"#27AE60"},
                             template="plotly_white")
            fig_ner.update_layout(height=380, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig_ner, use_container_width=True)

            tabla = df[["titulo","categoria","entidades"]].copy()
            tabla["Personas"]      = tabla.entidades.apply(lambda e: ", ".join(e.get("PERSONA",[])))
            tabla["Organizaciones"]= tabla.entidades.apply(lambda e: ", ".join(e.get("ORGANIZACIÓN",[])))
            tabla["Lugares"]       = tabla.entidades.apply(lambda e: ", ".join(e.get("LUGAR",[])))
            st.dataframe(tabla[["titulo","categoria","Personas","Organizaciones","Lugares"]]
                         .rename(columns={"titulo":"Título","categoria":"Categoría"}),
                         use_container_width=True, height=300)
