# run_tests.py

import subprocess
import os

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
    print(f"\n--- Iniciando Cenário: {scenario_name.upper()} ---")
    
    # Loop para as repetições de cada cenário
    for i in range(1, scenario["reps"] + 1):
        print(f"  -> Executando repetição {i} de {scenario['reps']}...")
        
        # Define o nome base para os arquivos CSV desta execução
        csv_prefix = os.path.join(results_dir, f"cenario_{scenario_name}_run_{i:02d}")
        
        # Constrói o comando do Locust para ser executado no terminal
        command = [
            "python", "-m", "locust",
            "-f", "locustfile.py",
            "--headless", # Roda sem a interface web
            "-u", str(scenario["users"]),
            "-r", str(scenario["spawn_rate"]),
            "-t", scenario["runtime"],
            "--csv", csv_prefix
        ]
        
        # Executa o comando e aguarda a conclusão
        try:
            subprocess.run(command, check=True)
            print(f"  -> Repetição {i} concluída. Resultados salvos em '{csv_prefix}_stats.csv'")
        except subprocess.CalledProcessError as e:
            print(f"  -> ERRO na execução da repetição {i}: {e}")
            print("  -> Abortando as repetições para este cenário.")
            break # Pára as repetições deste cenário se uma falhar
        except FileNotFoundError:
            print("ERRO: O comando 'locust' não foi encontrado.")
            print("Verifique se o Locust está instalado e no PATH do sistema.")
            exit()

print("\n==============================================")
print("--- TODOS OS TESTES FORAM CONCLUÍDOS! ---")
print("==============================================")