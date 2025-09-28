# -----------------------------------------------------------------------------
# Estágio 1: Configuração do Ambiente
# -----------------------------------------------------------------------------

# 1. Imagem Base: Começamos com uma imagem oficial do Python 3.11,
# na versão 'slim', que é menor e ideal para produção.
FROM python:3.11-slim

# 2. Variáveis de Ambiente:
#    - PYTHONUNBUFFERED: Garante que os logs do Python apareçam em tempo real.
#    - PYTHONPATH: Diz ao Python para procurar módulos dentro de /app,
#      resolvendo problemas de importação como 'from app.core import ...'.
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 3. Instalação de Dependências do Sistema (Neste caso, o Google Chrome)
#    Necessário para o Selenium / undetected-chromedriver.
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    wget \
    unzip \
    --no-install-recommends && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /etc/apt/keyrings/google-chrome.gpg && \
    sh -c 'echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list' && \
    apt-get update && apt-get install -y \
    google-chrome-stable \
    --no-install-recommends && \
    # Limpa o cache do apt para manter a imagem pequena
    rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Estágio 2: Construção da Aplicação
# -----------------------------------------------------------------------------

# 4. Diretório de Trabalho: Define /app como o diretório padrão para os
#    comandos seguintes.
WORKDIR /app

# 5. Instalação de Dependências Python (Otimizado para Cache)
#    Primeiro, copiamos APENAS o requirements.txt. O Docker só vai re-executar
#    o passo seguinte (pip install) se este arquivo mudar.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Cópia do Código da Aplicação
#    Agora, copiamos o nosso código. Se mudarmos apenas o código Python,
#    os passos anteriores (pip install) não serão re-executados,
#    tornando o build muito mais rápido.
#    Este comando cria a estrutura /app/app/main.py, etc.
COPY ./app /app/app

# 7. Exposição da Porta
#    Informa ao Docker que o container escuta na porta 8000.
EXPOSE 8000

# 8. Comando de Execução
#    O comando que será executado quando o container iniciar.
#    Usa Gunicorn como um gerenciador de processos robusto para produção.
CMD ["gunicorn", "-w", "1", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]