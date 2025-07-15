import re
import matplotlib.pyplot as plt

LOG_FILE = "log.txt"

# Inicializa estruturas
metricas = {}

with open(LOG_FILE, "r", encoding="utf-8") as f:
    texto = f.read()

# Regex para capturar blocos de resultados finais
padrao_caso = re.compile(
    r"== Resultados para (caso_\w+) ==\s+"
    r"Mensagens entregues: (\d+)\s+"
    r"Mensagens não entregues: (\d+)\s+"
    r"TTL médio.*?: ([\d\.]+)\s+"
    r"Taxa de entrega: ([\d\.]+)%\s+"
    r"Latência média: ([\d\.]+) segundos\s+"
    r"Número médio de saltos: ([\d\.]+)",
    re.MULTILINE
)

for match in padrao_caso.finditer(texto):
    caso = match.group(1)
    entregues = int(match.group(2))
    falhas = int(match.group(3))
    ttl = float(match.group(4))
    taxa = float(match.group(5))
    latencia = float(match.group(6))
    saltos = float(match.group(7))
    total = entregues + falhas

    metricas[caso] = {
        "entregues": entregues,
        "total": total,
        "taxa_entrega": taxa,
        "latencia_media": latencia,
        "saltos_medios": saltos,
        "ttl_medio": ttl
    }

# === Exibir no terminal ===
print("\nResumo das métricas finais:")
for caso, m in metricas.items():
    print(f"\n== {caso} ==")
    print(f"Entregues: {m['entregues']}/{m['total']}")
    print(f"Taxa de entrega: {m['taxa_entrega']:.2f}%")
    print(f"Latência média: {m['latencia_media']:.2f} s")
    print(f"Saltos médios: {m['saltos_medios']:.2f}")
    print(f"TTL médio: {m['ttl_medio']:.2f}")

# === Gráfico ===
def plotar(metricas, salvar=True):
    casos = list(metricas.keys())
    taxas = [metricas[c]["taxa_entrega"] for c in casos]

    plt.figure(figsize=(8,5))
    plt.bar(casos, taxas, color=["green", "orange", "red"])
    plt.title("Taxa de entrega por cenário")
    plt.ylabel("Taxa de entrega (%)")
    plt.ylim(0, 100)
    plt.grid(axis='y')
    if salvar:
        plt.savefig("taxa_entrega_final.png", dpi=300)
    plt.show()

plotar(metricas)
