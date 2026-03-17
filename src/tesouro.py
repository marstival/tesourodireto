import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Configuration ---
# Available bond types (Tipo Titulo):
#   "Tesouro Selic"
#   "Tesouro Prefixado"
#   "Tesouro Prefixado com Juros Semestrais"
#   "Tesouro IPCA+"
#   "Tesouro IPCA+ com Juros Semestrais"
#   "Tesouro Renda+ Aposentadoria Extra"
#   "Tesouro Educa+"
TIPO = "Tesouro Renda+ Aposentadoria Extra"
VCTO = 2049

# --- Load data ---
df = pd.read_csv(
    '../data/PrecoTaxaTesouroDireto.csv',
    delimiter=';',
    decimal=',',
    encoding='latin1'
)
df['Data Vencimento'] = pd.to_datetime(df['Data Vencimento'], format='%d/%m/%Y')
df['Data Base'] = pd.to_datetime(df['Data Base'], format='%d/%m/%Y')
df['Taxa Compra Manha'] = pd.to_numeric(df['Taxa Compra Manha'], errors='coerce')
df['PU Compra Manha'] = pd.to_numeric(df['PU Compra Manha'], errors='coerce')

print("Títulos disponíveis:", df['Tipo Titulo'].unique())

# --- Filter and sort ---
filtered_df = df[
    (df['Tipo Titulo'] == TIPO) &
    (df['Data Vencimento'].dt.year == VCTO)
].sort_values('Data Base').reset_index(drop=True)

if filtered_df.empty:
    raise ValueError(f"Nenhum dado encontrado para '{TIPO}' com vencimento em {VCTO}.")

# --- % change of PU from first available date ---
pct_change = (filtered_df['PU Compra Manha'] / filtered_df['PU Compra Manha'].iloc[0] - 1) * 100

titulo_label = f"{TIPO} {VCTO}"

# --- Build 3-panel chart ---
fig = make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    subplot_titles=(
        "Taxa Compra Manhã (%)",
        "PU Compra Manhã (R$)",
        "Variação % do PU (base: primeira data)",
    ),
    vertical_spacing=0.08,
)

# Panel 1 — Taxa
fig.add_trace(
    go.Scatter(
        x=filtered_df['Data Base'],
        y=filtered_df['Taxa Compra Manha'],
        name="Taxa (%)",
        line=dict(color='#1F77B4', width=1.5),
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Taxa: %{y:.2f}%<extra></extra>",
    ),
    row=1, col=1,
)

# Panel 2 — PU
fig.add_trace(
    go.Scatter(
        x=filtered_df['Data Base'],
        y=filtered_df['PU Compra Manha'],
        name="PU (R$)",
        line=dict(color='#2CA02C', width=1.5),
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>PU: R$ %{y:,.2f}<extra></extra>",
    ),
    row=2, col=1,
)

# Panel 3 — % change
fill_color = 'rgba(44,160,44,0.1)'
fig.add_trace(
    go.Scatter(
        x=filtered_df['Data Base'],
        y=pct_change,
        name="Variação % PU",
        line=dict(color='#2CA02C', width=1.5),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Variação: %{y:.2f}%<extra></extra>",
    ),
    row=3, col=1,
)

# --- Axis labels ---
fig.update_yaxes(title_text="Taxa (%)", row=1, col=1)
fig.update_yaxes(title_text="PU (R$)", row=2, col=1)
fig.update_yaxes(title_text="Variação (%)", row=3, col=1)

# --- Range selector on bottom x-axis ---
fig.update_xaxes(
    rangeselector=dict(
        buttons=[
            dict(count=1,  label="1M",  step="month", stepmode="backward"),
            dict(count=3,  label="3M",  step="month", stepmode="backward"),
            dict(count=6,  label="6M",  step="month", stepmode="backward"),
            dict(count=1,  label="1A",  step="year",  stepmode="backward"),
            dict(step="all", label="MAX"),
        ]
    ),
    row=3, col=1,
)

# --- Layout ---
fig.update_layout(
    title=dict(text=titulo_label, font=dict(size=16)),
    template="plotly_white",
    hovermode="x unified",
    height=750,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    showlegend=True,
)

fig.show()
fig.write_html('fig1.html')
