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

# Função para plotar o gráfico do número de restaurantes registrados por país:
def restaurants_per_country(df):
    """ Essa função tem como responsabilidade plotar um gráfico de barras com o número de restaurantes (y) por país (x).
        Utiliza as colunas 'country' e 'restaurant_id', agrupando por 'country' e realizando a contagem de 'restaurant_id'.
        
        Input: Dataframe
        Output: fig (o gráfico gerado)
        OBS: A função não exibe o gráfico, é preciso um comando separado para isso.
    """

    df_aux = (df.loc[:, ['country', 'restaurant_id']].groupby('country')
                                                  .count()
                                                  .sort_values('restaurant_id', ascending=False)
                                                  .reset_index())

    fig = px.bar(df_aux, x='country', y='restaurant_id', text='restaurant_id', category_orders={'restaurant_id': df_aux['restaurant_id']}, 
       labels={'country' : 'País', 'restaurant_id': 'Quantidade de restaurantes'})

    fig.update_traces(marker_color='#ff4b4b', textposition='outside')
    fig.update_layout(height=550)

    return fig

# Função para plotar o gráfico de número de cidades registradas por país:
def cities_per_country(df):
    """ Essa função tem por responsabilidade plotar o gráfico de barras do número de cidades (y) por país (x).
        Utiliza as colunas 'country' e 'city', agrupando por 'country' e obtendo o número de cidades únicas.
        
        Input: Dataframe
        Output: fig (o gráfico gerado)
        OBS: A função não exibe o gráfico, é preciso um comando separado para isso.
    """

    df_aux = (df.loc[:, ['country','city']].groupby('country')
                                        .nunique()
                                        .sort_values('city', ascending=False)
                                        .reset_index())

    fig = px.bar(df_aux, x='country', y ='city', text='city', category_orders={'city': df_aux['city']}, 
       labels={'country': 'País',
        'city': 'Quantidade de cidades'})

    fig.update_traces(marker_color='#ff4b4b', textposition='outside')
    fig.update_layout(height=550)

    return fig

# Função para plotar o gráfico da média de avaliações por país:
def avg_ratings_per_country(df):
    """ Essa função tem a responsabilidade de plotar um gráfico de barras da média de avaliações (y) por país (x).
        Utiliza as colunas 'country' e 'votes', agrupando por 'country' e calculando a média de 'votes'.
        
        Input: Dataframe
        Output: fig (o gráfico gerado)
        OBS: A função não exibe o gráfico, é preciso um comando separado para isso.
    """

    df_aux = (df.loc[:, ['votes', 'country']].groupby('country')
                                      .mean()
                                      .sort_values('votes', ascending=False)
                                      .reset_index())

    fig = px.bar(df_aux, x='country', y='votes', text='votes', text_auto='.2f', category_orders={'votes': df_aux['votes']}, 
    labels={'country': 'País',
    'votes': 'Quantidade de avaliações'})

    fig.update_traces(marker_color='#ff4b4b', textposition='outside')
    fig.update_layout(height=550)

    return fig

# Função para plotar o gráfico da média de preço do prato para duas pessoas por país:
def avg_price_for_two (df):
    """ Essa função tem a responsabilidade de plotar um gráfico de barras da média de preço para duas pessoas (y) por país (x).
        Utiliza as colunas 'country' e 'average_cost_for_two', agrupando por 'country' e calculando a média de 'average_cost_for_two'.
        
        Input: Dataframe
        Output: fig (o gráfico gerado)
        OBS: A função não exibe o gráfico, é preciso um comando separado para isso.
    """

    df_aux = (df.loc[:, ['country', 'average_cost_for_two']].groupby('country')
                                                     .mean()
                                                     .sort_values('average_cost_for_two', ascending=False)
                                                     .reset_index())

    fig = px.bar(df_aux, x='country', y='average_cost_for_two', text='average_cost_for_two', text_auto='.2f',
    category_orders={'average_cost_for_two': df_aux['average_cost_for_two']}, 
    labels={'country': 'País',
    'average_cost_for_two': 'Preço do prato para duas pessoas'})

    fig.update_traces(marker_color='#ff4b4b', textposition='outside')
    fig.update_layout(height=550)

    return fig

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
st.set_page_config(page_title='Countries', page_icon='🌎', layout="wide")

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

# Filtro países:
linhas_selecionadas = df['country'].isin(country_options)
df = df.loc[linhas_selecionadas, :]

# Contato:
st.sidebar.markdown("### Feito por [Luísa Muzzi](https://luisamuzzi.github.io/portfolio_projetos/)")

#==============================================
# Layout no streamlit
#==============================================
st.title('🌎 Visão Países')

with st.container():
    
    # Número de restaurantes registrados por país:
  
    st.markdown('#### Quantidade de restaurantes registrados por país')
    
    fig = restaurants_per_country(df)
    
    st.plotly_chart(fig, use_container_width=True)
    
with st.container():
    
    # Número de cidades registradas por país:
    
    st.markdown('#### Quantidade de cidades registradas por país')
   
    fig = cities_per_country(df)
    
    st.plotly_chart(fig, use_container_width=True)
    
with st.container():
    
    col1, col2 = st.columns(2)
    
    with col1:
        
        # Média de avaliações por país:
        
        st.markdown('#### Média de avaliações feitas por país')
               
        fig = avg_ratings_per_country(df)
        
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        
        # Média de preço para duas pessoas:
        
        st.markdown('#### Média de preço de um prato para duas pessoas por país')
                
        fig = avg_price_for_two (df)
        
        st.plotly_chart(fig, use_container_width=True)