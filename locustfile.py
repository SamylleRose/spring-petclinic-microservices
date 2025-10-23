# locustfile.py

import random
from locust import HttpUser, task, between
from faker import Faker

# Inicializa o Faker para gerar dados em português
fake = Faker('pt_BR')


# Esta parte é executada uma vez quando o Locust inicia
try:
    with open("owner_ids.txt", "r") as f:
        # Lê todas as linhas e remove espaços/quebras de linha extras
        owner_ids = [line.strip() for line in f.readlines() if line.strip()]
    if not owner_ids:
        print("AVISO: Arquivo 'owner_ids.txt' está vazio. O teste de 'GET /owners/{id}' irá falhar.")
except FileNotFoundError:
    print("ERRO: Arquivo 'owner_ids.txt' não encontrado. Crie-o primeiro com o script de popular o banco.")
    owner_ids = []


class PetClinicUser(HttpUser):
  
    wait_time = between(1, 3)
    
   
    host = "http://localhost:8080"

    
    @task(4)
    def list_owners(self):
        self.client.get("/api/customer/owners")

    # Tarefa 2: Obter detalhes de um dono específico - Peso 3 (30%)
    @task(3)
    def get_owner_by_id(self):
        # Apenas executa se a lista de IDs foi carregada com sucesso
        if owner_ids:
            random_id = random.choice(owner_ids)
            # O parâmetro 'name' agrupa todas as requisições para IDs diferentes sob o mesmo nome no relatório
            self.client.get(f"/api/customer/owners/{random_id}", name="/api/customer/owners/[id]")

    # Tarefa 3: Listar todos os veterinários - Peso 2 (20%)
    @task(2)
    def list_vets(self):
        self.client.get("/api/vet/vets")

    # Tarefa 4: Cadastrar um novo dono - Peso 1 (10%)
    @task(1)
    def create_owner(self):
        new_owner_data = {
            "firstName": fake.first_name(),
            "lastName": fake.last_name(),
            "address": fake.street_address(),
            "city": fake.city(),
            "telephone": fake.msisdn()[:11] 
        }
        self.client.post("/api/customer/owners", json=new_owner_data)