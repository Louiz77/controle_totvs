import requests
from config import Config
from datetime import datetime

class PipefyService:
    def __init__(self):
        self.api_url = "https://api.pipefy.com/graphql"
        self.headers = {
            "Authorization": f"Bearer {Config.PIPEFY_KEY}"
        }

    def fetch_all_cards(self, pipe_id, filters=None):
        """
        Busca todos os cards do Pipefy em um pipe específico com paginação.
        :param pipe_id: ID do pipe no Pipefy.
        :param filters: Filtros opcionais para a busca.
        :return: Lista de cards.
        """
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
        all_cards = []
        has_next_page = True
        after_cursor = None

        while has_next_page:
            variables = {"pipeId": pipe_id, "after": after_cursor}
            response = requests.post(
                self.api_url,
                json={"query": query_template, "variables": variables},
                headers=self.headers,
            )
            response.raise_for_status()

            data = response.json()
            cards_data = data["data"]["cards"]
            all_cards.extend(cards_data["edges"])
            page_info = cards_data["pageInfo"]
            has_next_page = page_info["hasNextPage"]
            after_cursor = page_info["endCursor"]

        if filters:
            all_cards = self.filter_cards(all_cards, filters)
        return all_cards

    def filter_cards(self, cards, filters):
        """
        Filtra os cards com base nos critérios especificados.
        :param cards: Lista de cards.
        :param filters: Dicionário de filtros.
        :return: Lista filtrada de cards.
        """
        filtered_cards = []

        for card in cards:
            match = True
            for field_name, field_value in filters.items():
                field_match = any(
                    field["name"] == field_name and field["value"] == field_value
                    for field in card["node"]["fields"]
                )
                if not field_match:
                    match = False
                    break

            if match:
                filtered_cards.append(card)

        return filtered_cards

    def get_monthly_data(self, month):
        """
        Recupera dados e gráficos para o relatório mensal.
        Considera somente cards onde:
        - field["name"] == "Componente -> Suporte a Sistemas"
        - field["value"] in ["TOTVS Datasul", "Meu RH"]
        - O mês corresponde ao campo "created_at".
        :param month: Mês no formato "YYYY-MM".
        :return: Dados e gráficos processados.
        """
        pipe_id = 303822738
        all_cards = self.fetch_all_cards(pipe_id)

        # Filtrar por mês selecionado e critérios específicos
        selected_month_cards = []
        for card in all_cards:
            card_created_at = card["node"].get("created_at")
            if not card_created_at:
                continue

            # Converter e verificar o mês
            try:
                card_month = datetime.strptime(card_created_at, "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m")
            except ValueError as e:
                print(f"Erro ao converter data para card ID {card['node']['id']}: {e}")
                continue

            if card_month != month:
                continue

            # Verificar campo "Componente -> Suporte a Sistemas"
            if any(
                    field["name"] == "Componente -> Suporte a Sistemas"
                    and field["value"] in ["Meu RH", "TOTVS Datasul"]
                    for field in card["node"]["fields"]
            ):
                selected_month_cards.append(card)

        # Inicializar contagens
        counts = {"Meu RH": 0, "TOTVS Datasul": 0}
        phases_count = {}
        concluded_cards = []

        # Processar cards filtrados
        for card in selected_month_cards:
            phase_name = card["node"]["current_phase"]["name"]

            # Contar por fases
            phases_count[phase_name] = phases_count.get(phase_name, 0) + 1

            # Adicionar títulos de cards concluídos que atendem aos critérios
            if phase_name == "Concluído" and any(
                    field["name"] == "Componente -> Suporte a Sistemas"
                    and field["value"] in ["Meu RH", "TOTVS Datasul"]
                    for field in card["node"]["fields"]
            ):
                concluded_cards.append(card["node"]["title"])

            # Contar por tipo de solicitação
            for field in card["node"]["fields"]:
                if field["name"] == "Componente -> Suporte a Sistemas" and field["value"] in counts:
                    counts[field["value"]] += 1

        # Preparar gráficos
        graphs = [
            {
                "title": "Distribuição por Tipo",
                "labels": list(counts.keys()),
                "values": list(counts.values()),
                "colors": ["blue", "green"],
                "xlabel": "Tipo",
                "ylabel": "Quantidade",
            },
            {
                "title": "Cards por Fase",
                "labels": list(phases_count.keys()),
                "values": list(phases_count.values()),
                "colors": ["purple", "orange", "cyan", "red", "yellow"],
                "xlabel": "Fase",
                "ylabel": "Quantidade",
            },
        ]

        return {
            "total_cards": len(selected_month_cards),
            "counts": counts,
            "phases_count": phases_count,
            "concluded_titles": concluded_cards,
            "cards": selected_month_cards,
        }, graphs