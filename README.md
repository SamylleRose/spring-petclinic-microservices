# Avaliação de Desempenho do Spring PetClinic (Microservices) com Locust

Vídeo mostrando o funcionamento: https://youtu.be/yxG1tb56QRA

Este repositório contém os artefatos para realizar uma avaliação de desempenho na aplicação Spring PetClinic (versão microservices) utilizando a ferramenta Locust.

## Objetivo

O objetivo é medir e relatar métricas de desempenho chave (tempo de resposta, requisições por segundo, taxa de erros) sob diferentes cargas de usuários.

## Pré-requisitos

- Docker e Docker Compose: Para subir a arquitetura de microserviços.

- Python 3: Para executar os scripts de população de dados e os testes.

- Git: Para clonar o repositório do PetClinic.

- Java 17 e Maven: Para compilar o projeto PetClinic caso clone o código fonte.

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

### 3. Executar os Testes de Carga

```
 python run_tests.py
```

### 4. Coletar e Analisar os Resultados

```
python analyze_results.py
```
