from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel
from uuid import uuid1


class Db:

    def __init__(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName("./postbot.db")
        db.open()
        self.db = db

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def __enter__(self):
        return self.db


class TabStorage:
    """store page data"""
    def __init__(self):
        self.data = {}
        self.load()

    def load(self) -> None:
        """load data from db(perhaps)"""
        pass

    def put(self, tab_key: str, data_key: str, data):
        self.data[tab_key][data_key] = data

    def new_tab(self) -> str:
        uuid = uuid1()
        self.data[uuid] = {}
        return str(uuid)

    def __len__(self):
        return len(self.data)

