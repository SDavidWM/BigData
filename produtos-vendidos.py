import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Caminho relativo (CSV está na mesma pasta do script)
caminho_arquivo = os.path.join(os.path.dirname(__file__), "bd.csv")

chunksize = 100000
vendas_produtos = {}

# Leitura em chunks
for chunk in pd.read_csv(caminho_arquivo, encoding="latin1", sep=";", chunksize=chunksize, on_bad_lines="skip"):
    # Converte PRECO_VENDA para float
    chunk["PRECO_VENDA"] = (
        chunk["PRECO_VENDA"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # Converte QUANTIDADE para float
    chunk["QUANTIDADE"] = (
        chunk["QUANTIDADE"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    # Calcula o valor total vendido por produto
    chunk["VALOR_TOTAL"] = chunk["PRECO_VENDA"] * chunk["QUANTIDADE"]

    # Agrupa por produto
    chunk_group = chunk.groupby("CODPROD")["VALOR_TOTAL"].sum()

    # Soma os valores entre os chunks
    for codprod, valor in chunk_group.items():
        vendas_produtos[codprod] = vendas_produtos.get(codprod, 0) + valor

# Top 10 produtos mais vendidos
vendas_por_produto = pd.Series(vendas_produtos).sort_values(ascending=False).head(10)

# Mostra tabela
print("\nTop 10 Produtos Mais Vendidos:")
print(vendas_por_produto)

# Gráfico
plt.figure(figsize=(12, 6))
sns.barplot(x=vendas_por_produto.index, y=vendas_por_produto.values, palette="mako")
plt.title("Top 10 Produtos Mais Vendidos", fontsize=16, fontweight="bold")
plt.xlabel("Código do Produto", fontsize=12)
plt.ylabel("Total Vendido (R$)", fontsize=12)
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.7)

# Rótulos nas barras
for i, v in enumerate(vendas_por_produto.values):
    plt.text(i, v + (v * 0.01), f"R$ {v:,.2f}", ha="center", fontsize=9)

plt.tight_layout()
plt.show()
