# Bibliotecas
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------

# Bibliotecas necessárias
import pandas as pd
import numpy as np
import streamlit as st
from datetime import date
import folium
from PIL import Image

from streamlit_folium import folium_static

st.set_page_config(
    page_title='Visão Restaurante - Breeze Company',
    page_icon='🍔',
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

st.header('Marketplace - Visão Restaurantes')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    st.subheader( 'Métricas Gerais' )
    with st.container():

        col1, col2, col3 = st.columns(3)
        with col1:
            deliver_unique = df1['Delivery_person_ID'].nunique()
            col1.metric( 'Entregadores Únicos', deliver_unique)
        with col2:
            df_aux = (df1.groupby('Festival')['Time_taken(min)']
                         .agg(['mean', 'std']))
            
            df_aux.columns= ['avg_time', 'std_time']

            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            col2.metric( 'Tempo Médio de Entrega c/ Festival', df_aux)
        with col3:
            df_aux = (df1.groupby('Festival')['Time_taken(min)']
                         .agg(['mean', 'std']))
            
            df_aux.columns= ['avg_time', 'std_time']

            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            col3.metric( 'Desvio Padrão de Entrega c/ Festival', df_aux)

        col4, col5, col6 = st.columns(3)
                                    
        with col4:
            cols = ['Restaurant_latitude', 'Restaurant_longitude',
         'Delivery_location_latitude', 'Delivery_location_longitude']

            df1['distance'] = df1.loc[:, cols].apply( lambda x:
                                               haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                               (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), 
                                               axis=1)
            
            avg_distance = np.round( df1['distance'].mean(), 2 )
            col1.metric('Distância Média das Entregas (Km)', avg_distance)
        
        with col5:
            df_aux = (df1.groupby('Festival')['Time_taken(min)']
                         .agg(['mean', 'std']))
            
            df_aux.columns= ['avg_time', 'std_time']

            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            col2.metric( 'Tempo Médio de Entrega s/ Festival', df_aux)

        with col6:
            df_aux = (df1.groupby('Festival')['Time_taken(min)']
                         .agg(['mean', 'std']))
            
            df_aux.columns= ['avg_time', 'std_time']

            df_aux = df_aux.reset_index()
            
            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            col3.metric( 'Desvio Padrão de Entrega s/ Festival', df_aux)

    with st.container():
        st.markdown("""---""")
        st.subheader( 'Tempo médio de entrega por cidade e tipo de pedido' )

        col1, col2 = st.columns(2)

        with col1:
            cols = ['City', 'Time_taken(min)']
            df_aux = df1.loc[:, cols].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = go.Figure()
            fig.add_trace( go.Bar( name='Control',
                        x=df_aux['City'],
                        y=df_aux['avg_time'],
                        error_y=dict( type='data', array=df_aux['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)

        with col2:
            df_aux = (df1.groupby(['City', 'Type_of_order'])['Time_taken(min)']
                         .agg(['mean', 'std']))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux.reset_index()
            st.dataframe(df_aux)
    
    with st.container():
        st.markdown("""---""")
        st.subheader( 'Distribuição do tempo por cidade e tipo de tráfego' )
        st.markdown( "#### Distancia média das entregas por cidade")

    with st.container():
                    
            cols = ['Restaurant_latitude', 'Restaurant_longitude',
            'Delivery_location_latitude', 'Delivery_location_longitude']

            df1['distance'] = df1.loc[:, cols].apply( lambda x:
                                    haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                               (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), 
                                               axis=1 )

            avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()

            fig = go.Figure( data=[ go.Pie( labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
            st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
            st.markdown("#### Desvio padrão por tipo de cidade e densidade de tráfego")       
            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            df_aux = (df1.loc[:, cols]
                         .groupby( ['City', 'Road_traffic_density'])
                         .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                  color='std_time', color_continuous_scale='RdBu',
                  color_continuous_midpoint=np.average(df_aux['std_time']))
            st.plotly_chart(fig)
