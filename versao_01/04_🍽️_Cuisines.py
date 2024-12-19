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
st.set_page_config(page_title = 'Cuisines', page_icon = '🍽️', layout = "wide")

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

#==============================================
# Layout no streamlit
#==============================================
st.title('🍽️ Visão Tipos de Culinária')

with st.container():
    
    st.markdown('## Melhores restaurantes dos principais tipos culinários')
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Restaurante de culinária italiana com a maior média de avaliação:
        
        metric = (metrics.loc[metrics['cuisines'] == 'Italian', ['restaurant_id', 'restaurant_name', 'aggregate_rating', 'cuisines', 'city', 
                                      'country', 'average_cost_for_two', 'votes', 'currency']]
                         .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True])
                         .reset_index(drop=True))
        
        col1.metric(label=f'{metric.iloc[0,3]}: {metric.iloc[0,1]}', 
                    value=f'{metric.iloc[0,2]}/5.0',
                    help=f"""
                    País: {metric.iloc[0,5]}
                    
                    Cidade: {metric.iloc[0,4]}
                    
                    Média de prato para dois: {metric.iloc[0,6]} {metric.iloc[0,8]}
                    
                    """)
        
    with col2:
        # Restaurante de culinária americana com a maior média de avaliação:
        
        metric = (metrics.loc[metrics['cuisines'] == 'American', ['restaurant_id', 'restaurant_name', 'aggregate_rating', 'cuisines', 'city', 
                                       'country', 'average_cost_for_two', 'votes', 'currency']]
                         .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True])
                         .reset_index(drop=True))
        
        col2.metric(label=f'{metric.iloc[0,3]}: {metric.iloc[0,1]}', 
                    value=f'{metric.iloc[0,2]}/5.0',
                    help=f"""
                    País: {metric.iloc[0,5]}
                    
                    Cidade: {metric.iloc[0,4]}
                    
                    Média de prato para dois: {metric.iloc[0,6]} {metric.iloc[0,8]}
                    
                    """)
    
    with col3:
        # Restaurante de culinária árabe com a maior média de avaliação:
        
        metric = (metrics.loc[metrics['cuisines'] == 'Arabian', ['restaurant_id', 'restaurant_name', 'aggregate_rating', 'cuisines', 'city', 
                                       'country', 'average_cost_for_two', 'votes', 'currency']]
                         .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True])
                         .reset_index(drop=True))
        
        col3.metric(label=f'{metric.iloc[0,3]}: {metric.iloc[0,1]}', 
                    value=f'{metric.iloc[0,2]}/5.0',
                    help=f"""
                    País: {metric.iloc[0,5]}
                    
                    Cidade: {metric.iloc[0,4]}
                    
                    Média de prato para dois: {metric.iloc[0,6]} {metric.iloc[0,8]}
                    
                    """)
        
    with col4:
        # Restaurante de culinária japonesa com a maior média de avaliação:
        
        metric = (metrics.loc[metrics['cuisines'] == 'Japanese', ['restaurant_id', 'restaurant_name', 'aggregate_rating', 'cuisines', 'city', 
                                       'country', 'average_cost_for_two', 'votes', 'currency']]
                         .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True])
                         .reset_index(drop=True))
        
        col4.metric(label=f'{metric.iloc[0,3]}: {metric.iloc[0,1]}', 
                    value=f'{metric.iloc[0,2]}/5.0',
                    help=f"""
                    País: {metric.iloc[0,5]}
                    
                    Cidade: {metric.iloc[0,4]}
                    
                    Média de prato para dois: {metric.iloc[0,6]} {metric.iloc[0,8]}
                    
                    """)
        
    with col5:
        # Restaurante de culinária japonesa com a maior média de avaliação:
        
        metric = (metrics.loc[metrics['cuisines'] == 'Home-made', ['restaurant_id', 'restaurant_name', 'aggregate_rating', 'cuisines', 'city', 
                                       'country', 'average_cost_for_two', 'votes', 'currency']]
                         .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True])
                         .reset_index(drop=True))
        
        col5.metric(label=f'{metric.iloc[0,3]}: {metric.iloc[0,1]}', 
                    value=f'{metric.iloc[0,2]}/5.0',
                    help=f"""
                    País: {metric.iloc[0,5]}
                    
                    Cidade: {metric.iloc[0,4]}
                    
                    Média de prato para dois: {metric.iloc[0,6]} {metric.iloc[0,8]}
                    
                    """)

with st.container():
    
    st.markdown(f'## Top {info_options} restaurantes')
    
    top_restaurantes = (df.loc[:, ['restaurant_id', 'restaurant_name', 'city','country', 'cuisines', 'average_cost_for_two','aggregate_rating', 'votes']]
                          .sort_values(['aggregate_rating', 'restaurant_id'], ascending=[False, True]))
    
    st.dataframe(top_restaurantes.head(info_options), use_container_width=True)
    
with st.container():
    
    col1, col2 = st.columns(2)
    
    with col1:
        
        st.markdown(f'## Top {info_options} melhores tipos de culinária')
        
        df_aux = (df.loc[:, ['cuisines', 'aggregate_rating']]
                    .groupby('cuisines')
                    .mean('aggregate_rating')
                    .sort_values('aggregate_rating', ascending=False)
                    .reset_index())

        fig = px.bar(df_aux.head(info_options), x='cuisines', y='aggregate_rating', text='aggregate_rating', text_auto='.2f' , 
                     labels={'cuisines': 'Tipos de culinária',
                     'aggregate_rating': 'Média da avaliação média'})

        fig.update_traces(marker_color='#ff4b4b', textposition='outside')
        fig.update_layout(height=550)
        
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        
        st.markdown(f'## Top {info_options} piores tipos de culinária')
        
        df_aux = (df.loc[:, ['cuisines', 'aggregate_rating']]
                    .groupby('cuisines')
                    .mean('aggregate_rating')
                    .sort_values('aggregate_rating', ascending=True)
                    .reset_index())

        fig = px.bar(df_aux.head(info_options), x='cuisines', y='aggregate_rating', text='aggregate_rating', text_auto='.2f' , 
                     labels={'cuisines': 'Tipos de culinária',
                     'aggregate_rating': 'Média da avaliação média'})


        fig.update_traces(marker_color='#ff4b4b', textposition='outside')
        fig.update_layout(height=550)
        
        st.plotly_chart(fig, use_container_width=True)