import os
from pathlib import Path

class Database():
    def __init__(self, db_file):
        self.db_file = db_file
        self.name = os.path.basename(db_file).replace(".db", "")

        self.tables = []