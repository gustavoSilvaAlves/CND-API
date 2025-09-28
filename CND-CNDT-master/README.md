# API de Consulta de CND (Certidão Negativa de Débitos) e CNDT (Certidão Negativa de Débitos Trabalhistas) 📜

![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Uma API robusta e assíncrona construída com FastAPI para automatizar a consulta de Certidões Negativas de Débitos (CND) diretamente do sistema da Dataprev. O projeto é totalmente containerizado com Docker para facilitar a execução em qualquer ambiente.

## ✨ Sobre o Projeto

Este projeto serve como um *wrapper* para o serviço de consulta de CND da Dataprev. Em vez de interagir manualmente com o site, esta API expõe um endpoint RESTful simples que recebe um CNPJ, realiza o processo de *web scraping* de forma automatizada e retorna o conteúdo da certidão em um formato JSON estruturado.

O principal objetivo é fornecer uma maneira programática e eficiente de integrar a consulta de CND em outros sistemas.

## 🚀 Tecnologias Utilizadas

Este projeto foi construído utilizando as seguintes tecnologias:

* **[Python 3.11](https://www.python.org/)**: Linguagem de programação principal.
* **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web assíncrono para a construção da API.
* **[Uvicorn](https://www.uvicorn.org/)** & **[Gunicorn](https://gunicorn.org/)**: Servidores ASGI/WSGI para rodar a aplicação em produção.
* **[HTTPX](https://www.python-httpx.org/)**: Cliente HTTP assíncrono para realizar as consultas ao site da Dataprev.
* **[Docker](https://www.docker.com/)** & **[Docker Compose](https://docs.docker.com/compose/)**: Para containerização e orquestração do ambiente da aplicação.

## 📁 Estrutura do Projeto

A estrutura de arquivos do projeto é organizada da seguinte forma:

```text
cndFastAPI/
├── .dockerignore      # Define arquivos a serem ignorados pelo Docker no build.
├── .gitignore         # Define arquivos a serem ignorados pelo Git.
├── Dockerfile         # Receita para construir a imagem Docker da aplicação.
├── compose.yaml       # Arquivo para orquestrar a execução do contêiner com Docker Compose.
├── main.py            # Ponto de entrada e lógica principal da API com FastAPI.
└── requirements.txt   # Lista de dependências Python do projeto.
```
## ⚙️ Como Começar

Siga os passos abaixo para executar a aplicação localmente.

### Pré-requisitos

Você precisa ter o **Docker** e o **Docker Compose** instalados na sua máquina.

* [Instalar Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Instalação e Execução

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/Mtec-Developer/CND.git](https://github.com/Mtec-Developer/CND.git)
    cd CND
    ```

2.  **Construa e execute com Docker Compose:**
    Este único comando irá construir a imagem Docker (se ainda não existir) e iniciar o contêiner da aplicação.

    ```bash
    docker compose up --build
    ```

3.  **Acesse a API:**
    A aplicação estará rodando e acessível em `http://localhost:8000`.

##  API - Uso e Endpoints

A API possui um único endpoint para consulta. Você pode acessar a documentação interativa (Swagger UI) gerada automaticamente pelo FastAPI em:

**`http://localhost:8000/docs`**

### Consulta de CND

* **Endpoint:** `GET /CND`
* **Descrição:** Retorna o conteúdo da Certidão Negativa de Débitos para o CNPJ informado.
* **Parâmetros de Query:**
    * `cnpj` (string, **obrigatório**): O CNPJ a ser consultado. Deve conter apenas 14 dígitos, sem pontos ou traços.

#### Exemplo de Requisição

```bash
curl -X 'GET' \
  'http://localhost:8000/CND?cnpj=16928337000101' \
  -H 'accept: application/json'

Exemplo de Resposta de Sucesso (200 OK)
JSON

{
  "cnpj": "16928337000101",
  "conteudo_certidao": "MINISTERIO DA FAZENDA\nSECRETARIA DA RECEITA FEDERAL DO BRASIL\nCERTIDAO NEGATIVA\nDE DEBITOS RELATIVOS AS CONTRIBUICOES PREVIDENCIARAS  E AS DE TERCEIROS\n..."
}
Exemplo de Resposta de Erro (404 Not Found)
Quando não há certidão emitida para o CNPJ.

JSON

{
  "detail": "Não há certidão emitida para o estabelecimento 19131243000197"
}
Exemplo de Resposta de Erro (422 Unprocessable Entity)
Quando o CNPJ fornecido é inválido (ex: contém letras, menos de 14 dígitos, etc.).

JSON

{
  "detail": [
    {
      "loc": ["query", "cnpj"],
      "msg": "String should match pattern '^[0-9]{14}$'",
      "type": "string_pattern"
    }
  ]
}

