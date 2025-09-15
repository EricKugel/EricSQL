import os
from pathlib import Path

import json

from logic.table import Table

class DatabaseException(Exception):
    pass

def create_blank(db_file, name):
    with open(db_file, "w") as file:
        file.write(json.dumps({"name": name, "tables": {}}))

class Database():
    def __init__(self, db_file):
        self.db_file = db_file
        self.name = os.path.basename(db_file).replace(".db", "")

        file = open(db_file, "r")
        start = file.read(1)
        file.close()
        if start == "":
            create_blank(self.db_file, self.name)

        self.read_in()

    def read_in(self):
        data = {}
        with open(self.db_file, "r") as file:
            data = json.loads(file.read())
        self.name = data["name"]
        self.tables = dict({(name, Table(name, data)) for name, data in data["tables"].items()})

    def write_out(self):
        data = {"name": self.name, "tables": {}}
        for name, table in self.tables.items():
            data["tables"][name] = table.write_out()

        with open(self.db_file, "w") as file:
            file.write(json.dumps(data))

    def create_table(self, name, data=None):
        if name in self.tables:
            raise DatabaseException(f"ERROR: Table {name} already exists")
        self.tables[name] = Table(name, data)

    def get_table(self, name):
        correct_names = list(self.tables.keys())
        lowered_names = list(map(str.lower, correct_names))
        try:
            i = lowered_names.index(name.lower())
            return self.tables[correct_names[i]]
        except:
            raise Exception(f"Invalid table name \"{name}\"")