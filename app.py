
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import calendar
import os 
BASE_DIR = os.path.dirname(os.path.abspath('TP.ipynb'))
df = pd.read_csv(os.path.join(BASE_DIR, '..', 'datasets', 'data.csv'))
colonnes = ['Transaction_Date','Gender','Location','Product_Category','Quantity','Avg_Price','Discount_pct','Month','CustomerID']
df = df[colonnes]

df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])
#Remplacer les valeurs manquantes dans CustomerID et convertir en int

df['CustomerID'] = df['CustomerID'].fillna(0).astype(int)


df['Total_price'] = df['Quantity'] * df['Avg_Price'] * (1 - df['Discount_pct'] / 100)


df.head(5)
#df.dtypes
Transaction_Date	Gender	Location	Product_Category	Quantity	Avg_Price	Discount_pct	Month	CustomerID	Total_price
0	2019-01-01	M	Chicago	Nest-USA	1.0	153.71	10.0	1	17850	138.339
1	2019-01-01	M	Chicago	Nest-USA	1.0	153.71	10.0	1	17850	138.339
2	2019-01-01	M	Chicago	Nest-USA	2.0	122.77	10.0	1	17850	220.986
3	2019-01-01	M	Chicago	Nest-USA	1.0	81.50	10.0	1	17850	73.350
4	2019-01-01	M	Chicago	Nest-USA	1.0	153.71	10.0	1	17850	138.339
# Fonction 1 : Chiffre d'affaires total

def calculer_chiffre_affaire(data):
    return round(data['Total_price'].sum(), 2)

# Test
ca_total = calculer_chiffre_affaire(df)
# Fonction 2 : Frequence des meilleures ventes

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


# Test
top10 = frequence_meilleure_vente(df)
print('Top 10 categories :')
top10
Top 10 categories :
Gender	Product_Category	F	M	Total_vente
0	Office	58267.0	30116.0	88383.0
1	Apparel	20802.0	11636.0	32438.0
2	Drinkware	19194.0	11307.0	30501.0
3	Lifestyle	15327.0	9554.0	24881.0
4	Nest-USA	13299.0	8131.0	21430.0
5	Bags	10897.0	4376.0	15273.0
6	Notebooks & Journals	4891.0	4665.0	9556.0
7	Headgear	2113.0	1420.0	3533.0
8	Nest	1723.0	1114.0	2837.0
9	Housewares	1540.0	944.0	2484.0
# Fonction 3 : Indicateur du mois

def indicateur_du_mois(data, current_month=12, freq=True, abbr=False):
    
    prev_month = current_month - 1 if current_month > 1 else 12

    month_name = (
        calendar.month_abbr[current_month]
        if abbr
        else calendar.month_name[current_month]
    )

    df_cur  = data[data['Month'] == current_month]
    df_prev = data[data['Month'] == prev_month]

    if freq:
        cur_val  = len(df_cur)
        prev_val = len(df_prev)
    else:
        cur_val  = round(df_cur['Total_price'].sum(), 2)
        prev_val = round(df_prev['Total_price'].sum(), 2)

    delta = round(cur_val - prev_val, 2)

    return {'month_name': month_name, 'value': cur_val, 'delta': delta}


# Tests
ind_ca    = indicateur_du_mois(df, current_month=12, freq=False)
ind_vente = indicateur_du_mois(df, current_month=12, freq=True)
print('CA     :', ind_ca)
print('Ventes :', ind_vente)
CA     : {'month_name': 'December', 'value': 366280.73, 'delta': -40585.4}
Ventes : {'month_name': 'December', 'value': 4506, 'delta': 539}
# Graphique 1 : Barplot horizontal Top 10 ventes par genre

def barplot_top_10_ventes(data):
    
    top10 = frequence_meilleure_vente(data, top=10, ascending=True)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=top10['Product_Category'],
        x=top10['F'],
        name='F',
        orientation='h',
        marker_color='red',
        opacity=0.85
    ))

    fig.add_trace(go.Bar(
        y=top10['Product_Category'],
        x=top10['M'],
        name='M',
        orientation='h',
        marker_color='blue',
        opacity=0.85
    ))

    fig.update_layout(
        title='Frequence des 10 meilleures ventes',
        barmode='overlay',
        xaxis_title='Total vente',
        yaxis_title='Categorie du produit',
        legend_title='Sexe',
        plot_bgcolor='#f0f4ff',
        paper_bgcolor='white',
        height=450,
        margin=dict(l=130, r=20, t=60, b=50)
    )

    return fig


