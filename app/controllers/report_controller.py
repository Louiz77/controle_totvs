from flask import jsonify, send_file
from app.services.google_sheets_service import GoogleSheetsService
from app.services.pdf_service import PDFGenerator
import pandas as pd
import uuid

class ReportController:
    def __init__(self):
        self.google_sheets_service = GoogleSheetsService()

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