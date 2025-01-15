from flask import jsonify, request
from app.models.chamado import Chamado
from app.services.google_sheets_service import GoogleSheetsService

class ChamadoController:
    def __init__(self):
        self.google_sheets_service = GoogleSheetsService()

    def add_chamado(self):
        try:
            data = request.json
            chamado = Chamado(
                descricao_analista=data['descricaoAnalista'],
                data=data['data'],
                solicitante=data['solicitante'],
                descricao_solicitacao=data['descricaoSolicitacao'],
                hora_inicial=data['horaInicial'],
                hora_final=data['horaFinal']
            )
            self.google_sheets_service.add_chamado(chamado)
            return jsonify({"message": "Chamado registrado com sucesso!"}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_all_chamados(self):
        try:
            chamados = self.google_sheets_service.get_all_chamados()

            # Corrigir o valor de TOTAL para exibir adequadamente
            for chamado in chamados:
                if "TOTAL" in chamado:
                    try:
                        total_value = float(chamado["TOTAL"]) / 100
                        # Verifica se o número é inteiro ou decimal e formata apropriadamente
                        chamado["TOTAL"] = int(total_value) if total_value.is_integer() else round(total_value, 2)
                    except ValueError:
                        chamado["TOTAL"] = None
                if "totalHoras" in chamado:
                    try:
                        total_value = float(chamado["totalHoras"]) / 100
                        # Verifica se o número é inteiro ou decimal e formata apropriadamente
                        chamado["totalHoras"] = int(total_value) if total_value.is_integer() else round(total_value, 2)
                    except ValueError:
                        chamado["totalHoras"] = None
            return jsonify(chamados), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500