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

# Variável color_country - Contém cores para serem associadas a cada país para os funções que plotam os gráficos da Visão Cidades
# (restaurants_per_city, restaurants_per_rating, cuisines_per_city).
color_country = {
    'India': '#ff4b4b',
    'United Kingdom': '#e19990',
    'United States of America': '#798897',
    'Indonesia': '#8bade1',
    'New Zeland': '#39608f',
    'Turkey': '#57423f',
    'Brazil': '#79aef3',
    'Australia': '#ffe5de',
    'Philippines': '#639d00',
    'Canada': '#2a6900',
    'Singapure': '#6B5695',
    'United Arab Emirates': '#0095ff',
    'Qatar': '#9c70ff',
    'Sri Lanka': '#ff95bc',
    'South Africa': '#f55b00'
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

# Função para plotar o gráfico da quantidade de restaurantes registrados por cidade:
def restaurants_per_city(df):
    """ Essa função tem a responsabilidade de plotar o gráfico de baaras do número de restaurantes (y) por cidade (x), mostrando a qual país pertence cada
        cidade.
        São utilizadas as colunas 'country', 'city' e 'restaurant_id', agrupando por 'country' e 'city' e contando a coluna 'restaurant_id'.
        Utiliza também a variável auxiliar color_country para definir as cores das barras.
        Plota as 10 primeiras cidades.
        
        Input: Dataframe
        Output: fig (o gráfico gerado)
        OBS: A função não exibe o gráfico, é preciso um comando separado para isso. 
    """
    df_aux = (df.loc[:, ['country','city', 'restaurant_id']].groupby(['country','city'])
                                                     .count()
                                                     .sort_values(['restaurant_id', 'city'], ascending=[False, True])
                                                     .reset_index())

    fig = px.bar(df_aux.head(10), x='city', y ='restaurant_id', color='country', text='restaurant_id', 
    labels={'city': 'Cidade',
    'restaurant_id': 'Quantidade de restaurantes',
    'country': 'País'}, category_orders={'city': df_aux['city']}, color_discrete_map=color_country)
    fig.update_traces(textposition='outside')
    fig.update_layout(height=550)

    return fig

# Função para plotar o gráfico da quantidade de restaurantes a partir do valor da média de avaliação:
def restaurants_per_rating(df, rating):
    """ Essa função tem a responsabilidade de plotar o gráfico de barras do número de restaurantes com média de avaliação acima de 4 (y) por cidade (x)
        OU o gráfico de barras do número de restaurantes com média de avaliação abaixo de 2.5 (y) por cidade (x).
        Plota as 10 primeiras cidades.
        
        Input: 
            - df: dataframe com dados necessários para o cálculo
            - rating: a nota da avaliação que determinará qual dos dois gráficos será pplotado.
                4: rating=4 calcula a quantidade de restaurantes com média de avaliação ACIMA DE 4 (> 4)
                2: rating=2.5 calcula a quantidade de restaurantes com média de avaliação ABAIXO DE 2.5 (< 2.5)
        Output: fig (o gráfico gerado)
    OBS: A função não exibe o gráfico, é preciso um comando separado para isso. 
    """

    if rating == 4:

        df_aux = (df.loc[df['aggregate_rating'] > rating, ['aggregate_rating', 'city', 'country']]
                    .groupby(['country', 'city'])
                    .count()
                    .sort_values(['aggregate_rating', 'city'], ascending=[False, True])
                    .reset_index())

        fig = px.bar(df_aux.head(10), x='city', y='aggregate_rating', color='country', text='aggregate_rating', 
        labels={'city': 'Cidade',
                'aggregate_rating': 'Quantidade de restaurantes',
                'country': 'País'}, category_orders={'city': df_aux['city']}, color_discrete_map=color_country)

        fig.update_traces(textposition='outside')
        fig.update_layout(height=550)

        return fig

    elif rating == 2.5:

        df_aux = (df.loc[df['aggregate_rating'] < rating, ['aggregate_rating', 'city', 'country']]
        .groupby(['country', 'city'])
        .count()
        .sort_values(['aggregate_rating', 'city'], ascending=[False, True]) 
        .reset_index())

        fig = px.bar(df_aux.head(10), x='city', y='aggregate_rating', color='country', text='aggregate_rating', 
        labels={'city': 'Cidade',
                'aggregate_rating': 'Quantidade de restaurantes',
                'country': 'País'}, category_orders={'city': df_aux['city']}, color_discrete_map=color_country)

        fig.update_traces(textposition='outside')
        fig.update_layout(height=550)

        return fig

# Função para plotar o gráfico do número de tipos culinários por cidade:
def cuisines_per_city(df):
    """ Essa função tem a responsabilidade de plotar o gráfico de barras do número de tipos culinários (y) por cidade (x), mostrando a qual país pertence cada
    cidade.
    São utilizadas as colunas 'country', 'city' e 'cuisines', agrupando por 'country' e 'city' e contando os valores únicos da coluna 'cuisines'.
    Utiliza também a variável auxiliar color_country para definir as cores das barras.
    Plota as 10 primeiras cidades.
    
    Input: Dataframe
    Output: fig (o gráfico gerado)
    OBS: A função não exibe o gráfico, é preciso um comando separado para isso. 
    """
    df_aux = (df.loc[:, ['city', 'cuisines', 'country']]
                .groupby(['country', 'city'])
                .nunique()
                .sort_values(['cuisines', 'city'], ascending=[False, True])
                .reset_index())

    fig = px.bar(df_aux.head(10), x='city', y='cuisines', color='country', text='cuisines', 
    labels={'city': 'Cidade',
            'cuisines': 'Quantidade de tipos culinários únicos',
            'country': 'País'},  category_orders={'city': df_aux['city']}, color_discrete_map=color_country)

    fig.update_traces(textposition='outside')
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
st.set_page_config(page_title='Cities', page_icon='🏙️', layout="wide")

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
st.title('🏙️ Visão Cidades')

with st.container():
    
    st.markdown('#### Top 10 cidades com mais restaurantes na base de dados')
    
    # Quantidade de restaurantes registrados por cidade (exibe os 10 primeiros):
        
    fig = restaurants_per_city(df)
    
    st.plotly_chart(fig, use_container_width=True)
    
with st.container():
    
    col1, col2 = st.columns(2)
    
    with col1:
        
        st.markdown('#### Top 10 cidades com restaurantes com média de avaliação acima de 4')
        
        # Quantidade de restaurantes por cidade com média de avaliação acima de 4 (exibe os 10 primeiros):
                
        fig = restaurants_per_rating(df, rating=4)
        
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        
        st.markdown('#### Top 10 cidades com restaurantes com média de avaliação abaixo de 2,5')
        
        # Quantidade de restaurantes por cidade com média de avaliação abaixo de 2,5 (exibe os 10 primeiros):
                
        fig = restaurants_per_rating(df, rating=2.5)
        
        st.plotly_chart(fig, use_container_width=True)

with st.container():
    
    st.markdown('#### Top 10 cidades com restaurates com o maior número de tipos de culinária distintos')
    
    # Encontrar a quantidade de tipos únicos de culinária por cidade.
   
    fig = cuisines_per_city(df)
    
    st.plotly_chart(fig, use_container_width=True)