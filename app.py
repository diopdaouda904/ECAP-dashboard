import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import calendar
import os

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Chargement des données
df_raw = pd.read_csv('data.csv')

colonnes_utiles = [
    'CustomerID', 'Gender', 'Location',
    'Product_Category', 'Quantity', 'Avg_Price',
    'Transaction_Date', 'Month', 'Discount_pct'
]
df = df_raw[colonnes_utiles].copy()
df['CustomerID'] = df['CustomerID'].fillna(0).astype(int)
df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
df['Total_price'] = df['Quantity'] * df['Avg_Price'] * (1 - df['Discount_pct'] / 100)

# Fonctions métier
def calculer_chiffre_affaire(data):
    return round(data['Total_price'].sum(), 2)

def frequence_meilleure_vente(data, top=10, ascending=False):
    data_clean = data.dropna(subset=['Gender'])
    pivot = (
        data_clean
        .groupby(['Product_Category', 'Gender'])['Quantity']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    for g in ['F', 'M']:
        if g not in pivot.columns:
            pivot[g] = 0
    pivot['Total_vente'] = pivot['F'] + pivot['M']
    pivot = pivot.sort_values('Total_vente', ascending=ascending).head(top)
    return pivot[['Product_Category', 'F', 'M', 'Total_vente']].reset_index(drop=True)

def indicateur_du_mois(data, current_month=12, freq=True, abbr=False):
    prev_month = current_month - 1 if current_month > 1 else 12
    month_name = calendar.month_abbr[current_month] if abbr else calendar.month_name[current_month]
    df_cur  = data[data['Month'] == current_month]
    df_prev = data[data['Month'] == prev_month]
    if freq:
        cur_val  = len(df_cur)
        prev_val = len(df_prev)
    else:
        cur_val  = round(df_cur['Total_price'].sum(), 2)
        prev_val = round(df_prev['Total_price'].sum(), 2)
    return {'month_name': month_name, 'value': cur_val, 'delta': round(cur_val - prev_val, 2)}

# Fonctions graphiques
def plot_vente_mois(data, abbr=False):
    ind_ca    = indicateur_du_mois(data, current_month=12, freq=False, abbr=abbr)
    ind_vente = indicateur_du_mois(data, current_month=12, freq=True,  abbr=abbr)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode='number+delta',
        value=ind_ca['value'],
        delta={'reference': ind_ca['value'] - ind_ca['delta']},
        title={'text': ind_ca['month_name']},
        domain={'x': [0, 0.5], 'y': [0, 1]}
    ))
    fig.add_trace(go.Indicator(
        mode='number+delta',
        value=ind_vente['value'],
        delta={'reference': ind_vente['value'] - ind_vente['delta']},
        title={'text': ind_vente['month_name']},
        domain={'x': [0.5, 1], 'y': [0, 1]}
    ))
    fig.update_layout(height=280)
    return fig

def barplot_top_10_ventes(data):
    top10 = frequence_meilleure_vente(data, ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top10['Product_Category'], x=top10['F'],
        name='F', orientation='h', marker_color='#7B8CDE'
    ))
    fig.add_trace(go.Bar(
        y=top10['Product_Category'], x=top10['M'],
        name='M', orientation='h', marker_color='#E8453C'
    ))
    fig.update_layout(
        barmode='overlay',
        title='Fréquence des 10 meilleures ventes',
        height=400
    )
    return fig

def plot_evolution_chiffre_affaire(data):
    weekly = (
        data.groupby(pd.Grouper(key='Transaction_Date', freq='W'))['Total_price']
        .sum().reset_index()
    )
    weekly.columns = ['Semaine', 'CA']
    fig = px.line(weekly, x='Semaine', y='CA',
                  title="Évolution du chiffre d'affaire par semaine", height=400)
    return fig

def plot_table(data):
    cols = ['Transaction_Date', 'Gender', 'Location', 'Product_Category', 'Quantity', 'Avg_Price', 'Discount_pct']
    df_100 = data.sort_values('Transaction_Date', ascending=False).head(100)[cols].copy()
    df_100['Transaction_Date'] = df_100['Transaction_Date'].dt.strftime('%Y-%m-%d')
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Date', 'Gender', 'Location', 'Product Category', 'Quantity', 'Avg Price', 'Discount Pct'],
            fill_color='#4472C4', font=dict(color='white', size=12), align='right'
        ),
        cells=dict(values=[df_100[col] for col in cols], fill_color='white', align='right')
    )])
    fig.update_layout(title='Table des 100 dernières ventes', height=400, margin=dict(l=0, r=0, t=40, b=0))
    return fig

# App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = html.Div([

    # Header
    html.Div([
        html.H1('ECAP Store', style={'color': 'white', 'margin': '0', 'fontSize': '22px'}),
        dcc.Dropdown(
            id='dropdown-zone',
            options=[{'label': 'Toutes les zones', 'value': 'ALL'}] +
                    [{'label': l, 'value': l} for l in sorted(df['Location'].dropna().unique())],
            value='ALL',
            clearable=False,
            style={'width': '250px'}
        )
    ], style={
        'background': '#6aabbd', 'padding': '14px 28px',
        'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'
    }),

    # Body
    html.Div([

        # Colonne gauche
        html.Div([
            html.Div([dcc.Graph(id='graph-kpi')], style={'height': '200px', 'overflow': 'hidden'}),
            dcc.Graph(id='graph-bar', style={'marginTop': '50px'})
        ], style={'flex': '1', 'background': 'white', 'padding': '10px'}),

        # Colonne droite
        html.Div([
            dcc.Graph(id='graph-line'),
            dcc.Graph(id='graph-table')
        ], style={'flex': '1.3', 'background': 'white', 'padding': '10px'})

    ], style={
        'display': 'flex', 'gap': '10px',
        'padding': '20px', 'background': '#f4f6fb', 'width': '100%'
    })
])

@app.callback(
    Output('graph-kpi',   'figure'),
    Output('graph-bar',   'figure'),
    Output('graph-line',  'figure'),
    Output('graph-table', 'figure'),
    Input('dropdown-zone', 'value')
)
def update(zone):
    filtered = df if zone == 'ALL' else df[df['Location'] == zone]
    return (
        plot_vente_mois(filtered),
        barplot_top_10_ventes(filtered),
        plot_evolution_chiffre_affaire(filtered),
        plot_table(filtered)
    )

if __name__ == '__main__':
    app.run(debug=False)
