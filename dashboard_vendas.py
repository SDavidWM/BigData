# dashboard_vendas.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ---------------------------
# Textos (use os textos que você já forneceu)
# ---------------------------
TEXTO_VENDEDOR = """O gráfico apresentado ilustra os 10 vendedores com maior volume de vendas no período analisado. Cada barra representa o valor total vendido por vendedor, permitindo uma comparação clara entre os desempenhos individuais.

Os dados mostram que os vendedores identificados como 31, 33 e 32 se destacaram como os mais produtivos, com volumes de vendas significativamente superiores aos demais. O vendedor 31, em particular, ultrapassou a marca de R$ 250.000, seguido de perto pelo vendedor 33 com cerca de R$ 235.000. Esses resultados indicam uma forte concentração de vendas em poucos profissionais, o que pode sugerir:

- Maior experiência ou carteira de clientes desses vendedores;
- Regiões com maior potencial de mercado;
- Estratégias de venda mais eficazes.

Em contrapartida, os vendedores nas últimas posições (ex: 54, 58 e 71) apresentam um volume de vendas visivelmente inferior, com menos de R$ 70.000. Isso pode indicar a necessidade de suporte adicional, treinamento ou redistribuição de metas.
"""

TEXTO_MES = """Este gráfico de linha apresenta a evolução do total de vendas ao longo dos meses, abrangendo o período de novembro de 2013 a maio de 2015. A linha azul indica a variação no volume mensal de vendas, permitindo identificar tendências sazonais e mudanças no desempenho ao longo do tempo.

Observa-se que o faturamento manteve-se relativamente estável entre o final de 2013 e o primeiro semestre de 2014, com médias entre R$ 135.000 e R$ 150.000. A partir de julho de 2014, houve uma tendência de crescimento, atingindo o pico em dezembro de 2014, com um valor próximo de R$ 210.000.

Contudo, nos meses seguintes — especialmente em abril e maio de 2015 — há uma queda brusca nas vendas, culminando em quase R$ 0 em maio. Essa queda pode ter diversas causas, como:

- Problemas operacionais ou logísticos;
- Mudanças no sistema de vendas ou no produto;
- Falhas na coleta de dados recentes;
- Fatores sazonais ou externos (como crises econômicas).

O gráfico revela uma fase de crescimento sustentado em 2014, seguida de queda abrupta em 2015, que merece investigação.
"""

TEXTO_PRODUTOS = """O gráfico apresentado ilustra os 10 produtos com maior volume de vendas no período analisado. Cada barra representa o valor total vendido por produto, permitindo uma comparação clara entre os desempenhos.

Os dados mostram que os produtos com os códigos que representam os três primeiros lugares se destacaram com volumes de vendas superiores a R$ 19 milhões. O produto líder atingiu a marca de R$ 19.830.959,00, seguido de perto pelo segundo colocado com R$ 19.574.877,47. Esses resultados indicam uma forte concentração de receita nos produtos mais populares, o que pode sugerir:

- Alta demanda ou reconhecimento de marca desses produtos;
- Estratégias de precificação ou promoção eficazes;
- Possível sazonalidade ou apelo massivo ao público-alvo.

Em contrapartida, os produtos nas últimas posições (ex: 9º e 10º) apresentam um volume de vendas inferior a R$ 10 milhões, com valores próximos a R$ 9,1 milhões e R$ 8,5 milhões, respectivamente. Essa disparidade pode indicar a necessidade de:

- Revisão do mix de produtos;
- Campanhas de incentivo para itens com menor desempenho;
- Análise de sazonalidade ou ciclo de vida do produto.
"""

# ---------------------------
# Carregar e processar dados (chunks para memória pequena)
# ---------------------------
CSV_PATH = "bd.csv"  # deve estar na mesma pasta do script

