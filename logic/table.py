import pandas as pd

class Table():
    def __init__(self, name, data=None):
        self.name = name
        self.read_in(data if data else {"schema": [], "records": []})

    def create_from_table(name, columns, data):
        table = Table(name)
        table.schema = [[column, "unknown"] for column in columns]
        table.columns = [scheme[0] for scheme in table.schema]
        # data = data.replace({float('nan'): None})
        table.data = data
        return table
    
    def write_out(self):
        return {"schema": self.schema, "records": self.data.values.tolist()}
    
    def read_in(self, data):
        self.schema = data["schema"]
        self.columns = [scheme[0] for scheme in self.schema]
        self.data = pd.DataFrame(data["records"], columns = self.columns)
        # self.data = self.data.replace({float('nan'): None})

    def get_lowered_columns(self):
        return list(map(str.lower, self.columns))
    
    def search_for_columns(self, columns):
        lowered_columns = list(map(str.lower, columns))
        all_lowered_columns = list(map(str.lower, self.columns))
        found_columns = []
        for column in lowered_columns:
            try:
                index = all_lowered_columns.index(column)
                found_columns.append(self.columns[index])
            except:
                raise Exception(f"Invalid column \'{column}\'")
        
        return found_columns
    
    def find_column(self, column):
        lowered_columns = list(map(str.lower, self.columns))
        try:
            i = lowered_columns.index(column.lower())
        except:
            raise Exception(f"Invalid column \'{column}\'")
        
        return self.schema[i], self.columns[i]


    def __str__(self):
        return str(self.data)
    
    def __repr__(self):
        return str(self.data)