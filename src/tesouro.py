import numpy as np
import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots # Import the make_subplots function

#Exemplos

#Tesouro IPCA+  2029
#Tesouro Selic 2029
#Tesouro Renda+ Aposentadoria Extra 2049
TIPO = "Tesouro Renda+ Aposentadoria Extra"
VCTO = 2049

# Read the uploaded file into a pandas dataframe
df = pd.read_csv('../data/PrecoTaxaTesouroDireto.csv',delimiter=';', decimal=',', encoding='latin1')
# Parse the date fields to datetime
df['Data Vencimento'] = pd.to_datetime(df['Data Vencimento'], format='%d/%m/%Y')
df['Data Base'] = pd.to_datetime(df['Data Base'], format='%d/%m/%Y')

df['PU Venda Manha'] = pd.to_numeric(df['PU Venda Manha'],  errors='coerce')
df['Taxa Compra Manha'] = pd.to_numeric(df['Taxa Compra Manha'], errors='coerce')

# Print the dataframe
print( df['Tipo Titulo'].unique())


filtered_df = df[
    (df['Tipo Titulo'] == TIPO) & (df['Data Vencimento'].dt.year == VCTO)
]
#print(filtered_df)


# Sort the dataframe by Data Base
filtered_df = filtered_df.sort_values(by=['Data Base'])

# Create a figure with two subplots
fig = make_subplots(rows=1, cols=2, subplot_titles=("Taxa Compra "+filtered_df['Tipo Titulo'].values[0], "PU Compra "+filtered_df['Tipo Titulo'].values[0]))

# Add traces for Taxa Venda Manha and PU Compra Manha
fig.add_trace(go.Scatter(x=filtered_df['Data Base'], y=filtered_df['Taxa Compra Manha'], name="Taxa Compra Manha"), row=1, col=1)
fig.add_trace(go.Scatter(x=filtered_df['Data Base'], y=filtered_df['PU Compra Manha'], name="PU Compra Manha", yaxis="y2"), row=1, col=2)

# Configure y-axis titles and show the figure
fig.update_yaxes(title_text="Taxa Compra Manha", row=1, col=1)
fig.update_yaxes(title_text="PU Compra Manha", row=1, col=2)

#fig.show()

fig.write_html('fig1.html', auto_open=True)