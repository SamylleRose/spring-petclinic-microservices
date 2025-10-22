# analyze_results.py (VERSÃO FINAL COM GRÁFICOS AVANÇADOS E DE BARRA INDIVIDUAIS)

import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# --- Configurações ---
results_dir = "results"
scenarios_config = [
    {"name": "A_leve", "users": 50, "reps": 15, "warmup_sec": 30},
    {"name": "B_moderado", "users": 100, "reps": 15, "warmup_sec": 30},
    {"name": "C_pico", "users": 200, "reps": 15, "warmup_sec": 30}
]

# --- Estilo dos gráficos ---
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)

# --- DataFrames para armazenar os resultados ---
summary_data = []
endpoint_data = []
latency_distribution_data = []

print("==============================================")
print("--- INICIANDO ANÁLISE DOS RESULTADOS ---")
print("==============================================")

for scenario in scenarios_config:
    scenario_name = scenario["name"]
    all_runs_aggregated = []
    all_runs_endpoints = []
    
    print(f"\nAnalisando Cenário: {scenario_name.upper()}...")
    
    for i in range(1, scenario["reps"] + 1):
        stats_file = os.path.join(results_dir, f"cenario_{scenario_name}_run_{i:02d}_stats.csv")
        history_file = os.path.join(results_dir, f"cenario_{scenario_name}_run_{i:02d}_stats_history.csv")

        try:
            df_stats = pd.read_csv(stats_file)
            df_history = pd.read_csv(history_file)
            
            df_warmup_removed = df_history[df_history["Timestamp"] >= (df_history["Timestamp"].iloc[0] + scenario["warmup_sec"])]
            if df_warmup_removed.empty:
                print(f"  Aviso: Repetição {i} sem dados agregados suficientes. Pulando.")
                continue
            
            aggregated_stats = df_stats[df_stats["Name"] == "Aggregated"].iloc[0]

            avg_response_time = df_warmup_removed["Total Average Response Time"].mean()
            all_runs_aggregated.append({
                "Tempo Médio de Resposta (ms)": avg_response_time,
                "Tempo Máximo de Resposta (ms)": df_warmup_removed["Total Max Response Time"].max(),
                "Requisições por Segundo": df_warmup_removed["Requests/s"].mean(),
                "Total de Requisições": aggregated_stats["Request Count"],
                "Falhas": aggregated_stats["Failure Count"],
            })

            latency_distribution_data.append({
                "Cenário": scenario_name.replace("_", " ").title(),
                "Tempo de Resposta (ms)": avg_response_time
            })
            
            df_endpoints_run = df_stats[df_stats["Name"] != "Aggregated"]
            for _, row in df_endpoints_run.iterrows():
                all_runs_endpoints.append({
                    "Cenário": scenario_name.replace("_", " ").title(),
                    "Endpoint": row["Name"],
                    "Tempo Médio (ms)": row["Average Response Time"],
                    "Falhas": row["Failure Count"],
                    "Contagem de Requisições": row["Request Count"]
                })
            
        except FileNotFoundError:
            print(f"  Aviso: Arquivo para repetição {i} não encontrado. Pulando.")
            continue
        except Exception as e:
            print(f"  ❌ Erro ao processar repetição {i}: {e}")
            continue

    if not all_runs_aggregated:
        print(f"Nenhum dado válido encontrado para o cenário {scenario_name}. Pulando.")
        continue

    df_agg_runs = pd.DataFrame(all_runs_aggregated)
    scenario_summary = df_agg_runs.mean().to_dict()
    scenario_summary["Cenário"] = scenario_name.replace("_", " ").title()
    scenario_summary["Usuários"] = scenario["users"]
    summary_data.append(scenario_summary)

    if all_runs_endpoints:
        df_ep_runs = pd.DataFrame(all_runs_endpoints)
        scenario_endpoints_summary = df_ep_runs.groupby(['Cenário', 'Endpoint']).mean().reset_index()
        endpoint_data.append(scenario_endpoints_summary)

# --- Monta os DataFrames finais ---
df_summary = pd.DataFrame(summary_data).set_index("Cenário")
df_summary["Sucessos"] = df_summary["Total de Requisições"] - df_summary["Falhas"]
df_summary["Taxa de Falha (%)"] = (df_summary["Falhas"] / df_summary["Total de Requisições"].replace(0, 1)) * 100
df_latency_dist = pd.DataFrame(latency_distribution_data)

df_endpoints = pd.DataFrame()
if endpoint_data:
    df_endpoints = pd.concat(endpoint_data, ignore_index=True)

# --- Exibe as Tabelas de Resumo ---
print(f"\n--- TABELA DE RESULTADOS GERAIS (MÉDIA DE ATÉ {scenarios_config[0]['reps']} REPETIÇÕES) ---\n")
print(df_summary[['Usuários', 'Requisições por Segundo', 'Tempo Médio de Resposta (ms)', 'Falhas', 'Taxa de Falha (%)']].to_markdown(floatfmt=".2f"))

