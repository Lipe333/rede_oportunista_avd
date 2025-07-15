from No import *
import pandas as pd
import random
from collections import defaultdict
from datetime import timedelta
from collections import defaultdict, deque # Adicione deque aqui

# Parâmetros da simulação
DATASET_FILE = "dataset_final_29.06.25.txt"
D_MINIMA = 500   # distância mínima entre origem e destino
RAIO_COMUNICACAO = 500
LIMITE_BATERIA = 30
N_EXECUCOES = 100
JANELA_TEMPO = 3000  # segundos

""" 
    Quanto maior o raio de comunicação e a janela de tempo, maior a porcentagem de mensagens entregues, no entanto, a latencia também aumenta
    Janela de tempo original = 30s
    Raio original = 10m
    Distancia original = 500m

"""

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

# Agrupar nós por timestamp para acesso rápido
nos_por_tempo = defaultdict(list)
for no in nos:
    nos_por_tempo[no.timestamp].append(no)

def escolher_pares_validos(nos, D=500):
    tentativas = 0
    while tentativas < 2000:
        origem, destino = random.sample(nos, 2)
        # evita origem == destino
        if origem.id_no == destino.id_no:
            tentativas += 1
            continue
        if origem.distancia_para(destino) >= D and origem.timestamp <= destino.timestamp:
            return origem, destino
        tentativas += 1
    raise RuntimeError("Não foi possível encontrar pares com distância mínima.")

def simular_entrega(origem, destino, nos_por_tempo, raio=10, egoismo=False,
                    prioridade=False, limite_bateria=30, max_saltos=100):
    visitados = set()
    # Mude esta linha:
    # fila = [(origem, origem.timestamp, 0)]
    # Para esta:
    fila = deque([(origem, origem.timestamp, 0)]) # Agora a fila é um deque
    sucesso = False
    latencia = None
    saltos_total = 0
    ttl_max = 0

    timestamps_ordenados = sorted(nos_por_tempo.keys())

    while fila:
        atual, tempo_atual, saltos = fila.pop()

        # Adicione esta verificação para limitar os saltos
        if saltos >= max_saltos:
            # print(f"Caminho descartado: {atual.id_no} excedeu {max_saltos} saltos.") # Opcional para debug
            continue

        visitados.add((atual.id_no, tempo_atual))

        if atual.id_no == destino.id_no:
            sucesso = True
            latencia = (tempo_atual - origem.timestamp).total_seconds()
            saltos_total = saltos
            break

        proximos = []
        for t in timestamps_ordenados:
            if t < tempo_atual:
                continue
            if (t - tempo_atual).total_seconds() > JANELA_TEMPO:
                break
            proximos.extend(nos_por_tempo[t])

        for vizinho in proximos:
            if (vizinho.id_no, vizinho.timestamp) in visitados:
                continue
            if not atual.pode_comunicar(vizinho, raio):
                continue
            if egoismo and vizinho.bateria < limite_bateria and not prioridade:
                continue
            # print("Contato possível:", atual.id_no, "->", vizinho.id_no,
            #       "Dist:", atual.distancia_para(vizinho))
            fila.append((vizinho, vizinho.timestamp, saltos + 1))

        ttl_max = max(ttl_max, len(proximos))

    return sucesso, latencia if sucesso else None, saltos_total if sucesso else None, ttl_max

def simular_experimento(nos, nos_por_tempo, N=100, D=500, R=10):
    resultados = {"caso_I": [], "caso_II": [], "caso_III": []}

    # Debug inicial: ver contatos reais
    # Debug inicial: ver contatos reais
    contatos = 0
    # Usaremos um conjunto para armazenar os pares de IDs de forma única
    # para cada timestamp (ex: (frozenset({1, 3}), datetime_obj))
    seen_contacts_for_debug_print = set()

    for t, lista in nos_por_tempo.items():
        # Para cada timestamp, compare todos os pares de nós
        for i in range(len(lista)):
            for j in range(i + 1, len(lista)):
                no1 = lista[i]
                no2 = lista[j]

                # Certifique-se de que os IDs são diferentes (para não comparar nó com ele mesmo)
                if no1.id_no == no2.id_no:
                    continue

                # Verifique se podem se comunicar
                if no1.pode_comunicar(no2, RAIO_COMUNICACAO):
                    # Crie uma chave única para o par de IDs (ordem não importa)
                    # Usamos frozenset para que possa ser um elemento de um set
                    pair_key = frozenset({no1.id_no, no2.id_no})

                    # Se este par de IDs neste timestamp ainda não foi impresso
                    if (pair_key, t) not in seen_contacts_for_debug_print:
                        contatos += 1
                        print(f"{no1.id_no} <-> {no2.id_no} no tempo {t}")
                        seen_contacts_for_debug_print.add((pair_key, t))

    print(f"Total de contatos possíveis (pares únicos de IDs por timestamp): {contatos}")


    for i in range(N):
        try:
            origem, destino = escolher_pares_validos(nos, D)
        except RuntimeError:
            print("Pares não encontrados na execução", i)
            continue
        
        print("Origem: ",origem.id_no, "Destino:",destino.id_no)
        r1 = simular_entrega(origem, destino, nos_por_tempo, R, egoismo=False)
        r2 = simular_entrega(origem, destino, nos_por_tempo, R, egoismo=True, prioridade=False, limite_bateria=LIMITE_BATERIA)
        r3 = simular_entrega(origem, destino, nos_por_tempo, R, egoismo=True, prioridade=True, limite_bateria=LIMITE_BATERIA)

        resultados["caso_I"].append(r1)
        resultados["caso_II"].append(r2)
        resultados["caso_III"].append(r3)

        print(f"Execução {i+1}/{N} concluída")
        print(f"Origem: {origem.id_no}, Destino: {destino.id_no}")
        print(f"  - Caso I: {'✓' if r1[0] else '✗'}, Saltos: {r1[2]}, Latência: {r1[1]}, TTL: {r1[3]}")
        print(f"  - Caso II: {'✓' if r2[0] else '✗'}, Saltos: {r2[2]}, Latência: {r2[1]}, TTL: {r2[3]}")
        print(f"  - Caso III: {'✓' if r3[0] else '✗'}, Saltos: {r3[2]}, Latência: {r3[1]}, TTL: {r3[3]}")

    return resultados

def calcular_metricas(resultados):
    for caso, tentativas in resultados.items():
        total = len(tentativas)
        entregues = [r for r in tentativas if r[0]]
        falhas = total - len(entregues)
        taxa_entrega = len(entregues) / total * 100 if total else 0
        latencias = [r[1] for r in entregues if r[1] is not None]
        saltos = [r[2] for r in entregues if r[2] is not None]
        ttl_total = sum([r[3] for r in tentativas])

        print(f"\n== Resultados para {caso} ==")
        print(f"Mensagens entregues: {len(entregues)}")
        print(f"Mensagens não entregues: {falhas}")
        print(f"TTL médio (densidade de vizinhos): {ttl_total / total:.2f}" if total else "Sem dados")
        print(f"Taxa de entrega: {taxa_entrega:.2f}%")
        print(f"Latência média: {sum(latencias)/len(latencias):.2f} segundos" if latencias else "Nenhuma entrega bem-sucedida")
        print(f"Número médio de saltos: {sum(saltos)/len(saltos):.2f}" if saltos else "Nenhuma entrega bem-sucedida")

if __name__ == "__main__":
    resultados = simular_experimento(nos, nos_por_tempo, N=N_EXECUCOES, D=D_MINIMA, R=RAIO_COMUNICACAO)
    calcular_metricas(resultados)