def load_data_chunks(path=CSV_PATH, chunksize=100000):
    vendas_vendedores = {}
    vendas_por_mes = {}
    vendas_produtos = {}

    for chunk in pd.read_csv(path, encoding="latin1", sep=";", chunksize=chunksize, on_bad_lines="skip"):
        # PRECO_VENDA -> float
        chunk["PRECO_VENDA"] = chunk["PRECO_VENDA"].astype(str).str.replace(",", ".", regex=False).astype(float)

        # vendedores
        g_vend = chunk.groupby("VENDEDOR")["PRECO_VENDA"].sum()
        for k, v in g_vend.items():
            vendas_vendedores[k] = vendas_vendedores.get(k, 0) + v

        # mês
        chunk["DATA"] = pd.to_datetime(chunk["DATA"], format="%d/%m/%Y", errors="coerce")
        chunk["ANO_MES"] = chunk["DATA"].dt.to_period("M")
        g_mes = chunk.groupby("ANO_MES")["PRECO_VENDA"].sum()
        for k, v in g_mes.items():
            vendas_por_mes[k] = vendas_por_mes.get(k, 0) + v

        # produtos (se houver QUANTIDADE)
        if "QUANTIDADE" in chunk.columns and "CODPROD" in chunk.columns:
            chunk["QUANTIDADE"] = chunk["QUANTIDADE"].astype(str).str.replace(",", ".", regex=False).astype(float)
            chunk["VALOR_TOTAL"] = chunk["PRECO_VENDA"] * chunk["QUANTIDADE"]
            g_prod = chunk.groupby("CODPROD")["VALOR_TOTAL"].sum()
            for k, v in g_prod.items():
                vendas_produtos[k] = vendas_produtos.get(k, 0) + v

    # Series formatados
    s_vendedores = pd.Series(vendas_vendedores).sort_values(ascending=False).head(10)
    s_mes = pd.Series(vendas_por_mes).sort_index()
    s_produtos = pd.Series(vendas_produtos).sort_values(ascending=False).head(10)
    return s_vendedores, s_mes, s_produtos

# ---------------------------
# Funções de plot (mantêm estilo original)
# ---------------------------
def plot_vendedores(ax, series):
    sns.barplot(x=series.index, y=series.values, palette="viridis", ax=ax)
    ax.set_title("Top 10 Vendedores por Total de Vendas", fontsize=14)
    ax.set_xlabel("Vendedor")
    ax.set_ylabel("Total de Vendas (R$)")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

def plot_meses(ax, series):
    ax.plot(series.index.astype(str), series.values, marker="o", linestyle="-", color="blue")
    ax.set_title("Total de Vendas por Mês", fontsize=14)
    ax.set_xlabel("Mês")
    ax.set_ylabel("Total de Vendas (R$)")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(alpha=0.5)

def plot_produtos(ax, series):
    sns.barplot(x=series.index, y=series.values, palette="mako", ax=ax)
    ax.set_title("Top 10 Produtos Mais Vendidos", fontsize=14)
    ax.set_xlabel("Código do Produto")
    ax.set_ylabel("Total Vendido (R$)")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    # labels on bars
    for i, v in enumerate(series.values):
        ax.text(i, v + (v * 0.01), f"R$ {v:,.2f}", ha="center", fontsize=9)

# ---------------------------
# Interface Tkinter
# ---------------------------
class DashboardApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Relatórios de Vendas")
        self.frame_top = ttk.Frame(master)
        self.frame_top.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        # Botões
        btn_vend = ttk.Button(self.frame_top, text="Top Vendedores", command=self.show_vendedores)
        btn_mes = ttk.Button(self.frame_top, text="Vendas por Mês", command=self.show_meses)
        btn_prod = ttk.Button(self.frame_top, text="Top Produtos", command=self.show_produtos)
        btn_vend.pack(side=tk.LEFT, padx=4)
        btn_mes.pack(side=tk.LEFT, padx=4)
        btn_prod.pack(side=tk.LEFT, padx=4)

        # Área do gráfico
        self.plot_frame = ttk.Frame(master)
        self.plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Matplotlib Figure
        self.fig, self.ax = plt.subplots(figsize=(10, 5))
        plt.tight_layout()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Área de texto com scrollbar
        self.text_frame = ttk.Frame(master)
        self.text_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=6)
        self.text_widget = tk.Text(self.text_frame, height=10, wrap="word")
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.text_widget.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.configure(yscrollcommand=self.scrollbar.set)

        # Carrega dados (uma vez)
        self.s_vendedores, self.s_mes, self.s_produtos = load_data_chunks()

        # mostra inicialmente o primeiro gráfico
        self.show_vendedores()

    def clear_plot(self):
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)

    def clear_text(self):
        self.text_widget.config(state="normal")
        self.text_widget.delete("1.0", tk.END)

    def show_vendedores(self):
        self.clear_plot()
        plot_vendedores(self.ax, self.s_vendedores)
        self.canvas.draw()
        self.clear_text()
        self.text_widget.insert(tk.END, TEXTO_VENDEDOR)
        self.text_widget.config(state="disabled")

    def show_meses(self):
        self.clear_plot()
        plot_meses(self.ax, self.s_mes)
        self.canvas.draw()
        self.clear_text()
        self.text_widget.insert(tk.END, TEXTO_MES)
        self.text_widget.config(state="disabled")

    def show_produtos(self):
        self.clear_plot()
        plot_produtos(self.ax, self.s_produtos)
        self.canvas.draw()
        self.clear_text()
        self.text_widget.insert(tk.END, TEXTO_PRODUTOS)
        self.text_widget.config(state="disabled")

def main():
    root = tk.Tk()
    root.geometry("1000x800")
    app = DashboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
