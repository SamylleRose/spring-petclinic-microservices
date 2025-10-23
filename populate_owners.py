import requests
import random
from faker import Faker


# CONFIGURAÇÕES 


# Inicializa o Faker para gerar dados em português brasileiro
fake = Faker('pt_BR')

# Constantes da API
BASE_URL = "http://localhost:8080/api"
OWNERS_URL = f"{BASE_URL}/customer/owners"

# Configurações de Geração de Dados 
TOTAL_OWNERS_TO_CREATE = 300
MAX_PETS_PER_OWNER = 3
OWNER_IDS_FILE = "owner_ids.txt"


# DEFINIÇÃO DAS FUNÇÕES


def create_owner():
    
    owner_data = {
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "address": fake.street_address(),
        "city": fake.city(),
        "telephone": fake.msisdn()[:11]
    }
    try:
        response = requests.post(OWNERS_URL, json=owner_data)
        response.raise_for_status()
        created_owner = response.json()
        owner_id = created_owner.get("id")
        print(f"✅ Dono '{created_owner['firstName']}' criado com sucesso (ID: {owner_id}).")
        return owner_id
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao criar dono: {e}")
        return None

def add_pet_to_owner(owner_id):
  
    if not owner_id:
        return
        
    pet_types = ["cat", "dog", "lizard", "snake", "bird", "hamster"]
    pet_type = random.choice(pet_types)
    pet_data = {
        "name": fake.first_name(),
        "birthDate": fake.date_of_birth(minimum_age=1, maximum_age=15).strftime("%Y-%m-%d"),
        "typeId": pet_types.index(pet_type) + 1
    }
    url = f"{OWNERS_URL}/{owner_id}/pets"
    try:
        response = requests.post(url, json=pet_data)
        response.raise_for_status()
        print(f"  🐾 Pet '{pet_data['name']}' ({pet_type}) adicionado ao dono ID {owner_id}.")
    except requests.exceptions.RequestException as e:
     
        error_text = getattr(e.response, 'text', str(e))
        print(f"  ❌ Erro ao adicionar pet ao dono ID {owner_id}: {error_text}")


# BLOCO DE EXECUÇÃO PRINCIPAL 

if __name__ == "__main__":
    print("=====================================================")
    print("--- INICIANDO A POPULAÇÃO DE DONOS E PETS ---")
    print("=====================================================")

    created_owner_ids = []
    for _ in range(TOTAL_OWNERS_TO_CREATE):
        owner_id = create_owner()
        if owner_id:
            created_owner_ids.append(owner_id)
            num_pets = random.randint(1, MAX_PETS_PER_OWNER)
            for _ in range(num_pets):
                add_pet_to_owner(owner_id)
    
    if created_owner_ids:
        with open(OWNER_IDS_FILE, "w") as f:
            for owner_id in created_owner_ids:
                f.write(f"{owner_id}\n")
        print(f"\n✅ IDs de {len(created_owner_ids)} donos foram salvos em '{OWNER_IDS_FILE}'.")

    print("\n===============================================")
    print("--- POPULAÇÃO DE DONOS E PETS CONCLUÍDA! ---")
    print("===============================================")