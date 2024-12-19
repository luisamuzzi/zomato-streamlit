## Projeto de análise de dados da empresa Zomato

### Resumo

Este projeto foi desenvolvido como parte do curso de Python da Comunidade DS para estudo da linguagem python voltada à análise de dados e do framework streamlit.

[Acesse aqui o dashboard](https://zomatoproject-luisamuzzi.streamlit.app/).

### Índice

* [1. Problema de negócio](https://github.com/luisamuzzi/zomato_project?tab=readme-ov-file#1-problema-de-neg%C3%B3cio)
* [2. Premissas assumidas para a análise](https://github.com/luisamuzzi/zomato_project?tab=readme-ov-file#2-premissas-assumidas-para-a-an%C3%A1lise)
* [3. Estratégias da solução](https://github.com/luisamuzzi/zomato_project?tab=readme-ov-file#3-estrat%C3%A9gias-da-solu%C3%A7%C3%A3o)
* [4. Top 3 Insights de dados](https://github.com/luisamuzzi/zomato_project?tab=readme-ov-file#4-top-3-insights-de-dados)
* [5. O produto final do projeto](https://github.com/luisamuzzi/zomato_project?tab=readme-ov-file#5-o-produto-final-do-projeto)
* [6. Conclusão](https://github.com/luisamuzzi/zomato_project?tab=readme-ov-file#6-conclus%C3%A3o)
* [7. Próximos passos](https://github.com/luisamuzzi/zomato_project?tab=readme-ov-file#7-pr%C3%B3ximos-passos)

### 1. Problema de negócio

A empresa Zomato é um marketplace de restaurantes. Ou seja, seu core business é facilitar o encontro e negociações de clientes e restaurantes. Os restaurantes fazem o cadastro dentro da plataforma da Zomato, que disponibiliza informações como endereço, tipo de culinária servida, se possui reservas, se faz entregas e também uma nota de avaliação dos serviços e produtos do restaurante, dentre outras informações.

O principal objetivo da análise é identificar pontos chave da empresa por meio das seguintes perguntas de negócio:

#### Informações gerais:

1. Quantos restaurantes únicos estão registrados?
2. Quantos países únicos estão registrados?
3. Quantas cidades únicas estão registradas?
4. Qual o total de avaliações feitas?
5. Qual o total de tipos de culinária registrados?

#### Informações por país:

1. Qual o número de restaurantes registrados por país?
2. Quantas são as cidades registradas por país?
3. Qual a média de avaliações feitas por país?
4. Qual a média de preço de um prato para duas pessoas por país?

#### Informações por cidade:

1. Quais são as cidades com mais restaurantes na base de dados?
2. Quais são as cidades com mais restaurantes com média de avaliação acima de 4?
3. Quais são as cidades com mais restaurantes com média de avaliação abaixo de 2,5?
4. Quais são as cidades com o maior número de tipos culinários distintos?

#### Informações por tipo de culinária:

1. Quais são os melhores restaurantes dos principais tipos culinários?
2. Quais são os melhores tipos culinários?
3. Quais são os piores tipos culinários?

O objetivo desse projeto é criar um conjunto de gráficos e/ou tabelas que exibam essas métricas da melhor forma possível para o CEO.

### 2. Premissas assumidas para a análise

1. Marketplace foi o modelo de negócio assumido.
2. As 4 principais visões do negócio foram: Visão geral, visão países, visão cidades e visão tipos culinários.
3. Os dados foram obtidos em: https://www.kaggle.com/datasets/akashram/zomato-restaurants-autoupdated-dataset?resource=download&select=zomato.csv

### 3. Estratégias da solução

O painel estratégico foi desenvolvido utilizando as métricas que refletem as 4 principais visões da empresa:

1. Visão do geral
2. Visão por país
3. Visão por cidade
4. Visão por tipos culinários

Cada visão é representada pelo seguinte conjunto de métricas:

1. Visão geral
    1. Número de restaurantes cadastrados
    2. Número de países cadastrados
    3. Número de cidades cadastradas
    4. Número de avaliações feitas na plataforma  
    5. Número de tipos culinários cadastrados na plataforma
2. Visão países
    1. Distribuição da quantidade de restaurantes registrados por país
    2. Distribuição da quantidade de cidades registradas por país
    3. Distribuição da média de avaliações feitas por país
    4. Distribuição da média de preço de um prato para duas pessoas por país
3. Visão cidades
    1. Distribuição das 10 cidades com mais restaurantes cadastrados na base de dados
    2. Distribuição das 10 cidades com restaurantes com média de avaliação acima de 4
    3. Distribuição das 10 cidades com restaurantes com média de avaliação abaixo de 2,5
    4. Distribuição das 10 cidades com restaurantes com o maior número de tipos de culinária distintos
4. Visão tipos de culinária
    1. Média de avaliação dos melhores restaurantes dos principais tipos culinários (Italian, American, Arabian, Japanese e Home-made)
    2. Top restaurantes por média de avaliação
    3. Top melhores tipos de culinária
    4. Top piores tipos de culinária

### 4. Top 3 Insights de dados

1. A Índia é o país com mais restaurantes e cidades cadastradas e o segundo país com maior número médio de avaliações (atrás da Indonésia).
2. Emirados Árabes Unidos, Índia, Turquia e EUA tem as top 10 cidades com mais restaurantes registrados. Sendo a Índia o país que possui mais cidades no top 10 cidades com média de avaliação acima de 4 e no top 10 cidades com média de avaliação abaixo de 2,5 (nesse último, juntamente com o Brasil).
3. O tipo culinário mais bem avaliado é Outros e os piores avaliados são Somente drinks e Mineiro.

### 5. O produto final do projeto

Painel online, hospedado em um Cloud e disponível para acesso em qualquer dispositivo conectado à internet.

O painel pode ser acessado por meio do link: https://zomatoproject-luisamuzzi.streamlit.app/

### 6. Conclusão

O objetivo desse projeto é criar um conjunto de gráficos e/ou tabelas que exibam essas métricas da melhor forma possível para a áre de negócios.

Das visões apresentadas, podemos concluir que a Índia é o país com o maior número de restaurantes e cidades cadastradas. Além de ter o maior número de restaurantes no top 10 com média acima de 4 e com média abaixo de 2,5.

### 7. Próximos passos

1. Reduzir o número de métricas.
2. Criar novos filtros.
3. Adicionar novas visões de negócio.
