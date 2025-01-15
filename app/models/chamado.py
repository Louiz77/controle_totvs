from datetime import datetime

class Chamado:
    def __init__(self, descricao_analista, data, solicitante, descricao_solicitacao, hora_inicial, hora_final):
        self.descricao_analista = descricao_analista
        self.data = data
        self.solicitante = solicitante
        self.descricao_solicitacao = descricao_solicitacao
        self.hora_inicial = hora_inicial
        self.hora_final = hora_final

    def to_dict(self):
        """Converte os dados do chamado em um dicionário."""
        total_horas = self.calcular_total_horas()
        return {
            "DescricaoAnalista": self.descricao_analista,
            "Data": self.data,
            "Solicitante": self.solicitante,
            "DescricaoSolicitacao": self.descricao_solicitacao,
            "HoraInicial": self.hora_inicial,
            "HoraFinal": self.hora_final,
            "TotalHoras": total_horas
        }

    def calcular_total_horas(self):
        """Calcula o total de horas com base nos horários."""
        try:
            hora_inicial = datetime.strptime(self.hora_inicial, '%H:%M')
            hora_final = datetime.strptime(self.hora_final, '%H:%M')
            diferenca = hora_final - hora_inicial
            total_horas = diferenca.total_seconds() / 3600
            return round(total_horas, 2) if total_horas > 0 else 0
        except Exception as e:
            return str(e)