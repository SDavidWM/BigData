import pandas as pd
import matplotlib.pyplot as plt

chunksize = 100000
vendas_por_mes = {}

for chunk in pd.read_csv("bd.csv", encoding="latin1", sep=";", chunksize=chunksize, on_bad_lines="skip"):
    chunk["PRECO_VENDA"] = (
        chunk["PRECO_VENDA"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    chunk["DATA"] = pd.to_datetime(chunk["DATA"], format="%d/%m/%Y", errors="coerce")
    chunk["ANO_MES"] = chunk["DATA"].dt.to_period("M")

    chunk_group = chunk.groupby("ANO_MES")["PRECO_VENDA"].sum()

    for mes, valor in chunk_group.items():
        vendas_por_mes[mes] = vendas_por_mes.get(mes, 0) + valor

vendas_por_mes = pd.Series(vendas_por_mes).sort_index()

plt.figure(figsize=(14, 6))
plt.plot(vendas_por_mes.index.astype(str), vendas_por_mes.values, marker="o", linestyle="-")
plt.title("Total de Vendas por Mês", fontsize=16)
plt.xlabel("Mês", fontsize=12)
plt.ylabel("Total de Vendas (R$)", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.grid(alpha=0.5)
plt.tight_layout()
plt.show()

