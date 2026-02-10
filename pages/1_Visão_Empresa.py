# Bibliotecas
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------

# Bibliotecas necessárias
import pandas as pd
import streamlit as st
from datetime import date
import folium
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config(
    page_title='Visão Empresa - Breeze Company',
    page_icon='📈',
    layout='wide'
)

# -----------------------------------------------------------------

# Funções
def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe
        Tipos de Limpeza:
            1. Remoção de dados NaN.
            2. Mudança do tipo da coluna de dados.
            3. Remoção dos espaços das variáveis de texto.
            4. Formatação da coluna de datas
            5. Limpeza da coluna de tempo ( remoção do texto da variável numérica)

            Input: Dataframe
            Output: Dataframe
    """
    # ---------------------------- Limpeza -----------------------------

    df1 = df1[
        (df1['Delivery_person_Age'] != 'NaN ') & 
        (df1['Road_traffic_density'] != 'NaN ') &
        (df1['City'] != 'NaN ') &
        (df1['Festival'] != 'NaN ') &
        (df1['multiple_deliveries'] != 'NaN ')
    ]

    # ----------------------- Conversões de tipo ------------------------

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y' )
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # ------------------------ Remoção de espaços ------------------------
    cols_str = [
        "ID",
        "Road_traffic_density",
        "Type_of_order",
        "Type_of_vehicle",
        "City",
        "Festival"
    ]

    for col in cols_str:
        df1[col] = df1[col].astype(str).str.strip()

    # ----------------- Limpeza da coluna time_taken(min) -----------------
    df1['Time_taken(min)'] = df1['Time_taken(min)'].str.split(' ').str[1].astype(int)

    return df1

# --------------- Inicio da estrutura lógica do código --------------
# Import dataset
df = pd.read_csv( 'dataset/train.csv')
df1 = df.copy()
# Limpeza dos dados
df1 = clean_code( df )

# ------------------------------------------------------------------

# Streamlit
# ============================================
#               Barra Lateral
# ============================================

image = Image.open( 'brze.png' )
st.sidebar.image(image,  width=150)

st.sidebar.header( 'Breeze Company')
st.sidebar.subheader( 'Clique, Peça, Repita ')
st.sidebar.markdown( """---""" )

st.sidebar.header( 'Filtros')

st.sidebar.subheader('Selecione uma data')
date_slider = st.sidebar.slider(
    '',
    value=date( 2022, 4, 1 ),
    min_value=date( 2022, 2, 11 ),
    max_value=date( 2022, 4, 6 ),
    format='DD/MM/YYYY' )

date_slider = pd.to_datetime(date_slider)

st.sidebar.markdown( """---""" )

st.sidebar.subheader('Selecione as cidades')
city = st.sidebar.multiselect(
    " ",
    ['Metropolitian', 'Urban', 'Semi-Urban'],
    default=['Metropolitian', 'Urban', 'Semi-Urban'])

st.sidebar.markdown("""---""")

st.sidebar.markdown( '### Selecione o clima')
weatherconditions = st.sidebar.multiselect(
    " ",
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 
     'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms',
              'conditions Stormy', 'conditions Sunny', 'conditions Windy'])

st.sidebar.markdown("""---""")

st.sidebar.markdown('### Selecione as condições de tráfego')
traffic_conditions = st.sidebar.multiselect(
    " ",
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown( """---""" )

st.sidebar.markdown( '### Powered by Gabe')

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Cidade
linhas_selecionadas = df1['City'].isin(city)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Clima
linhas_selecionadas = df1['Weatherconditions'].isin(weatherconditions)
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_conditions)
df1 = df1.loc[linhas_selecionadas, :]

# ============================================
#               Layout no Streamlit
# ============================================

st.header('Marketplace - Visão Empresa')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tatica', 'Visão Geográfica'])

with tab1:
    with st.container():

        st.subheader(' Pedidos por dia')
        # ----- Seleção de Linhas -----
        df_aux = df1.groupby('Order_Date')['ID'].count().reset_index()
        
        # ----- Desenhando o gráfico de barras -----
        fig = px.bar(df_aux, x='Order_Date', y='ID')
        st.plotly_chart( fig, use_container_width=True )

    with st.container():
        st.markdown("""---""")

        st.subheader(' Pedidos por tipo de tráfego')
        # ----- Selecionando as Linhas -----
        df_aux = df1.groupby('Road_traffic_density')['ID'].count().reset_index()
        df_aux['entregas_percent'] = df_aux['ID'] / df_aux['ID'].sum()

        # ----- Desenhando o gráfico de pizza -----
        fig = (px.pie(df_aux, values='entregas_percent', 
                              names='Road_traffic_density'))
        st.plotly_chart(fig, use_container_width=False)

    with st.container():
        st.markdown("""---""")

        st.subheader('Volume de pedidos por cidade e tipo de tráfego')
        # ----- Seleção de Linhas -----
        df_aux = df1.groupby(['City', 'Road_traffic_density'])['ID'].count().reset_index()

        # ----- Desenhando o gráfico de bolha -----
        fig = (px.scatter(df_aux, x="City", 
                                  y="Road_traffic_density", 
                                  size="ID", color="City"))
        
        st.plotly_chart(fig, use_container_width=False)

with tab2:
    with st.container():
        
        st.subheader('Pedidos por semana')
        # ------ Criar a coluna Semana -----
        df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
        df_aux = df1.groupby('week_of_year')['ID'].count().reset_index()

        # ----- Desenhando o gráfico de linha -----
        fig = (px.line(df_aux, 
                       x='week_of_year', 
                       y='ID'))
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown("""---""")

        st.subheader('Pedidos por entregador por semana')
        # ------ Criar a coluna Semana -----
        df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )

        # ----- Quantidade de pedidos por semana -----
        # ----- Quantidade de entregadores únicos por semana -----
        df_aux01 = df1.groupby('week_of_year')['ID'].count().reset_index()
        df_aux02 = df1.groupby('week_of_year')['Delivery_person_ID'].nunique().reset_index()

        # ----- Junção dos 2 Dataframes -----
        df_aux = pd.merge(df_aux01, df_aux02, how="inner")
        df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

        # ----- Desenhando o gráfico de linhas -----
        fig = (px.line(df_aux, x='week_of_year', y='order_by_deliver'))
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader('Mapa do País')

    # ----- Seleção de linhas -----
    df_aux = (df1.groupby(['City', 'Road_traffic_density'])
            [['Delivery_location_latitude', 'Delivery_location_longitude']]
                 .median()
                 .reset_index())

    # ----- Desenhando o mapa -----
    map = folium.Map()

    for index, location_info in df_aux.iterrows():
        (folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] )
                        .add_to( map ))
        
    folium_static( map, width=1024 , height=600 )