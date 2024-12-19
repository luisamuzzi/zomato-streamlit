import streamlit as st
from PIL import Image

#==============================================
# Configuração da largura da página
#==============================================
st.set_page_config(page_title='Home', page_icon='🏠', layout='wide')

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

    st.markdown("### Feito por [Luísa Muzzi](https://luisamuzzi.github.io/portfolio_projetos/)")
    
#==============================================
# Texto da página
#==============================================
st.write('# Zomato Dashboard')

st.markdown(
    """
    Este dashboard foi construído para acompanhar as métricas da empresa Zomato.
    ### Como utilizar esse Dashboard?
    - Main Page: Métricas gerais e mapa de restaurantes.
    - Visão Países: Métricas por país.
    - Visão Cidades: Métricas por cidade.
    - Visão Tipos de Culinária: Métricas por tipo de culinária.
    ### A Zomato
    A Zomato é uma empresa indiana de que atua como um marketplace. Fundada em 2008, sua proposta é fazer a conexão entre restaurantes 
    e clientes por meio da sua plataforma. Os restaurantes fazem o cadastro dentro da plataforma da Zomato, que disponibiliza 
    aos clientes informações como endereço, tipo de culinária servida, se possui reservas, se faz entregas e também uma nota de 
    avaliação dos serviços e produtos do restaurante, dentre outras informações. Cientes da Zomato utilizam a plataforma para 
    procurar e descobrir novos restaurantes, ler e deixar avaliações de restaurantes, realizar pedidos, entre outros.
    ### Aquisição dos dados
    Os dados utilizados nesse projeto são dados públicos disponibilizados pela empresa no Kaggle. Esse projeto não possui nenhuma
    afiliação com a empresa Zomato.
    ### Contato
    Este dashboard foi feito por Luísa Muzzi. 
    - [LinkedIn](https://www.linkedin.com/in/lu%C3%ADsamuzzi/)
    - [GitHub](https://github.com/luisamuzzi)
    - [Portfólio de projetos](https://luisamuzzi.github.io/portfolio_projetos/)
""")