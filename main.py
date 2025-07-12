from No import *
import pandas as pd
import random

# Parâmetros da simulação
DATASET_FILE = "dataset_final_29.06.25.txt"
D_MINIMA = 500   # distância mínima entre origem e destino
RAIO_COMUNICACAO = 10
LIMITE_BATERIA = 30
N_EXECUCOES = 100


# Carregando o dataset
df = pd.read_csv(DATASET_FILE, delimiter=";", header=None, on_bad_lines="skip")
df.columns = [
    "ID", "Data", "Hora", "Localizacao", "Bateria",
    "Memoria Int", "Memoria Ext", "Wi-Fi", "Bluetooth",
    "Conexao", "P2P", "Roteadores"
]

# Criando os objetos Nó
nos = []
for _, row in df.iterrows():
    no = No(
        id_no=row["ID"],
        data=row["Data"],
        hora=row["Hora"],
        localizacao=row["Localizacao"],
        bateria=row["Bateria"],
        memoria_int=row["Memoria Int"],
        memoria_ext=row["Memoria Ext"],
        wifi=row["Wi-Fi"],
        bluetooth=row["Bluetooth"],
        conexao=row["Conexao"],
        p2p=row["P2P"],
        roteadores=row["Roteadores"] if not pd.isna(row["Roteadores"]) else ""
    )
    nos.append(no)


def escolher_pares_validos(nos, D=500):
    tentativas = 0
    while tentativas < 1000:
        origem, destino = random.sample(nos, 2)
        if origem.distancia_para(destino) >= D:
            return origem, destino
        tentativas += 1
    raise RuntimeError("Não foi possível encontrar pares com distância mínima.")


def simular_entrega(origem, destino, nos, raio=10, egoismo=False, prioridade=False, limite_bateria=30):
    visitados = set()
    fila = [(origem, origem.timestamp, 0)]  # (nó atual, tempo, saltos)
    sucesso = False
    latencia = None
    saltos_total = 0

    while fila:
        atual, tempo_atual, saltos = fila.pop(0)
        visitados.add(atual.id_no)

        if atual.id_no == destino.id_no:
            sucesso = True
            latencia = (tempo_atual - origem.timestamp).total_seconds()
            saltos_total = saltos
            break

        for vizinho in nos:
            if vizinho.id_no in visitados:
                continue
            if not atual.pode_comunicar(vizinho, raio):
                continue
            if egoismo and vizinho.bateria < limite_bateria:
                if not prioridade:
                    continue
            fila.append((vizinho, vizinho.timestamp, saltos + 1))

    return sucesso, latencia if sucesso else None, saltos_total if sucesso else None


def simular_experimento(nos, N=100, D=500, R=10):
    resultados = {"caso_I": [], "caso_II": [], "caso_III": []}

    for i in range(N):
        try:
            origem, destino = escolher_pares_validos(nos, D)
        except RuntimeError:
            print("Pares não encontrados na execução", i)
            continue

        # Caso I - todos colaboram
        r1 = simular_entrega(origem, destino, nos, R, egoismo=False)
        resultados["caso_I"].append(r1)

        # Caso II - egoístas, sem prioridade
        r2 = simular_entrega(origem, destino, nos, R, egoismo=True, prioridade=False, limite_bateria=LIMITE_BATERIA)
        resultados["caso_II"].append(r2)

        # Caso III - egoístas, mas com prioridade
        r3 = simular_entrega(origem, destino, nos, R, egoismo=True, prioridade=True, limite_bateria=LIMITE_BATERIA)
        resultados["caso_III"].append(r3)

        print(f"Execução {i+1}/{N} concluída")
        print(f"Origem: {origem.id_no}, Destino: {destino.id_no}")
        print(f"  - Caso I: {'✓' if r1[0] else '✗'}, Saltos: {r1[2]}, Latência: {r1[1]}")
        print(f"  - Caso II: {'✓' if r2[0] else '✗'}, Saltos: {r2[2]}, Latência: {r2[1]}")
        print(f"  - Caso III: {'✓' if r3[0] else '✗'}, Saltos: {r3[2]}, Latência: {r3[1]}")

    return resultados


def calcular_metricas(resultados):
    for caso, tentativas in resultados.items():
        entregues = [r for r in tentativas if r[0]]
        taxa_entrega = len(entregues) / len(tentativas) * 100 if tentativas else 0
        latencias = [r[1] for r in entregues if r[1] is not None]
        saltos = [r[2] for r in entregues if r[2] is not None]

        print(f"\n== Resultados para {caso} ==")
        print(f"Taxa de entrega: {taxa_entrega:.2f}%")
        print(f"Latência média: {sum(latencias)/len(latencias):.2f} segundos" if latencias else "Nenhuma entrega bem-sucedida")
        print(f"Número médio de saltos: {sum(saltos)/len(saltos):.2f}" if saltos else "Nenhuma entrega bem-sucedida")


if __name__ == "__main__":
    resultados = simular_experimento(nos, N=N_EXECUCOES, D=D_MINIMA, R=RAIO_COMUNICACAO)
    calcular_metricas(resultados)