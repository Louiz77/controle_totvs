from flask import jsonify, send_file, request
from app.services.google_sheets_service import GoogleSheetsService
from app.services.pdf_service import PDFGenerator
from app.services.pdf_service import MonthlyPDFReport
from app.services.pipefy_service import PipefyService
import pandas as pd
import uuid
import re

class ReportController:
    def __init__(self):
        self.google_sheets_service = GoogleSheetsService()
        self.pipefy_service = PipefyService()

    def generate_report(self):
        try:
            id_user_uuid = str(uuid.uuid4())
            # Obter dados da planilha
            records = self.google_sheets_service.get_all_chamados()

            if not records:
                return jsonify({"error": "Nenhum dado encontrado na planilha."}), 404

            # Converter dados em DataFrame para facilitar o processamento
            data = pd.DataFrame(records)

            # Gerar o PDF
            pdf_generator = PDFGenerator(data)
            output_file = (f"{id_user_uuid}_output_file")
            pdf_generator.generate_pdf(output_file)

            # Retornar o arquivo gerado
            return send_file(output_file, as_attachment=True)
        except Exception as e:
            print(f"Erro ao gerar o relatório: {e}")
            return jsonify({"error": str(e)}), 500

    def generate_monthly_report(self):
        try:
            month = request.args.get("month")
            if not month or not re.match(r"^\d{4}-\d{2}$", month):
                return jsonify({"error": "Mês inválido ou não especificado"}), 400

            data, graphs = self.pipefy_service.get_monthly_data(month)
            if not data.get("total_cards"):
                print(data)
                return jsonify({"error": "Nenhum dado encontrado para o mês selecionado"}), 404

            pdf_generator = MonthlyPDFReport(data, graphs, month)
            output_file = f"relatorio_mensal_{month}.pdf"
            pdf_generator.generate_pdf(output_file)

            return send_file(output_file, as_attachment=True)

        except Exception as e:
            print(f"Erro ao gerar o relatório mensal: {e}")
            return jsonify({"error": str(e)}), 500