if not df_endpoints.empty:
    print(f"\n--- TABELA DE DESEMPENHO POR ENDPOINT (MÉDIA) ---\n")
    print(df_endpoints.pivot_table(index='Endpoint', columns='Cenário', values=['Tempo Médio (ms)', 'Falhas']).to_markdown(floatfmt=".2f"))

# --- Geração dos Gráficos ---
print("\nGerando conjunto completo de gráficos...")

# --- GRÁFICOS AVANÇADOS ---

# Gráfico 1: Composição de Sucesso vs. Falha
plt.figure()
df_summary[['Sucessos', 'Falhas']].plot(kind='bar', stacked=True, color=['#2ECC71', '#E74C3C'], figsize=(12, 7), rot=0)
plt.title('Composição das Requisições: Sucessos vs. Falhas', fontsize=16)
plt.ylabel('Número Médio de Requisições por Execução')
plt.xlabel('Cenário de Carga')
plt.tight_layout()
plt.savefig('grafico_avancado_1_sucesso_vs_falha.png')
plt.close()

# Gráfico 2: Latência vs. Throughput
plt.figure()
sns.scatterplot(data=df_summary, x='Requisições por Segundo', y='Tempo Médio de Resposta (ms)', hue='Cenário', s=200, palette='plasma')
sns.lineplot(data=df_summary.sort_values('Requisições por Segundo'), x='Requisições por Segundo', y='Tempo Médio de Resposta (ms)', color='grey', legend=False)
plt.title('Latência vs. Vazão (Throughput)', fontsize=16)
plt.ylabel('Tempo Médio de Resposta (ms)')
plt.xlabel('Requisições por Segundo (RPS)')
plt.grid(True, which='both', linestyle='--')
plt.tight_layout()
plt.savefig('grafico_avancado_2_latencia_vs_throughput.png')
plt.close()

# Gráfico 3: Distribuição da Latência
plt.figure()
sns.boxplot(data=df_latency_dist, x='Cenário', y='Tempo de Resposta (ms)', palette='viridis')
plt.title('Distribuição do Tempo de Resposta entre as Execuções', fontsize=16)
plt.ylabel('Tempo de Resposta (ms)')
plt.xlabel('Cenário de Carga')
plt.tight_layout()
plt.savefig('grafico_avancado_3_distribuicao_latencia.png')
plt.close()

# Gráfico 4: Escalabilidade do Throughput
plt.figure()
sns.lineplot(data=df_summary, x='Usuários', y='Requisições por Segundo', marker='o', markersize=10, color='b')
plt.title('Escalabilidade do Throughput vs. Carga de Usuários', fontsize=16)
plt.ylabel('Requisições por Segundo (RPS)')
plt.xlabel('Número de Usuários Concorrentes')
plt.xticks(df_summary['Usuários'])
plt.ylim(bottom=0)
plt.grid(True, which='both', linestyle='--')
plt.tight_layout()
plt.savefig('grafico_avancado_4_escalabilidade_throughput.png')
plt.close()


# --- NOVOS GRÁFICOS DE BARRA INDIVIDUAIS ---

# Gráfico 5: Tempo Médio de Resposta (Barra)
plt.figure()
sns.barplot(data=df_summary, x=df_summary.index, y='Tempo Médio de Resposta (ms)', palette='coolwarm', hue=df_summary.index, legend=False)
plt.title('Comparativo: Tempo Médio de Resposta', fontsize=16)
plt.ylabel('Tempo (ms)')
plt.xlabel('Cenário de Carga')
plt.tight_layout()
plt.savefig('grafico_barra_1_tempo_resposta.png')
plt.close()

# Gráfico 6: Requisições por Segundo (Barra)
plt.figure()
sns.barplot(data=df_summary, x=df_summary.index, y='Requisições por Segundo', palette='crest', hue=df_summary.index, legend=False)
plt.title('Comparativo: Requisições por Segundo (RPS)', fontsize=16)
plt.ylabel('Requisições por Segundo (RPS)')
plt.xlabel('Cenário de Carga')
plt.tight_layout()
plt.savefig('grafico_barra_2_rps.png')
plt.close()

# Gráfico 7: Contagem de Sucessos (Barra)
plt.figure()
sns.barplot(data=df_summary, x=df_summary.index, y='Sucessos', palette='Greens_r', hue=df_summary.index, legend=False)
plt.title('Comparativo: Contagem de Requisições com Sucesso', fontsize=16)
plt.ylabel('Número Médio de Sucessos')
plt.xlabel('Cenário de Carga')
plt.tight_layout()
plt.savefig('grafico_barra_3_sucessos.png')
plt.close()

# Gráfico 8: Contagem de Falhas (Barra)
plt.figure()
sns.barplot(data=df_summary, x=df_summary.index, y='Falhas', palette='Reds_r', hue=df_summary.index, legend=False)
plt.title('Comparativo: Contagem de Falhas', fontsize=16)
plt.ylabel('Número Médio de Falhas')
plt.xlabel('Cenário de Carga')
plt.tight_layout()
plt.savefig('grafico_barra_4_falhas.png')
plt.close()

print("Análise concluída. Verifique os novos gráficos salvos na pasta.")
print("==============================================")