class Database:
    def __init__(self, name, ):
        self.tables = []
        self.name = name
        self.filename = self.create_file()