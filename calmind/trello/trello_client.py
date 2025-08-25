import requests
from trello import TrelloClient
from dotenv import load_dotenv

load_dotenv()

class TrelloCard:
    def __init__(self, name, description, url):
        self.name = name
        self.description = description
        self.url = url

    def __str__(self):
        return f"Name: {self.name}\nDescription: {self.description}\nURL: {self.url}\n---"

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
        }

class TrelloService:
    def __init__(self, api_key, api_token, board_id):
        self.client = TrelloClient(
            api_key=api_key,
            token=api_token,
        )
        # If you are encountering SSL issues on macOS, you can try to uncomment the following lines
        # to disable SSL verification. This is not recommended for production environments.
        # session = requests.Session()
        # session.verify = False
        # self.client.http_service.session = session
        self.board_id = board_id

    def get_cards(self):
        board = self.client.get_board(self.board_id)
        cards = board.all_cards()
        trello_cards = []
        for card in cards:
            trello_cards.append(
                TrelloCard(
                    name=card.name,
                    description=card.description,
                    url=card.url,
                )
            )
        return trello_cards