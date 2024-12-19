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

# Função para exibir as métricas dos melhores restaurantes por tipo culinário de acordo com a média de avaliações:
def best_per_cuisine(metrics, cuisine, col):
    """ Essa função tem a responsabilidade de calcular o melhor restaurante do tipo de culinária inserido de acordo com a média de avaliações.
        Deve ser inserido o dataframe metrics, pois ele é uma cópia do dataframe df desvinculada dos filtros.
        
        Input:
            - metrics: dataframe chamado metrics
            - cuisine: tipo de culinária
                cuisine='Italian'
                cuisine='American'
                cuisine='Arabian'
                cuisine='Japanese'
                cuisine='Home-made'
            - col: coluna na qual deve ser inserida a métrica
                col=col1 para 'Italian'
                col=col2 para 'American'
                col=col3 para 'Arabian'
                col=col4 para 'Japanese'
                col=col5 para 'Home-made'
        Output: None
    
    """
    metric = (metrics.loc[metrics['cuisines'] == cuisine, ['restaurant_id', 'restaurant_name', 'aggregate_rating', 'cuisines', 'city', 
                                   'country', 'average_cost_for_two', 'votes', 'currency']]
                     .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True])
                     .reset_index(drop=True))

    col.metric(label=f'{metric.iloc[0,3]}: {metric.iloc[0,1]}', 
                value=f'{metric.iloc[0,2]}/5.0',
                help=f"""
                País: {metric.iloc[0,5]}

                Cidade: {metric.iloc[0,4]}

                Média de prato para dois: {metric.iloc[0,6]} {metric.iloc[0,8]}

                """)

    return None

#  Função para plotar o gráfico dos melhores ou dos piores tipos de culinária:
def top_cuisines(df, ascending):
    """ Essa função tem a responsabilidade de plotar um gráfico de barras dos melhores restaurantes OU dos piores restaurantes por tipo culinário.
        Utiliza as colunas 'cuisines' e 'aggregate_rating', agrupando por 'cuisines' e calculando a média de 'aggregate_rating'.
        Plota o top tipos culinários de acordo com o selecionado no filtro de número de informações.
        
        Input:
            - df: dataframe com dados necessários para o cálculo
            - ascending: ordenação dos dados
                ascending=True: top piores tipos culinários
                ascending=False: top melhores tipos culinários
        Output: fig (o gráfico gerado)
        OBS: A função não exibe o gráfico, é preciso um comando separado para isso.               
    """

    df_aux = (df.loc[:, ['cuisines', 'aggregate_rating']]
                .groupby('cuisines')
                .mean('aggregate_rating')
                .sort_values('aggregate_rating', ascending=ascending)
                .reset_index())

    fig = px.bar(df_aux.head(info_options), x='cuisines', y='aggregate_rating', text='aggregate_rating', text_auto='.2f' , 
                 labels={'cuisines': 'Tipos de culinária',
                 'aggregate_rating': 'Média da avaliação média'})

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
st.set_page_config(page_title='Cuisines', page_icon='🍽️', layout="wide")

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

st.sidebar.markdown("""___""")

# Seletor de quantidade de informações a serem visualizadas:
info_options = st.sidebar.slider(label='Selecione a quantidade de informações que deseja visualizar:',
                                 value=20,
                                 min_value=0,
                                 max_value=20)

st.sidebar.markdown("""___""")

# Seletor de tipos de culinária:
cuisine_options = st.sidebar.multiselect('Escolha os tipos de culinária:',
                                         list(df['cuisines'].unique()), default=list(df['cuisines'].unique()))

# Filtro países:
linhas_selecionadas = df['country'].isin(country_options)
df = df.loc[linhas_selecionadas, :]

# Filtro de quantidade de informações:

# Filtro de tipos de culinária:
linhas_selecionadas = df['cuisines'].isin(cuisine_options)
df = df.loc[linhas_selecionadas, :]

# Contato:
st.sidebar.markdown("### Feito por [Luísa Muzzi](https://luisamuzzi.github.io/portfolio_projetos/)")

#==============================================
# Layout no streamlit
#==============================================
st.title('🍽️ Visão Tipos de Culinária')

with st.container():
    
    st.markdown('## Melhores restaurantes dos principais tipos culinários')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Restaurante de culinária italiana com a maior média de avaliação:
        
        best_per_cuisine(metrics, cuisine='Italian', col=col1)
        
    with col2:
        # Restaurante de culinária americana com a maior média de avaliação:
        
        best_per_cuisine(metrics, cuisine='American', col=col2)
    
    with col3:
        # Restaurante de culinária árabe com a maior média de avaliação:
                
        best_per_cuisine(metrics, cuisine='Arabian', col=col3)
                   
    with col4:
        # Restaurante de culinária japonesa com a maior média de avaliação:
        
        best_per_cuisine(metrics, cuisine='Japanese', col=col4)
        
    with col5:
        # Restaurante de culinária caseira com a maior média de avaliação:
        
        best_per_cuisine(metrics, cuisine='Home-made',col=col5)

with st.container():
    
    # Top restaurantes de acordo com a média de avaliação:
    
    st.markdown(f'## Top {info_options} restaurantes')
    
    top_restaurantes = (df.loc[:, ['restaurant_id', 'restaurant_name', 'city','country', 'cuisines', 'average_cost_for_two','aggregate_rating', 'votes']]
                          .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True]))
    
    st.dataframe(top_restaurantes.head(info_options), use_container_width=True)
    
with st.container():
    
    col1, col2 = st.columns(2)
    
    with col1:
        
        # Top melhores tipos de culinária de acordo com a média de avaliação:
        
        st.markdown(f'## Top {info_options} melhores tipos de culinária')
        
        fig = top_cuisines(df, ascending=False)
        
        st.plotly_chart(fig, use_container_width=True)
        
        
    with col2:
        
        # Top piores tipos de culinária de acordo com a média de avaliação:
        
        st.markdown(f'## Top {info_options} piores tipos de culinária')
        
        fig = top_cuisines(df, ascending=True)
        
        st.plotly_chart(fig, use_container_width=True)