# Avaliação de Desempenho do Spring PetClinic (Microservices) com Locust

Este repositório contém os artefatos para realizar uma avaliação de desempenho na aplicação Spring PetClinic (versão microservices) utilizando a ferramenta Locust.

## Objetivo

O objetivo é medir e relatar métricas de desempenho chave (tempo de resposta, requisições por segundo, taxa de erros) sob diferentes cargas de usuários.

## Pré-requisitos

- Docker e Docker Compose: Para subir a arquitetura de microserviços.

- Python 3: Para executar os scripts de população de dados e os testes.

- Git: Para clonar o repositório do PetClinic.

- Java 17+ e Maven: Para compilar o projeto PetClinic caso clone o código fonte.

## Passo a Passo para Reprodução

### 1. Preparar o Ambiente

Primeiro, clone e suba a aplicação Spring PetClinic Microservices.

```
# Clone o repositório oficial
git clone [https://github.com/spring-petclinic/spring-petclinic-microservices.git](https://github.com/spring-petclinic/spring-petclinic-microservices.git)
cd spring-petclinic-microservices

# Compile os pacotes com Maven (pode demorar alguns minutos)
./mvnw clean install -DskipTests

# Suba a stack completa com Docker Compose
docker-compose up -d

```

Aguarde alguns minutos para todos os serviços (API Gateway, Customers, Vets, etc.) iniciarem. Você pode verificar o status com docker-compose ps.

### 2. Instalar Dependências Python

Navegue para o diretório onde você salvou os scripts deste projeto e instale as bibliotecas Python necessárias.

```
pip install locust faker requests
```

### 3. Popular o Banco de Dados

Antes de iniciar os testes, é crucial ter dados na aplicação para que as requisições GET retornem resultados válidos. Execute o script de população:

```
python populate_data.py
```

Este script irá criar 50 donos, cada um com um número aleatório de pets.

### 4. Executar os Testes de Carga

O script run_scenarios.sh foi criado para executar os três cenários de teste definidos. Dê permissão de execução ao script primeiro:

```
chmod +x run_scenarios.sh
```

Agora, execute cada cenário. É recomendado executar cada um 3 vezes para obter uma média confiável, conforme solicitado no trabalho.

### Cenário A (Leve):

```
./run_scenarios.sh leve
```

### Cenário B (Moderado):

```
./run_scenarios.sh medio
```

### Cenário C (Pico):

```
./run_scenarios.sh pico
```

### 5. Coletar e Analisar os Resultados

Após a execução de cada cenário, os resultados serão salvos na pasta results/. Você encontrará dois tipos de arquivo para cada cenário:

- cenario_leve_stats.csv: Dados brutos com as métricas principais.

- cenario_leve_report.html: Um relatório web completo com gráficos interativos de tempo de resposta, RPS e falhas. Este relatório é excelente para incluir no seu artigo e vídeo.

Abra os arquivos CSV em uma planilha (Excel, Google Sheets) para calcular as médias das 3 repetições de cada cenário. Use o arquivo resumo_resultados.md como guia para organizar sua tabela final.

Importante sobre o aquecimento (warm-up): O Locust não tem uma função nativa para "descartar" o primeiro minuto. Ao analisar os gráficos no relatório HTML, simplesmente ignore o período inicial onde a carga está subindo (ramp-up) e foque no período estável do teste.
