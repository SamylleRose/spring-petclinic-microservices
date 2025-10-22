# analyze_results.py (VERSÃO CORRIGIDA)

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configurações ---
results_dir = "results"
scenarios_config = [
    {"name": "A_leve", "reps": 15, "warmup_sec": 30},
    {"name": "B_moderado", "reps": 15, "warmup_sec": 30},
    {"name": "C_pico", "reps": 15, "warmup_sec": 30}
]

# --- Estilo dos gráficos ---
sns.set_theme(style="whitegrid")

# --- DataFrame para armazenar o resumo final ---
summary_data = []

print("==============================================")
print("--- INICIANDO ANÁLISE DOS RESULTADOS ---")
print("==============================================")

# --- Processa cada cenário ---
for scenario in scenarios_config:
    scenario_name = scenario["name"]
    all_runs_data = []
    
    print(f"\nAnalisando Cenário: {scenario_name.upper()}...")
    
    for i in range(1, scenario["reps"] + 1):
        stats_file = os.path.join(results_dir, f"cenario_{scenario_name}_run_{i:02d}_stats.csv")
        history_file = os.path.join(results_dir, f"cenario_{scenario_name}_run_{i:02d}_stats_history.csv")

        try:
            # Usamos o _stats_history.csv para descartar o aquecimento
            df_history = pd.read_csv(history_file)
            
            # Filtra os dados para remover o período de aquecimento
            df_warmup_removed = df_history[df_history["Timestamp"] >= (df_history["Timestamp"].iloc[0] + scenario["warmup_sec"])]
            
            # Se não sobrar dados após remover o aquecimento, pula esta repetição
            if df_warmup_removed.empty:
                print(f"  Aviso: Repetição {i} não teve dados suficientes após o aquecimento.")
                continue

            # Obtém os dados agregados do final da execução para Total de Requisições e Falhas
            df_stats = pd.read_csv(stats_file)
            aggregated_stats = df_stats[df_stats["Name"] == "Aggregated"].iloc[0]

            # --- CORREÇÃO APLICADA AQUI ---
            # Calcula as métricas pós-aquecimento usando os nomes corretos das colunas
            avg_response_time = df_warmup_removed["Total Average Response Time"].mean()
            max_response_time = df_warmup_removed["Total Max Response Time"].max()
            requests_per_second = df_warmup_removed["Requests/s"].mean()
            # --- FIM DA CORREÇÃO ---
            
            total_requests = aggregated_stats["Request Count"]
            total_failures = aggregated_stats["Failure Count"]
            success_percentage = ((total_requests - total_failures) / total_requests) * 100 if total_requests > 0 else 100

            all_runs_data.append({
                "Tempo Médio de Resposta (ms)": avg_response_time,
                "Tempo Máximo de Resposta (ms)": max_response_time,
                "Requisições por Segundo": requests_per_second,
                "Total de Requisições": total_requests,
                "Erros": total_failures,
                "% de Sucesso": success_percentage,
            })
            
        except FileNotFoundError:
            print(f"  Aviso: Arquivo de resultado para a repetição {i} não encontrado. Pulando.")
            continue

    if not all_runs_data:
        print(f"Nenhum dado válido encontrado para o cenário {scenario_name}. Pulando.")
        continue

    # Calcula a média de todas as repetições para o cenário
    df_scenario_runs = pd.DataFrame(all_runs_data)
    scenario_summary = df_scenario_runs.mean().to_dict()
    scenario_summary["Cenário"] = scenario_name.replace("_", " ").title()
    summary_data.append(scenario_summary)

# --- Cria e exibe a tabela de resumo final ---
df_summary = pd.DataFrame(summary_data).set_index("Cenário")
print(f"\n--- TABELA DE RESULTADOS (MÉDIA DE {scenarios_config[0]['reps']} REPETIÇÃO(ÕES)) ---\n")
print(df_summary.to_markdown(floatfmt=".2f"))


# --- Geração dos Gráficos ---
print("\nGerando gráficos...")

# Gráfico 1: Tempo Médio de Resposta
plt.figure(figsize=(10, 6))
sns.barplot(x=df_summary.index, y="Tempo Médio de Resposta (ms)", data=df_summary, palette="viridis")
plt.title("Tempo Médio de Resposta por Cenário")
plt.ylabel("Tempo (ms)")
plt.xlabel("Cenário de Carga")
plt.savefig("grafico_tempo_medio.png")
plt.close()

# Gráfico 2: Requisições por Segundo (RPS)
plt.figure(figsize=(10, 6))
sns.barplot(x=df_summary.index, y="Requisições por Segundo", data=df_summary, palette="plasma")
plt.title("Requisições por Segundo (RPS) por Cenário")
plt.ylabel("Req/s")
plt.xlabel("Cenário de Carga")
plt.savefig("grafico_rps.png")
plt.close()

# Gráfico 3: Percentual de Sucesso
plt.figure(figsize=(10, 6))
ax = sns.barplot(x=df_summary.index, y="% de Sucesso", data=df_summary, palette="magma")
ax.set(ylim=(0, 105)) # Ajusta o eixo Y para ir de 0 a 105%
plt.title("Percentual de Sucesso por Cenário")
plt.ylabel("% Sucesso")
plt.xlabel("Cenário de Carga")
plt.savefig("grafico_sucesso.png")
plt.close()

print("Gráficos salvos como: grafico_tempo_medio.png, grafico_rps.png, grafico_sucesso.png")
print("\n==============================================")
print("--- ANÁLISE CONCLUÍDA! ---")
print("==============================================")