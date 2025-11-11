import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

chunksize = 100000
vendas_totais = {}

for chunk in pd.read_csv("bd.csv", encoding="latin1", sep=";", chunksize=chunksize, on_bad_lines="skip"):
    #converte a coluna PRECO_VENDA para floar
    chunk["PRECO_VENDA"] = (
        chunk["PRECO_VENDA"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    
    #parte que faz o agrupamento por vendedor (RCA)
    chunk_group = chunk.groupby("VENDEDOR")["PRECO_VENDA"].sum()
    
    for vendedor, valor in chunk_group.items():
        vendas_totais[vendedor] = vendas_totais.get(vendedor, 0) + valor

vendas_por_vendedor = pd.Series(vendas_totais).sort_values(ascending=False).head(10)

#para mostrar a tabela antes do grafico
print(vendas_por_vendedor)

#grafico 
plt.figure(figsize=(12, 6))
sns.barplot(x=vendas_por_vendedor.index, y=vendas_por_vendedor.values, palette="viridis")
plt.title("Top 10 Vendedores por Total de Vendas", fontsize=16)
plt.xlabel("Vendedor", fontsize=12)
plt.ylabel("Total de Vendas (R$)", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()
