from No import *
import pandas as pd

DATASET_FILE = "dataset_final_29.06.25.txt"

# Carregando o CSV
df = pd.read_csv(DATASET_FILE, delimiter=";", header=None)

# Renomeando colunas (opcional)
df.columns = [
    "ID", "Data", "Hora", "Localizacao", "Bateria",
    "Memoria Int", "Memoria Ext", "Wi-Fi", "Bluetooth",
    "Conexao", "P2P", "Roteadores"
]

# Criando lista de objetos No
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
    print(no)
    nos.append(no)