barplot_top_10_ventes(df).show()
# CA par semaine

CA_semaine = df.groupby(
    pd.Grouper(key='Transaction_Date', freq='W')
    )['Total_price'].sum().reset_index()


    # Graphique
fig = px.line(
        CA_semaine,
        x='Transaction_Date',
        y='Total_price',
        title="Evolution du chiffre d'affaire par semaine"
    )

fig.update_layout(
        xaxis_title="Semaine",
        yaxis_title="Chiffre d'affaire",
        template="plotly_white"

    )
# Trier par date décroissante et prendre les 100 dernières
df_100 = (
    df.sort_values('Transaction_Date', ascending=False)
    .head(100)
    .reset_index(drop=True)
)

# Sélectionner les colonnes affichées dans le dashboard
colonnes_table = ['Transaction_Date', 'Gender', 'Location', 'Product_Category', 'Quantity', 'Avg_Price', 'Discount_pct']
df_100 = df_100[colonnes_table]

df_100
Transaction_Date	Gender	Location	Product_Category	Quantity	Avg_Price	Discount_pct
0	2019-12-31	F	New York	Nest-USA	1.0	121.30	30.0
1	2019-12-31	F	Chicago	Nest-USA	2.0	121.30	30.0
2	2019-12-31	F	New York	Apparel	1.0	48.92	30.0
3	2019-12-31	M	New Jersey	Apparel	1.0	16.30	30.0
4	2019-12-31	M	New Jersey	Apparel	1.0	3.47	30.0
...	...	...	...	...	...	...	...
95	2019-12-30	F	New Jersey	Nest-USA	1.0	151.88	30.0
96	2019-12-30	F	New Jersey	Nest-USA	5.0	80.52	30.0
97	2019-12-30	F	New Jersey	Nest	1.0	355.74	30.0
98	2019-12-30	F	California	Nest-USA	1.0	151.88	30.0
99	2019-12-30	F	New York	Accessories	2.0	3.05	30.0
100 rows × 7 columns

# Graphique 4 : Indicateurs KPI du mois (cards)

def plot_vente_mois(data, abbr=False):
   
    current_month = int(data['Month'].max())

    ind_ca    = indicateur_du_mois(data, current_month=current_month, freq=False, abbr=abbr)
    ind_vente = indicateur_du_mois(data, current_month=current_month, freq=True,  abbr=abbr)

    fig = go.Figure()

    # KPI 1 — Chiffre d'affaires
    fig.add_trace(go.Indicator(
        mode='number+delta',
        value=ind_ca['value'], 
        delta=dict(
            reference=ind_ca['value'] - ind_ca['delta'],
        ),
        title=dict(text=ind_ca['month_name']),
        domain=dict(x=[0, 0.45], y=[0, 1])
    ))

    # KPI 2 — Nombre de transactions
    fig.add_trace(go.Indicator(
        mode='number+delta',
        value=ind_vente['value'],
        delta=dict(
            reference=ind_vente['value'] - ind_vente['delta'],
        ),
        title=dict(text=ind_vente['month_name'] ),
        domain=dict(x=[0.55, 1], y=[0, 1])
    ))

    fig.update_layout(
        paper_bgcolor='white',
        height=200,
        margin=dict(l=20, r=20, t=40, b=10)
    )

    return fig


plot_vente_mois(df).show()
from dash import Dash, dcc, html, dash_table, Input, Output
import dash_bootstrap_components as dbc
import os 
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import calendar


# Chargement & preparation 
BASE_DIR = os.path.dirname(os.path.abspath('TP.ipynb'))
df_raw= pd.read_csv(os.path.join(BASE_DIR, '..', 'datasets', 'data.csv'))

