from flask import Blueprint, jsonify, request
import requests
from datetime import datetime
from app.controllers.chamado_controller import ChamadoController
from app.controllers.report_controller import ReportController
from config import Config

report_bp = Blueprint('report', __name__)
report_controller = ReportController()

chamados_bp = Blueprint('chamados', __name__)
chamado_controller = ChamadoController()

chamados_bp.add_url_rule('/chamados', 'get_all_chamados', chamado_controller.get_all_chamados, methods=['GET'])
chamados_bp.add_url_rule('/chamados', 'add_chamado', chamado_controller.add_chamado, methods=['POST'])

report_bp.add_url_rule('/generate', 'generate', report_controller.generate_report, methods=['GET'])

report_bp.add_url_rule(
    "/generate-monthly-report",
    "generate_monthly_report",
    report_controller.generate_monthly_report,
    methods=["GET"],
)

pipefy_bp = Blueprint('pipefy', __name__)

@pipefy_bp.route('/cards', methods=['GET'])
def get_pipefy_cards():
    try:
        print("Buscando dados do Pipefy para o dashboard...")
        PIPEFY_API_URL = "https://api.pipefy.com/graphql"
        HEADERS = {
            "Authorization": f"Bearer {Config.PIPEFY_KEY}"
        }

        query_template = """
        query ($pipeId: ID!, $after: String) {
          cards(pipe_id: $pipeId, first: 300, after: $after) {
            edges {
              node {
                id
                title
                fields {
                  name
                  value
                }
                current_phase {
                  name
                }
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """

        pipe_id = 303822738
        all_cards = []
        has_next_page = True
        after_cursor = None

        while has_next_page == True:
            variables = {"pipeId": pipe_id, "after": after_cursor}
            response = requests.post(
                PIPEFY_API_URL,
                json={"query": query_template, "variables": variables},
                headers=HEADERS,
            )
            response.raise_for_status()

            data = response.json()
            cards_data = data["data"]["cards"]
            all_cards.extend(cards_data["edges"])
            page_info = cards_data["pageInfo"]
            has_next_page = page_info["hasNextPage"]
            after_cursor = page_info["endCursor"]

        # Filtrar cards com "Componente" == "Suporte a Sistemas"
        suporte_cards = [
            card for card in all_cards
            if any(
                field["name"] == "Componente -> Suporte a Sistemas"
                and field["value"] in ["Meu RH", "TOTVS Datasul"]
                for field in card["node"]["fields"]
            )
               and card["node"]["current_phase"]["name"] != "Concluído"
        ]

        # Contar valores específicos no campo de seleção
        counts = {"Meu RH": 0, "TOTVS Datasul": 0}
        for card in suporte_cards:
            for field in card["node"]["fields"]:
                if field["name"] == "Componente -> Suporte a Sistemas" and field["value"] in counts:
                    counts[field["value"]] += 1
        # Organizar contagens por fase
        phases_count = {
            "triagem": sum(
                1 for card in suporte_cards if card["node"]["current_phase"]["name"] == "Triagem"
            ),
            "pendente": sum(
                1 for card in suporte_cards if card["node"]["current_phase"]["name"] == "Pendente"
            ),
            "em_atendimento": sum(
                1 for card in suporte_cards if card["node"]["current_phase"]["name"] == "Em atendimento"
            ),
            "escalar_chamado": sum(
                1 for card in suporte_cards if card["node"]["current_phase"]["name"] == "Escalar o Chamado"
            ),
        }
        return jsonify({
            "counts": counts,
            "phases_count": phases_count,
            "cards": suporte_cards,
        })

    except Exception as e:
        print(f"Erro ao buscar dados do Pipefy: {e}")
        return jsonify({"error": str(e)}), 500

@pipefy_bp.route('/cards_by_month', methods=['GET'])
def get_pipefy_cards_by_month():
    try:
        month = request.args.get('month')
        if not month:
            return jsonify({"error": "Mês não fornecido"}), 400

        PIPEFY_API_URL = "https://api.pipefy.com/graphql"
        HEADERS = {
            "Authorization": f"Bearer {Config.PIPEFY_KEY}"
        }

        query_template = """
        query ($pipeId: ID!, $after: String) {
          cards(pipe_id: $pipeId, first: 300, after: $after) {
            edges {
              node {
                id
                title
                fields {
                  name
                  value
                }
                current_phase {
                  name
                }
                created_at
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
        """

        pipe_id = 303822738
        all_cards = []
        has_next_page = True
        after_cursor = None

        while has_next_page:
            variables = {"pipeId": pipe_id, "after": after_cursor}
            response = requests.post(
                PIPEFY_API_URL,
                json={"query": query_template, "variables": variables},
                headers=HEADERS,
            )
            response.raise_for_status()

            data = response.json()
            cards_data = data["data"]["cards"]
            all_cards.extend(cards_data["edges"])
            page_info = cards_data["pageInfo"]
            has_next_page = page_info["hasNextPage"]
            after_cursor = page_info["endCursor"]

        # Filtrar cards pelo mês selecionado
        selected_month_cards = [
            card for card in all_cards
            if datetime.strptime(card["node"]["created_at"], "%Y-%m-%dT%H:%M:%S%z").month == int(month)
            and any(
                field["name"] == "Componente -> Suporte a Sistemas"
                and field["value"] in ["Meu RH", "TOTVS Datasul"]
                for field in card["node"]["fields"]
            )
        ]

        totals = {"Meu RH": 0, "TOTVS Datasul": 0}
        completed = {"Meu RH": 0, "TOTVS Datasul": 0}
        for card in selected_month_cards:
            for field in card["node"]["fields"]:
                if field["name"] == "Componente -> Suporte a Sistemas" and field["value"] in totals:
                    totals[field["value"]] += 1
                    if card["node"]["current_phase"]["name"] == "Concluído":
                        completed[field["value"]] += 1

        return jsonify({
            "totals": totals,
            "completed": completed,
        })

    except Exception as e:
        print(f"Erro ao buscar dados do Pipefy por mês: {e}")
        return jsonify({"error": str(e)}), 500