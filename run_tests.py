
import subprocess
import os
import time

# --- Definição dos Cenários de Teste ---
scenarios = [
    {
        "name": "A_leve",
        "users": 50,
        "spawn_rate": 10,
        "runtime": "2m",
        "reps": 15
    },
    {
        "name": "B_moderado",
        "users": 100,
        "spawn_rate": 20,
        "runtime": "2m",
        "reps": 15
    },
    {
        "name": "C_pico",
        "users": 200,
        "spawn_rate": 40,
        "runtime": "2m",
        "reps": 15
    }
]

# --- Diretório para salvar os resultados ---
results_dir = "results"
os.makedirs(results_dir, exist_ok=True)

print("==============================================")
print("--- INICIANDO EXECUÇÃO DOS TESTES DE CARGA ---")
print("==============================================")

# --- Loop principal para executar cada cenário ---
for scenario in scenarios:
    scenario_name = scenario["name"]
    
    # --- ETAPA DE REINICIALIZAÇÃO DO AMBIENTE ---
    print("\n=====================================================================")
    print(f"--- PREPARANDO AMBIENTE PARA O CENÁRIO: {scenario_name.upper()} ---")
    print("=====================================================================")

    try:
        print(" -> [1/4] Parando e removendo contêineres antigos (docker-compose down)...")
        subprocess.run(["docker-compose", "down"], check=True, capture_output=True)

        print(" -> [2/4] Iniciando novos contêineres (docker-compose up -d)...")
        subprocess.run(["docker-compose", "up", "-d"], check=True, capture_output=True)

        print(" -> [3/4] Aguardando 90 segundos para os serviços Java iniciarem...")
        time.sleep(90)

        print(" -> [4/4] Populando o banco de dados com dados iniciais...")
        subprocess.run(["python", "populate_owners.py"], check=True)
        
        print(f"--- Ambiente pronto. Iniciando testes do cenário {scenario_name.upper()} ---")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ ERRO CRÍTICO ao preparar o ambiente: {e}")
        print("Output do erro:", e.stderr.decode('utf-8', errors='ignore'))
        print("Abortando a execução.")
        exit()
    except FileNotFoundError:
        print("\n❌ ERRO: O comando 'docker-compose' ou 'python' não foi encontrado.")
        exit()

    # Loop para as repetições de cada cenário
    for i in range(1, scenario["reps"] + 1):
        print(f"  -> Executando repetição {i} de {scenario['reps']}...")
        
        csv_prefix = os.path.join(results_dir, f"cenario_{scenario_name}_run_{i:02d}")
        
        command = [
            "python", "-m", "locust",
            "-f", "locustfile.py",
            "--headless",
            "-u", str(scenario["users"]),
            "-r", str(scenario["spawn_rate"]),
            "-t", scenario["runtime"],
            "--csv", csv_prefix,
            "--exit-code-on-error", "0"  # <--- MUDANÇA 1: Diz ao Locust para não falhar
        ]
        
        try:
            # MUDANÇA 2: Removido 'check=True' para não parar o script em caso de erro do Locust
            subprocess.run(command) 
            print(f"  -> Repetição {i} concluída.")
        except Exception as e:
            print(f"  -> ❌ ERRO INESPERADO na execução da repetição {i}: {e}")
            break

print("\n==============================================")
print("--- TODOS OS TESTES FORAM CONCLUÍDOS! ---")
print("==============================================")