colonnes_utiles = [
    'CustomerID', 'Gender', 'Location',
    'Product_Category', 'Quantity', 'Avg_Price',
    'Transaction_Date', 'Month', 'Discount_pct'
]

df = df_raw[colonnes_utiles].copy()
df['CustomerID'] = df['CustomerID'].fillna(0).astype(int)

df['Transaction_Date'] = pd.to_datetime(df['Transaction_Date'])

df['Total_price'] = df['Quantity'] * df['Avg_Price'] * (1 - df['Discount_pct'] / 100)
df.head()
CustomerID	Gender	Location	Product_Category	Quantity	Avg_Price	Transaction_Date	Month	Discount_pct	Total_price
0	17850	M	Chicago	Nest-USA	1.0	153.71	2019-01-01	1	10.0	138.339
1	17850	M	Chicago	Nest-USA	1.0	153.71	2019-01-01	1	10.0	138.339
2	17850	M	Chicago	Nest-USA	2.0	122.77	2019-01-01	1	10.0	220.986
3	17850	M	Chicago	Nest-USA	1.0	81.50	2019-01-01	1	10.0	73.350
4	17850	M	Chicago	Nest-USA	1.0	153.71	2019-01-01	1	10.0	138.339
df.dtypes
CustomerID                   int32
Gender                      object
Location                    object
Product_Category            object
Quantity                   float64
Avg_Price                  float64
Transaction_Date    datetime64[ns]
Month                        int64
Discount_pct               float64
Total_price                float64
dtype: object
# Fonctions metier 
def calculer_chiffre_affaire(data):
    return round(data['Total_price'].sum())

calculer_chiffre_affaire(df)
3717667
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

frequence_meilleure_vente(data=df)
Gender	Product_Category	F	M	Total_vente
0	Office	58267.0	30116.0	88383.0
1	Apparel	20802.0	11636.0	32438.0
2	Drinkware	19194.0	11307.0	30501.0
3	Lifestyle	15327.0	9554.0	24881.0
4	Nest-USA	13299.0	8131.0	21430.0
5	Bags	10897.0	4376.0	15273.0
6	Notebooks & Journals	4891.0	4665.0	9556.0
7	Headgear	2113.0	1420.0	3533.0
8	Nest	1723.0	1114.0	2837.0
9	Housewares	1540.0	944.0	2484.0
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


indicateur_du_mois(df)
{'month_name': 'December', 'value': 4506, 'delta': 539}
def barplot_top_10_ventes(data):
    
    
    top10 = frequence_meilleure_vente(data, ascending=True)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top10['Product_Category'],
        x=top10['F'],
        name='F',
        orientation='h',
        marker_color='#7B8CDE'
    ))
    
    fig.add_trace(go.Bar(
        y=top10['Product_Category'],
        x=top10['M'],
        name='M',
        orientation='h',
        marker_color='#E8453C'
    ))
    
    fig.update_layout(
        barmode='overlay',
        title='Fréquence des 10 meilleures ventes',
        height = 400
    )
    
    return fig

barplot_top_10_ventes(df).show()
def plot_evolution_chiffre_affaire(data):
    
    weekly = (
        data.groupby(pd.Grouper(key='Transaction_Date', freq='W'))['Total_price']
        .sum()
        .reset_index()
    )
    weekly.columns = ['Semaine', 'CA']
    
    fig = px.line(
        weekly,
        x='Semaine',
        y='CA',
        title="Évolution du chiffre d'affaire par semaine",
        height=400
    )
    
    return fig

# Test
plot_evolution_chiffre_affaire(df).show()
def plot_vente_mois(data, abbr=False):
    
    ind_ca    = indicateur_du_mois(data, current_month=12, freq=False, abbr=abbr)
    ind_vente = indicateur_du_mois(data, current_month=12, freq=True,  abbr=abbr)
    
    fig = go.Figure()
    
    # Carte 1 — Chiffre d'affaires
    fig.add_trace(go.Indicator(
        mode='number+delta',
        value=ind_ca['value'],
        delta={'reference': ind_ca['value'] - ind_ca['delta']},
        title={'text': ind_ca['month_name'] },
        domain={'x': [0, 0.5], 'y': [0, 1]}
    ))
    
    # Carte 2 — Transactions
    fig.add_trace(go.Indicator(
        mode='number+delta',
        value=ind_vente['value'],
        delta={'reference': ind_vente['value'] - ind_vente['delta']},
        title={'text': ind_vente['month_name'] },
        domain={'x': [0.5, 1], 'y': [0, 1]}
    ))
    
    fig.update_layout(height=280)
    
    return fig

