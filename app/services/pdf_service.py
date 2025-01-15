import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF

class PDFGenerator:
    def __init__(self, data):
        self.data = data

    def generate_bar_chart(self, output_path, column_name, title, xlabel, ylabel):
        """Gera um gráfico de barras e salva como imagem."""
        chart_data = self.data[column_name].value_counts()

        plt.figure(figsize=(10, 6))
        chart_data.plot(kind='bar', color='skyblue')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()

        plt.savefig(output_path)
        plt.close()

    def add_styled_intro_page(self, pdf):
        """Adiciona uma página inicial estilizada ao PDF."""
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        #imagens itfacil e totvs
        pdf.image("IT-Facil---logo---alta-47c0885e-6390534b-1920w.png", x=10, y=8, w=50)
        pdf.image("totvs-logo.png", x=150, y=8, w=50)
        pdf.ln(30)

        #titulo do doc
        pdf.set_font("Arial", style="B", size=24)
        pdf.cell(0, 10, txt="Relatório de Controle de Chamados TOTVS", ln=True, align="C")
        pdf.ln(10)

        #texto inciial
        pdf.set_font("Arial", size=12)
        intro_text = (
            "Este documento apresenta um resumo detalhado dos chamados faturados "
            "da TOTVS, fornecendo uma visão geral dos dados, análises e gráficos. "
            "O objetivo é oferecer informações claras e objetivas para a gestão e "
            "tomada de decisões baseadas nos números apresentados."
        )
        pdf.multi_cell(0, 10, intro_text, align="J")
        pdf.ln(10)

        pdf.set_font("Arial", style="I", size=10)
        pdf.cell(0, 10, txt=f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="R")
        pdf.ln(20)  # Espaçamento antes de começar o conteúdo

    def generate_pdf(self, output_file):
        """Gera um PDF com as informações da planilha."""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        #initial page
        self.add_styled_intro_page(pdf)

        #add tabela
        pdf.add_page()
        pdf.set_font("Arial", style="B", size=16)
        pdf.cell(200, 10, txt="Tabela Resumo dos Chamados", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", size=10)
        headers = ["Descrição Analista", "Data", "Solicitante", "Descrição", "Hora Inicial", "Hora Final"]
        col_widths = [60, 20, 25, 50, 20, 20]

        #header
        for header, col_width in zip(headers, col_widths):
            pdf.cell(col_width, 10, header, border=1, align="C")
        pdf.ln()

        #dados para iterar
        for _, row in self.data.iterrows():
            pdf.cell(60, 10, row['descricaoAnalista'], border=1)
            pdf.cell(20, 10, row['data'], border=1)
            pdf.cell(25, 10, row['solicitante'], border=1)
            pdf.cell(50, 10, row['descricaoSolicitacao'], border=1)
            pdf.cell(20, 10, row['horaInicial'], border=1)
            pdf.cell(20, 10, row['horaFinal'], border=1)
            pdf.ln()

        #insercao do chart na page
        pdf.add_page()
        pdf.cell(200, 10, txt="Gráficos de Análise TOTVS", ln=True, align="C")
        pdf.ln(10)

        #chart de barra
        chart_path = "chart_bar.png"
        self.generate_bar_chart(
            chart_path,
            column_name="solicitante",
            title="Quantidade de Chamados por Solicitante",
            xlabel="Solicitantes",
            ylabel="Quantidade de Chamados"
        )

        pdf.image(chart_path, x=30, y=None, w=150)
        os.remove(chart_path)

        # ultima page
        pdf.add_page()
        pdf.cell(200, 10, txt="Obrigado por utilizar o controle de chamados TOTVS.", ln=True, align="C")
        pdf.cell(200, 10, txt="Desenvolvido por:", ln=True, align="L")
        pdf.cell(200, 10, txt="ITFácil", ln=True, align="L")
        pdf.cell(200, 10, txt="Luiz Gustavo Sousa", ln=True, align="L")
        pdf.ln(10)
        pdf.cell(200, 10, txt=f"Relatório gerado: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="C")
        pdf.output(output_file)
        return output_file