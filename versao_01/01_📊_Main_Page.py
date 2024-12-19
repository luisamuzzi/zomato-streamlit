#==============================================
# Libraries
#==============================================
import pandas as pd
import inflection
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from haversine import haversine
import streamlit as st
from streamlit_folium import folium_static
from PIL import Image

#==============================================
# Funções
#==============================================
# Renomear as colunas do dataframe:
def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    
    return df


# Preenchimento do nome dos países:
COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "United Kingdom",
    216: "United States of America",
}

def country_name(country_id):
    return COUNTRIES[country_id]


# Criação da categoria do tipo de comida:
def create_price_type(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

    
#Criação do nome das cores:
COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}

def color_name(color_code):
    return COLORS[color_code]


# Ajustando a ordem das colunas:
def adjust_columns_order(dataframe):
    df = dataframe.copy()

    new_cols_order = [
        "restaurant_id",
        "restaurant_name",
        "country",
        "city",
        "address",
        "locality",
        "locality_verbose",
        "longitude",
        "latitude",
        "cuisines",
        "price_range",
        "price_type",
        "average_cost_for_two",
        "currency",
        "has_table_booking",
        "has_online_delivery",
        "is_delivering_now",
        "aggregate_rating",
        "rating_color",
        "color_name",
        "rating_text",
        "votes",
    ]

    return df.loc[:, new_cols_order]

# -------------------------------------------- Início da estrutura lógica do código ----------------------------------------------------------------

#==============================================
# Import dataset
#==============================================
df_original = pd.read_csv('C:/Users/Luísa/Documents/repos/ftc_programacao_python/projeto_final/dataset/zomato.csv')

#==============================================
# Limpeza dos dados
#==============================================
df = df_original.copy()

# Eliminando NaN:
df = df.dropna()

# Renomear as colunas do dataframe:

df = rename_columns(df)

# Remoção da coluna "switch_to_order_menu" - possui apenas um valor em todas as linhas:

df = df.drop(columns = ['switch_to_order_menu'])

# Criação de uma coluna com o nome dos países e remoção da coluna 'country_code':

df['country'] = df.loc[:, 'country_code'].apply(lambda x: country_name(x))

df = df.drop(columns=['country_code'])

# Criação de uma coluna da categoria do tipo de comida:

df['price_type'] = df.loc[:, 'price_range'].apply(lambda x: create_price_type(x))


# Criação de uma coluna com o nome das cores:

df['color_name'] = df.loc[:, 'rating_color'].apply(lambda x: color_name(x))

# Categorização dos restaurantes por somente um tipo de culinária:

df['cuisines'] = df.loc[:, 'cuisines'].apply(lambda x: x.split(',')[0])

# Eliminando linhas duplicadas:

df = df.drop_duplicates()

# Ajustando a ordem das colunas:

df = adjust_columns_order(df)

# Removendo outliers:

df = df.loc[df['average_cost_for_two'] != 25000017, :]

# Resetando o index:
df = df.reset_index(drop=True)

# Criando cópia do dataframe para as métricas principais não se alterarem com os filtros:
metrics = df.copy()

#==============================================
# Configuração da largura da página
#==============================================
st.set_page_config(page_title = 'Main Page', page_icon = '📊', layout = "wide")

#==============================================
# Barra Lateral
#==============================================

# Logo:
image = Image.open('C:/Users/Luísa/Documents/repos/ftc_programacao_python/projeto_final/logo.png')

# Colunas para logo e nome da empresa:
with st.sidebar:
    
    col1, col2 = st.columns(2)

    with col1:

        st.image(image=image, use_column_width=True)
    
    with col2:
        
        st.markdown('')
        st.markdown('')
        st.markdown('# Fome Zero')
        
    st.markdown("""___""")
    
# Seletor de países:  
st.sidebar.markdown('## Filtros')
    
country_options = st.sidebar.multiselect('Escolha os países dos quais deseja visualizar restaurantes:', 
                                         list(df['country'].unique()), default=list(df['country'].unique()))

# Botão para download dos dados tratados:
dados_tratados = pd.read_csv('C:/Users/Luísa/Documents/repos/ftc_programacao_python/projeto_final/dataset/dados_tratados.csv', sep=';')

st.sidebar.markdown('# Dados tratados')

st.sidebar.download_button(label='Download',
                           data=dados_tratados.to_csv(index=False, sep=';'),
                           file_name='data.csv',
                           mime='text/csv')

# Filtro países:
linhas_selecionadas = df['country'].isin(country_options)
df = df.loc[linhas_selecionadas, :]

#==============================================
# Layout no streamlit
#==============================================
st.title('Fome Zero!')

st.markdown('## O Melhor lugar para encontrar seu mais novo restaurante favorito!')

st.markdown('### Temos as seguintes marcas dentro da nossa plataforma:')

# Inserindo métricas gerais:
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    
    # Total de restaurantes cadastrados: 
    restaurantes_cadastrados = metrics['restaurant_id'].nunique()
    
    col1.metric('Restaurantes cadastrados', restaurantes_cadastrados)

with col2:
    
    # Total de países cadastrados:
    paises_cadastrados = metrics['country'].nunique()
    
    col2.metric('Países cadastrados', paises_cadastrados)

with col3:
    
    # Total de cidades cadastradas:
    cidades_cadastradas= metrics['city'].nunique()
    
    col3.metric('Cidades cadastradas', cidades_cadastradas)
    
with col4:
    
    # Total de avaliações feitas:
    total_avaliacoes = metrics['votes'].sum()
    
    col4.metric('Avaliações feitas na plataforma', f'{total_avaliacoes:,}'.replace(',', '.'))
    
with col5:
    
    # Total de tipos de culinária:
    total_cuisines = metrics['cuisines'].nunique()
    
    col5.metric('Tipos de culinária oferecidos', total_cuisines)
    
# Inserindo mapa:
with st.container():
    
    df_aux = df.loc[:, ['latitude', 'longitude', 'restaurant_name', 'cuisines', 'average_cost_for_two', 'currency','aggregate_rating', 'color_name']]

    map = folium.Map()

    marker_cluster = MarkerCluster().add_to(map)

    for index, info in df_aux.iterrows():

        popup = folium.Popup(f""" <p><strong>{info['restaurant_name']}</strong></p>
        Preço: {info['average_cost_for_two']},00 {info['currency']} para dois<br>
        Cuisine: {info['cuisines']}<br>
        Aggregate rating: {info['aggregate_rating']}/5.0 
               """,
        max_width=500,
        )
        
        folium.Marker(location=[info['latitude'], info['longitude']],
                    icon=folium.Icon(icon='glyphicon glyphicon-cutlery', color=info['color_name']),
                    popup=popup).add_to(marker_cluster)
        
    folium_static(map, width = 1024, height = 600)