# Test
plot_vente_mois(df).show()
def plot_table(data):
    
    cols = ['Transaction_Date', 'Gender', 'Location', 'Product_Category', 'Quantity', 'Avg_Price', 'Discount_pct']
    
    df_100 = (
        data.sort_values('Transaction_Date', ascending=False)
        .head(100)[cols]
        .copy()
    )
    df_100['Transaction_Date'] = df_100['Transaction_Date'].dt.strftime('%Y-%m-%d')
    
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=['Date', 'Gender', 'Location', 'Product Category', 'Quantity', 'Avg Price', 'Discount Pct'],
            fill_color='#4472C4',
            font=dict(color='white', size=12),
            align='right'
        ),
        cells=dict(
            values=[df_100[col] for col in cols],
            fill_color='white',
            align='right'
        )
    )])
    
    fig.update_layout(
        title='Table des 100 dernières ventes',
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return fig

# Test
plot_table(df).show()
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([

    # Header
    html.Div([
        html.H1('ECAP Store', style={'color': 'white', 'margin': '0', 'fontSize': '22px'}),
        dcc.Dropdown(
            options=[{'label': l, 'value': l} for l in sorted(df['Location'].dropna().unique())],
            placeholder='Choisissez des zones',
            style={'width': '250px'}
        )
    ], style={
        'background': '#6aabbd',
        'padding': '14px 28px',
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center'
    }),

    # Body — 2 colonnes
    html.Div([

        # Colonne gauche — KPI + Barplot
        html.Div([
            dcc.Graph(figure=plot_vente_mois(df)),
            dcc.Graph(figure=barplot_top_10_ventes(df))
        ], style={'width': '45%', 'background': 'white', 'padding': '10px'}),

        # Colonne droite — Courbe + Table
        html.Div([
            dcc.Graph(figure=plot_evolution_chiffre_affaire(df)),
            dcc.Graph(figure=plot_table(df))
        ], style={'width': '55%', 'background': 'white', 'padding': '10px'})

    ], style={
        'display': 'flex',
        'gap': '10px',
        'padding': '20px',
        'background': '#f4f6fb'
    })

])





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
            placeholder='Choisissez des zones',
            style={'width': '250px'}
        )
    ], style={
        'background': '#6aabbd',
        'padding': '14px 28px',
        'display': 'flex',
        'justifyContent': 'space-between',
        'alignItems': 'center'
    }),

    # Body
    html.Div([

        # Colonne gauche
        html.Div([
            html.Div([
                dcc.Graph(id='graph-kpi')
            ], style={'height': '200px', 'overflow': 'hidden'}),
            dcc.Graph(id='graph-bar',style={'marginTop': '50px'})
        ], style={'flex': '1', 'background': 'white', 'padding': '10px'}),

        # Colonne droite
        html.Div([
            dcc.Graph(id='graph-line'),
            dcc.Graph(id='graph-table')
        ], style={'flex': '1.3', 'background': 'white', 'padding': '10px'})

    ], style={
        'display': 'flex',
        'gap': '10px',
        'padding': '20px',
        'background': '#f4f6fb',
        'width': '100%'
    })
])


# Callback
@app.callback(
    Output('graph-kpi',   'figure'),
    Output('graph-bar',   'figure'),
    Output('graph-line',  'figure'),
    Output('graph-table', 'figure'),
    Input('dropdown-zone', 'value')
)
def update(zone):
    if zone == 'ALL':
        filtered = df
    else:
        filtered = df[df['Location'] == zone]

    return (
        plot_vente_mois(filtered),
        barplot_top_10_ventes(filtered),
        plot_evolution_chiffre_affaire(filtered),
        plot_table(filtered)
    )




app.run(debug=False, jupyter_mode='inline', port=8050)
 
