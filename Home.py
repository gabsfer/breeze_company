import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home - Breeze Company",
    page_icon="📊",
    layout='centered',
)

image = Image.open( 'brze.png' )
st.sidebar.image(image,  width=150)

st.sidebar.header( 'Breeze Company')
st.sidebar.subheader( 'Clique, Peça, Repita ')
st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Gabe')

st.markdown( "## 📊 Breeze Company Growth Dashboard")

st.markdown(
    """
    O Growth Dashboard foi construído para o acompanhamento das métricas de crescimento dos Entregadores e dos Restaurantes.
    """
)
st.markdown("")

st.markdown(
    """
    ### Como utilizar este Dashboard:
    """
)

st.markdown('')

st.markdown(
    """
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    """
)

st.markdown('')

st.markdown(
    """
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    """
)   

st.markdown('')

st.markdown(
    """
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
    """
)