import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Steel Tycoon", page_icon="🚗", layout="wide")

st.title("🚗 Steel Tycoon: Diseña tu acero automotriz")
st.write("Modifica la composición química del acero y trata de cumplir la misión sin pasarte del presupuesto.")

@st.cache_data
def cargar_datos():
    df = pd.read_excel("pmo.xlsx")
    df.columns = df.columns.str.strip().str.replace("Â", "", regex=False)

    df = df.rename(columns={
        "Alloy code": "Alloy",
        "Temperature (°C)": "Temperature",
        "Temperature (C)": "Temperature",
        "0.2% Proof Stress (MPa)": "YS",
        "Tensile Strength (MPa)": "UTS"
    })

    for col in df.columns:
        if col != "Alloy":
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["C", "Mn", "Cr", "Ni", "Mo", "Ceq", "Temperature", "YS", "UTS"])
    return df

df = cargar_datos()

st.sidebar.header("🎮 Misión automotriz")

pieza = st.sidebar.selectbox(
    "Pieza a fabricar:",
    ["Chasis", "Barra de impacto", "Zona de deformación", "Suspensión", "Escape / zona caliente"]
)

presupuesto = st.sidebar.slider("Presupuesto máximo", 900, 5000, 1800, 100)
st.sidebar.write("Presupuesto en **USD por tonelada**.")

st.sidebar.header("🧪 Diseña tu acero")

C = st.sidebar.slider("Carbono C (%)", 0.01, 1.20, 0.25, 0.01)
Mn = st.sidebar.slider("Manganeso Mn (%)", 0.01, 2.50, 0.80, 0.01)
Cr = st.sidebar.slider("Cromo Cr (%)", 0.00, 3.00, 0.50, 0.01)
Ni = st.sidebar.slider("Níquel Ni (%)", 0.00, 4.00, 0.50, 0.01)
Mo = st.sidebar.slider("Molibdeno Mo (%)", 0.00, 1.50, 0.20, 0.01)
Temp = st.sidebar.slider("Temperatura de trabajo (°C)", 0, 700, 300, 25)

# =========================
# CÁLCULOS DEL ACERO
# =========================

Ceq = C + Mn / 6 + (Cr + Mo) / 5 + Ni / 15

UTS = (
    350
    + C * 420
    + Mn * 65
    + Cr * 55
    + Ni * 40
    + Mo * 130
    - Temp * 0.18
)

YS = (
    240
    + C * 330
    + Mn * 55
    + Cr * 40
    + Ni * 30
    + Mo * 100
    - Temp * 0.15
)

dureza = UTS / 3.4

elongacion = (
    35
    - C * 16
    - Cr * 1.5
    - Mo * 2.5
    - Ceq * 7
)

elongacion = max(elongacion, 3)

costo = (
    520
    + C * 180
    + Mn * 90
    + Cr * 280
    + Ni * 620
    + Mo * 950
)

soldabilidad = max(0, 100 - Ceq * 90)
desempeno_termico = min(100, 30 + Cr * 12 + Mo * 25 + Ni * 5)
riesgo_fractura = min(100, max(0, Ceq * 80 + C * 25 - elongacion))

# =========================
# SCORE SEGÚN PIEZA
# =========================

if pieza == "Chasis":
    score = (YS / 900) * 45 + (soldabilidad / 100) * 25 + (elongacion / 35) * 20 + (1 - costo / 5000) * 10

elif pieza == "Barra de impacto":
    score = (UTS / 1000) * 55 + (elongacion / 35) * 20 + (YS / 900) * 15 + (1 - costo / 5000) * 10

elif pieza == "Zona de deformación":
    score = (elongacion / 35) * 45 + (soldabilidad / 100) * 25 + (YS / 800) * 15 + (1 - riesgo_fractura / 100) * 15

elif pieza == "Suspensión":
    score = (YS / 900) * 50 + (UTS / 1000) * 25 + (1 - riesgo_fractura / 100) * 15 + (1 - costo / 5000) * 10

else:
    score = (desempeno_termico / 100) * 45 + (UTS / 1000) * 25 + (Cr / 3) * 15 + (Mo / 1.5) * 15

