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
        pdf.ln(20)

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

        try:
            for total in self.data['TOTAL']:
                total_value = float(total) / 100
                total = int(total_value) if total_value.is_integer() else round(total_value, 2)
                pdf.cell(200, 10, txt=f"Quantidade total de horas faturadas: {total}", ln=True, align="C")
                pdf.ln(10)
        except ValueError:
            pass

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

class MonthlyPDFReport:
    def __init__(self, data, graphs, month):
        """
        Inicializa o gerador de relatório PDF.
        :param data: Dados relevantes para o relatório.
        :param graphs: Gráficos gerados pelo frontend.
        """
        self.data = data
        self.graphs = graphs
        self.month = month

    def generate_pdf(self, output_file):
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)

            # Página Inicial
            pdf.add_page()
            pdf.set_font("Arial", style="B", size=16)
            pdf.cell(0, 10, f"Relatório Mensal de Chamados | {self.month}", ln=True, align="C")
            pdf.ln(10)
            pdf.image("IT-Facil---logo---alta-47c0885e-6390534b-1920w.png", x=10, y=18, w=50)
            pdf.image("totvs-logo.png", x=150, y=24, w=50)
            pdf.ln(30)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, f"Este relatório apresenta uma visão geral dos chamados do mês selecionado ({self.month}), incluindo métricas importantes como: Quantidade de cards, informações gerais, gráficos etc")

            pdf.ln(5)
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(0, 10, "Informações Gerais do Mês", ln=True, align="C")
            pdf.ln(5)
            pdf.set_font("Arial", size=12)

            pdf.cell(0, 10, f"Total de cards no mês: {self.data['total_cards']}", ln=True)
            pdf.multi_cell(0, 10, (
                f"- Destes, {self.data['counts']['Meu RH']} são relacionados ao Meu RH.\n"
                f"- {self.data['counts']['TOTVS Datasul']} são relacionados ao TOTVS Datasul."
            ))
            pdf.ln(5)

            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(0, 10, f"Fases atuais dos cards do mês selecionado ({self.month}):", ln=True, align="C")
            pdf.set_font("Arial", size=12)
            for phase, count in self.data['phases_count'].items():
                pdf.cell(0, 10, f"Fase {phase}: {count}", ln=True)
                pdf.ln(3)

            # Títulos dos Cards Concluídos
            pdf.add_page()
            pdf.set_font("Arial", style="B", size=14)
            pdf.cell(0, 10, "Títulos dos Cards Concluídos", ln=True, align="C")
            pdf.ln(5)
            pdf.set_font("Arial", size=12)

            if self.data["cards"]:
                pdf.multi_cell(0, 10, (
                    "Abaixo estão listados os títulos dos cards concluídos no mês selecionado. "
                    "Os links podem ser usados para acessar diretamente os cards no sistema Pipefy."
                ))
                pdf.ln(5)

                # Verifica se self.data["cards"] é uma lista de dicionários
                if isinstance(self.data["cards"], list):
                    for card in self.data["cards"]:
                        if card:
                            pdf.multi_cell(0, 10, (
                                f"- {card['node']['title']} (ID: {card['node']['id']})\n"
                                f"  Link: https://app.pipefy.com/open-cards/{card['node']['id']}\n"
                            ))
                        else:
                            print(f"Erro: Card não possui os campos esperados: {card["node"]}")
            else:
                pdf.cell(0, 10, "Não há cards concluídos no mês selecionado.", ln=True)

            # Gráficos
            for graph in self.graphs:
                chart_path = f"{graph['title'].replace(' ', '_')}.png"
                self.generate_chart(graph, chart_path)
                pdf.add_page()
                pdf.set_font("Arial", style="B", size=14)
                pdf.cell(0, 10, graph["title"], ln=True, align="L")
                pdf.ln(5)
                pdf.image(chart_path, x=30, y=None, w=150)

            # Data do Relatório
            pdf.add_page()
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(0, 10, f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="L")
            print('finalizou pdf')
            pdf.output(output_file)

        except Exception as e:
            print(e)

    def generate_chart(self, graph, output_path):
        import matplotlib.pyplot as plt

        plt.figure(figsize=(10, 6))
        plt.bar(graph["labels"], graph["values"], color=graph["colors"])
        plt.title(graph["title"])
        plt.xlabel(graph["xlabel"])
        plt.ylabel(graph["ylabel"])
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()