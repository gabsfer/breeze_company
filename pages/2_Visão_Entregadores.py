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
    page_title='Visão Entregadores - Breeze Company',
    page_icon='🛵',
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

st.header('Marketplace - Visão Entregadores')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():

        st.subheader( 'Métricas Gerais' )
        col1, col2, col3, col4 = st.columns( 4, gap='large' )

        with col1:
            maior_idade = df1['Delivery_person_Age'].max()
            col1.metric( 'Maior idade dos entregadores', maior_idade )

        with col2:
            menor_idade = df1['Delivery_person_Age'].min()
            col2.metric( 'Menor idade dos entregadores', menor_idade )

        with col3:
            melhor_condicao = df1['Vehicle_condition'].max()
            col3.metric( 'Melhor condição de veículo', melhor_condicao )

        with  col4:
            pior_condicao = df1['Vehicle_condition'].min()
            col4.metric( 'Pior condição de veículo', pior_condicao)

    with st.container():

        st.markdown("""---""")
        st.subheader( 'Avaliações' )

        col1, col2 = st.columns([2, 2])

        with col1:
            st.markdown( '##### Avaliação média por entregador' )
            df_avg_ratings_by_deliver = (df1.groupby('Delivery_person_ID')['Delivery_person_Ratings']
                                            .mean()
                                            .reset_index())
            st.dataframe( df_avg_ratings_by_deliver, use_container_width=True, height=495 )

        with col2:
            st.markdown( '##### Avaliação média por trânsito' )
            # ----- Seleção de Linhas -----
            df_avg_std_rating_by_traffic = (df1.groupby('Road_traffic_density')['Delivery_person_Ratings']
                                               .agg(['mean', 'std']))

            # ----- Renomeando as colunas mean e std -----
            df_avg_std_rating_by_traffic.columns=['delivery_mean', 'delivery_std']

            # ----- Reset do index -----
            df_avg_std_rating_by_traffic.reset_index()
            st.dataframe( df_avg_std_rating_by_traffic, use_container_width=True )

            st.markdown( '##### Avaliação média por clima' )
            # ----- Seleção de Linhas -----
            df_avg_std_rating_by_weather = (df1.groupby('Weatherconditions')['Delivery_person_Ratings']
                                .agg(['mean', 'std']))
            # ----- Renomeando as colunas mean e std -----
            df_avg_std_rating_by_weather.columns = ['weather_mean', 'weather_std']

            # ----- Reset do index -----
            df_avg_std_rating_by_weather.reset_index()
            st.dataframe( df_avg_std_rating_by_weather, use_container_width=True )

    with st.container():

        st.markdown("""---""")
        st.subheader( 'Velocidade de Entrega' )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown( '#### Entregadores mais rápidos por cidade' )
            # ----- Seleção de Linhas -----
            df2 = (df1.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
                      .min()
                      .reset_index()
                      .sort_values(['City', 'Time_taken(min)'],ascending= True))

            # ----- Filtrando os 10 por cidade -----
            df_aux01 = df2.loc[df2['City'] == 'Metropolitian'].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban'].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban'].head(10)

            df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index(drop=True)
            st.dataframe( df3 )

        with col2:
            
            st.markdown( '#### Entregadores mais lentos por cidade' )
            # ----- Seleção de Linhas -----
            df2 = (df1.groupby(['City', 'Delivery_person_ID'])['Time_taken(min)']
                      .max()
                      .reset_index()
                      .sort_values(['City', 'Time_taken(min)'], ascending= False))

            # ----- Selecionando os 10 por cidade -----
            df_aux01 = df2.loc[df2['City'] == 'Metropolitian'].head(10)
            df_aux02 = df2.loc[df2['City'] == 'Urban'].head(10)
            df_aux03 = df2.loc[df2['City'] == 'Semi-Urban'].head(10)

            df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
            st.dataframe( df3 )