score = max(0, min(score, 100))
score_final = score * 0.65 if costo > presupuesto else score

# =========================
# RESULTADOS PRINCIPALES
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric("UTS estimado", f"{UTS:.0f} MPa")
col2.metric("YS estimado", f"{YS:.0f} MPa")
col3.metric("Costo", f"${costo:,.0f} USD/t")
col4.metric("Score", f"{score_final:.1f}/100")

if costo > presupuesto:
    st.error("Te pasaste del presupuesto. El score fue penalizado.")
else:
    st.success("Tu diseño está dentro del presupuesto.")

if score_final >= 85:
    nivel = "🏆 Excelente: acero automotriz de alto desempeño"
elif score_final >= 70:
    nivel = "✅ Bueno: diseño funcional"
elif score_final >= 55:
    nivel = "⚠️ Regular: se puede mejorar"
else:
    nivel = "❌ Malo: no cumple bien la misión"

st.subheader("🏁 Resultado del diseño")
st.write(f"Para fabricar **{pieza}**, tu acero obtuvo: **{nivel}**.")

# =========================
# SUGERENCIAS
# =========================

st.subheader("💡 Sugerencias para mejorar tu acero")

sugerencias = []

if costo > presupuesto:
    sugerencias.append("Baja Ni o Mo, porque son los elementos que más suben el costo.")

if soldabilidad < 55:
    sugerencias.append("Baja el carbono C o el carbono equivalente Ceq para mejorar la soldabilidad.")

if elongacion < 10:
    sugerencias.append("Baja C o Mo para mejorar la ductilidad y evitar que el acero sea demasiado frágil.")

if riesgo_fractura > 65:
    sugerencias.append("Reduce C o Ceq; tu acero está quedando muy resistente pero con mayor riesgo de fractura.")

if pieza == "Chasis":
    if YS < 450:
        sugerencias.append("Para chasis sube un poco Mn, Cr o Mo para aumentar el límite de fluencia.")
    if soldabilidad < 70:
        sugerencias.append("Para chasis cuida la soldabilidad, porque muchas partes se unen por soldadura.")

elif pieza == "Barra de impacto":
    if UTS < 650:
        sugerencias.append("Para barra de impacto sube C, Mn, Cr o Mo para aumentar la resistencia a tensión.")
    if elongacion < 12:
        sugerencias.append("No subas demasiado el carbono; la barra también necesita absorber energía sin romperse.")

elif pieza == "Zona de deformación":
    if elongacion < 18:
        sugerencias.append("Para zona de deformación baja C, Cr o Mo para aumentar la elongación.")
    if YS > 750:
        sugerencias.append("Tu acero puede estar demasiado rígido para una zona de deformación controlada.")

elif pieza == "Suspensión":
    if YS < 550:
        sugerencias.append("Para suspensión sube Mn, Cr o Mo para aumentar el límite de fluencia.")
    if riesgo_fractura > 60:
        sugerencias.append("Para suspensión baja C; necesitas resistencia, pero también evitar fractura.")

elif pieza == "Escape / zona caliente":
    if desempeno_termico < 60:
        sugerencias.append("Para zonas calientes sube Cr o Mo, porque mejoran el desempeño térmico.")
    if costo > presupuesto:
        sugerencias.append("Si el costo se dispara, baja Ni antes que Cr o Mo.")

if score_final < 55:
    sugerencias.append("Prueba cambios pequeños: sube Mn primero, luego Cr, y usa Mo con cuidado porque encarece mucho.")

if not sugerencias:
    sugerencias.append("Tu diseño está bastante equilibrado. Puedes intentar bajar costo reduciendo Ni o Mo sin perder demasiada resistencia.")

for s in sugerencias:
    st.info(s)

# =========================
# RESUMEN
# =========================

st.subheader("🧾 Resumen técnico del acero diseñado")

