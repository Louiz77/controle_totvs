import gspread
from google.oauth2.service_account import Credentials
from config import Config

class GoogleSheetsService:
    def __init__(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.creds = Credentials.from_service_account_file(Config.GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=scopes)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open_by_key(Config.GOOGLE_SHEET_ID).sheet1

    def add_chamado(self, chamado):
        """Adiciona um novo chamado à planilha."""
        chamado_data = chamado.to_dict()
        values = list(chamado_data.values())
        try:
            self.sheet.append_row(values)
        except Exception as e:
            raise Exception(f"Erro ao adicionar o chamado: {e}")

    def get_all_chamados(self):
        """Recupera todos os chamados registrados na planilha."""
        try:
            return self.sheet.get_all_records()
        except Exception as e:
            raise Exception(f"Erro ao buscar chamados: {e}")
