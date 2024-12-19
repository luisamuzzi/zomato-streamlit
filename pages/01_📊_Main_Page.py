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
# Variáveis auxiliares
#==============================================
# Variável COUNTRIES - Contém o nome do país correspondente a cada código numérico e será usada na função que preencherá o nome dos países (country_name).
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

# Variável COLORS - Contém o nome correspondente a cada código de cor e será usada na função que preencherá o nome das cores (color_name).
COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
}

#==============================================
# Funções
#==============================================
# Função para renomear as colunas do dataframe:
def rename_columns(dataframe):
    """ Essa função tem a responsabilidade de renomear as colunas do dataframe trocando as letras maiúsculas por minúsculas
        e trocando espaços por underscore (_).
        
        Input: Dataframe
        Output: Dataframe
    
    """
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


# Função para preenchimento do nome dos países:
def country_name(country_id):
    """ Essa função tem a responsabilidade de preencher o nome dos países utilizando a variável auxiliar COUNTRIES.
        Aplicar em cada linha da coluna de código numérico dos países por meio do comando .apply().
    
    """
    return COUNTRIES[country_id]


# Função para criação da categoria do tipo de preço:
def create_price_type(price_range):
    """ Essa função tem a responsabilidade de preencher a categoria do tipo de preço dos restaurantes a partir da coluna de
        faixa de preço.
        Aplicar em cada linha da coluna de faixa de preço por meio do comando .apply().
    """    
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

    
# Função para criação do nome das cores:
def color_name(color_code):
    """ Essa função tem a responsabilidade de preencher o nome das cores utilizando a variável auxiliar COLORS.
        Aplicar em cada linha da coluna de código numérico das cores por meio do comando .apply().
    """
    return COLORS[color_code]


# Função para ajustar a ordem das colunas:
def adjust_columns_order(dataframe):
    """ Essa função tem a responsabilidade de ajustar a ordem das colunas do dataframe.
        
        Input: Dataframe
        Output: Dataframe
        
    """
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

# Função para limpar o dataframe:
def clean_dataframe(df):
    """ Essa função tem a responsabilidade de limpar e preprar o dataframe.
        
        Tipos de limpeza e preparação realizadas:
        1. Remoção de NA;
        2. Mudança do nome das colunas substituindo espaços por _ e letras maiúsculas por minúsculas;
        3. Remoção da coluna "switch_to_order_menu", que possui apenas um valor em todas as linhas;
        4. Criação de uma coluna com o nome dos países e remoção da coluna com o código dos países;
        5. Criação de uma coluna de tipo de preço;
        6. Criação de uma coluna com o nome das cores;
        7. Categorização dos restaurantes por somente um tipo de culinária;
        8. Eliminação de linhas duplicadas;
        9. Ajuste da ordem das colunas;
        10. Remoção de outliers;
        11. Reset do index.
        
        Input: Dataframe
        Output: Dataframe
        
    """
    
    # Eliminando NaN:
    df = df.dropna()

    # Renomear as colunas do dataframe:
    df = rename_columns(df)

    # Remoção da coluna "switch_to_order_menu" - possui apenas um valor em todas as linhas:
    df = df.drop(columns = ['switch_to_order_menu'])

    # Criação de uma coluna com o nome dos países e remoção da coluna 'country_code':
    df['country'] = df.loc[:, 'country_code'].apply(lambda x: country_name(x))
    df = df.drop(columns=['country_code'])

    # Criação de uma coluna da categoria do tipo de preço:
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
        
    return df

# Função para inserir métricas gerais:
def general_metrics(metrics):
    """ Essa função tem a responsabilidade de inserir as métricas gerais da empresa.
        
        Métricas inseridas:
        1. Total de restaurantes cadastrados;
        2. Total de países cadastrados;
        3. Total de cidades cadastradas;
        4. Total de avaliações feitas;
        5. Total de tipos de culinária.
        
        Input: Dataframe
        Output: None
        OBS: É necessário inserir a cópia do dataframe salva na variável metrics, para que as métricas não sejam afetadas pelo filtro.
    """

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
        
    return None

# Função para criar e inserir o mapa da localização dos restaurantes:
def restaurant_map(df):
    """ Essa função tem a responsabilidade de criar e inserir o mapa da localização dos restaurantes por meio da latitude e longitude.
        Além disso, também insere o nome, o custo médio para duas pessoas, o tipo de culinária e a média de avaliações de cada restaurante.
        
        Input: Dataframe
        Output: None
        
    """
    
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
    
    return None

# -------------------------------------------- Início da estrutura lógica do código ----------------------------------------------------------------

#==============================================
# Import dataset
#==============================================
df_original = pd.read_csv('dataset/zomato.csv')

#==============================================
# Limpeza e preparação dos dados
#==============================================
df = clean_dataframe(df_original)

# Criando cópia do dataframe para as métricas principais não se alterarem com os filtros:
metrics = df.copy()

#==============================================
# Configuração da largura da página
#==============================================
st.set_page_config(page_title='Main Page', page_icon='📊', layout="wide")

#==============================================
# Barra Lateral
#==============================================
# Logo:
image = Image.open('logo.png')

# Colunas para logo e nome da empresa:
with st.sidebar:

    col1, col2, col3 = st.columns([1,6,1])

    with col1:

        st.write("")

    with col2:

        st.image(image=image, use_column_width=True)

    with col3:

        st.write("")

    col1, col2, col3 = st.columns([1,6,1])

    with col1:

        st.write("")

    with col2:
        
        st.markdown('## Food Delivery & Dining')

    with col3:

        st.write("")
    
    st.markdown("""___""")
        
# Seletor de países:  
st.sidebar.markdown('## Filtros')

country_options = st.sidebar.multiselect('Escolha os países dos quais deseja visualizar restaurantes:', 
                                         list(df['country'].unique()), default=list(df['country'].unique()))

# Botão para download dos dados tratados:
dados_tratados = pd.read_csv('dataset/dados_tratados.csv', sep=';')

st.sidebar.markdown('## Dados tratados')

st.sidebar.download_button(label='Download',
                           data=dados_tratados.to_csv(index=False, sep=';'),
                           file_name='data.csv',
                           mime='text/csv')

# Filtro países:
linhas_selecionadas = df['country'].isin(country_options)
df = df.loc[linhas_selecionadas, :]

# Contato:
st.sidebar.markdown("### Feito por [Luísa Muzzi](https://luisamuzzi.github.io/portfolio_projetos/)")

#==============================================
# Layout no streamlit
#==============================================
st.title('Zomato')

st.markdown('## O melhor lugar para encontrar seu mais novo restaurante favorito!')

st.markdown('### Temos as seguintes marcas dentro da nossa plataforma:')

# Inserindo métricas gerais:
general_metrics(metrics)
    
# Inserindo mapa:
with st.container():
    
    restaurant_map(df)