resumen = pd.DataFrame({
    "Variable": [
        "Carbono C (%)",
        "Manganeso Mn (%)",
        "Cromo Cr (%)",
        "Níquel Ni (%)",
        "Molibdeno Mo (%)",
        "Carbono equivalente Ceq",
        "Temperatura (°C)",
        "UTS (MPa)",
        "YS (MPa)",
        "Dureza estimada (HB)",
        "Elongación estimada (%)",
        "Soldabilidad (%)",
        "Riesgo de fractura (%)",
        "Costo estimado (USD/t)"
    ],
    "Valor": [
        C, Mn, Cr, Ni, Mo, Ceq, Temp, UTS, YS,
        dureza, elongacion, soldabilidad, riesgo_fractura, costo
    ]
})

st.dataframe(resumen.round(3), use_container_width=True)

# =========================
# RADAR
# =========================

st.subheader("📊 Perfil del acero diseñado")

categorias = [
    "Resistencia UTS",
    "Fluencia YS",
    "Ductilidad",
    "Soldabilidad",
    "Desempeño térmico",
    "Costo bajo"
]

valores = [
    min(100, UTS / 1000 * 100),
    min(100, YS / 900 * 100),
    min(100, elongacion / 35 * 100),
    soldabilidad,
    desempeno_termico,
    max(0, 100 - costo / 5000 * 100)
]

radar = go.Figure()

radar.add_trace(go.Scatterpolar(
    r=valores,
    theta=categorias,
    fill="toself",
    name="Acero diseñado"
))

radar.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    showlegend=True
)

st.plotly_chart(radar, use_container_width=True)

# =========================
# COMPARACIÓN CON DATASET
# =========================

st.subheader("📈 Tu acero comparado con aceros reales del dataset")

df_plot = df.copy()

df_plot["Costo estimado"] = (
    520
    + df_plot["C"] * 180
    + df_plot["Mn"] * 90
    + df_plot["Cr"] * 280
    + df_plot["Ni"] * 620
    + df_plot["Mo"] * 950
)

fig = px.scatter(
    df_plot,
    x="Costo estimado",
    y="UTS",
    color="YS",
    hover_name="Alloy",
    title="Costo vs resistencia a la tensión"
)

fig.add_trace(go.Scatter(
    x=[costo],
    y=[UTS],
    mode="markers",
    marker=dict(size=18, symbol="star"),
    name="Tu acero"
))

st.plotly_chart(fig, use_container_width=True)

# =========================
# ACEROS PARECIDOS
# =========================

st.subheader("🏭 Aceros reales parecidos al diseño")

df_real = df.copy()

df_real["distancia"] = (
    abs(df_real["C"] - C)
    + abs(df_real["Mn"] - Mn)
    + abs(df_real["Cr"] - Cr)
    + abs(df_real["Ni"] - Ni)
    + abs(df_real["Mo"] - Mo)
)

df_real["Costo estimado"] = (
    520
    + df_real["C"] * 180
    + df_real["Mn"] * 90
    + df_real["Cr"] * 280
    + df_real["Ni"] * 620
    + df_real["Mo"] * 950
)

top = df_real.sort_values("distancia").head(10)

st.dataframe(
    top[[
        "Alloy", "C", "Mn", "Cr", "Ni", "Mo",
        "Ceq", "Temperature", "YS", "UTS", "Costo estimado"
    ]].round(3),
    use_container_width=True
)

st.subheader("🧠 Interpretación automotriz")

st.write(
    f"""
    Tu acero tiene un carbono equivalente de **{Ceq:.3f}**. 
    Este valor ayuda a estimar qué tan fácil sería soldarlo. 
    Mientras más alto sea el Ceq, normalmente aumenta la resistencia, 
    pero también puede disminuir la soldabilidad.
    """
)

if pieza == "Chasis":
    st.write("Para chasis conviene buen YS, buena soldabilidad y ductilidad razonable.")
elif pieza == "Barra de impacto":
    st.write("Para barra de impacto conviene alta resistencia UTS y capacidad de absorber energía.")
elif pieza == "Zona de deformación":
    st.write("Para zonas de deformación conviene ductilidad alta, no solo máxima resistencia.")
elif pieza == "Suspensión":
    st.write("Para suspensión importa mucho el límite de fluencia porque trabaja con cargas repetidas.")
else:
    st.write("Para zonas calientes importan Cr y Mo porque ayudan al desempeño térmico.")
