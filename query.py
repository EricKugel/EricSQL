import parser

from table import Table
from parser import Token

import pandas as pd

def flatten_tokens(tokens):
    if isinstance(tokens, Token) and tokens.type != "group":
        return [tokens]
    elif isinstance(tokens, Token):
        tokens = [tokens]

    all_tokens = []
    for token in tokens:
        all_tokens.extend(flatten_tokens(token.value)) if token.type == "group" else all_tokens.append(token)

    return all_tokens

class Query():
    def __init__(self, database, statement, clauses):
        self.database = database
        self.statement = statement
        self.clauses = clauses
    def execute(self):
        result = self.statement.execute(self.database)
        for clause in self.clauses:
            if clause.snoop:
                result = clause.snoop_callback(result)
        return result

class Statement():
    def __init__(self, tokens):
        self.tokens = tokens
        self.clauses = []

class Clause():
    snoop = False
    def __init__(self, tokens):
        self.tokens = tokens

class Function():
    def __init__(self, tokens):
        if len(tokens) == 1 and tokens[0].type == "group":
            self.tokens = tokens[0].value
        else:
            self.tokens = tokens

class Count(Function):
    def execute(self, table):
        distinct = self.tokens[0].type == "operator" and self.tokens[0].value == "distinct"
        if distinct:
            self.tokens = self.tokens[1:]

        columns = self.tokens[0]
        if self.tokens[0].type == "operator" and columns.value == "*":
            selected_columns = table.columns
        else:
            selected_columns = list(map(lambda t: t.value, flatten_tokens(self.tokens)))
            selected_columns = table.search_for_columns(selected_columns)

        df = table.data[selected_columns]
        if distinct:
            df = df.drop_duplicates()
        
        return len(df)

# TODO: Expressions
# TODO: What is numeric?
class Sum(Function):
    def execute(self, table):
        scheme, column = table.find_column(self.tokens[0].value)
        if scheme[1] not in ["int"]:
            raise Exception(f"Column {column} is not numeric")
        column = table.data[column].dropna()
        return sum(column)

class From(Clause):
    def get_table(self, database):
        if self.tokens[0].type == "group":
            recursive_query = create_queries(self.tokens[0].value, database)[0]
            return recursive_query.execute()
        return database.get_table(self.tokens[0].value)
    
class OrderBy(Clause):
    snoop = True
    def snoop_callback(self, result):
        ascending = []
        columns = []
        in_queue = 0

        for token in flatten_tokens(self.tokens):
            if token.type == "operator" and token.value in ["asc", "desc"]:
                ascending.extend([True] * in_queue if token.value == "asc" else [False] * in_queue)
                in_queue = 0
            else:
                columns.append(token.value)
                in_queue += 1

        ascending.extend([True] * in_queue)
        found_columns = result.search_for_columns(columns)

        sorted_data = result.data.sort_values(by = found_columns, ascending = ascending)
        return Table.create_from_table("result", schema = result.schema, data = sorted_data)
    
class Values(Clause):
    def get_rows(self, columns):
        values = []
        for token in self.tokens:
            if token.type == "group":
                child_tokens = flatten_tokens(token.value)
                values.extend(list(map(lambda t: t.value, child_tokens)))
            else:
                values.append(token.value)
        
        rows = []
        for i in range(0, len(values), (length := len(columns))):
            rows.append(values[i:i + length])
        return rows

class Select(Statement):
    def execute(self, database):
        from_clause = None
        for clause in self.clauses:
            if isinstance(clause, From):
                from_clause = clause
                break
        else:
            raise Exception("Select statements require From clauses")

        table = from_clause.get_table(database)

        if self.tokens[0].type == "function":
            function_outputs = []
            for i in range(len(self.tokens) // 2):
                if self.tokens[i * 2].type != "function":
                    raise Exception("Columns and aggregate functions can't be mixed without a GROUP BY clause")

                func = function_factory(self.tokens[i * 2:i * 2 + 2])
                function_outputs.append(func.execute(table))
            return function_outputs if len(function_outputs) > 1 else function_outputs[0]

        columns = self.tokens[0]
        if self.tokens[0].type == "operator" and columns.value == "*":
            selected_columns = table.columns
        else:
            selected_columns = list(map(lambda t: t.value, flatten_tokens(self.tokens)))
            selected_columns = table.search_for_columns(selected_columns)

        selected_schema = []
        for scheme in table.schema:
            if scheme[0] in selected_columns:
                selected_schema.append(scheme)
        
        return Table.create_from_table("result", selected_schema, table.data[selected_columns])

class SelectDistinct(Statement):
    def execute(self, database):
        new_statement = Select(self.tokens)
        new_statement.clauses = self.clauses
        result = new_statement.execute(database)
        return Table.create_from_table("result", schema = result.schema, data = result.data.drop_duplicates())
    
class InsertInto(Statement):
    def execute(self, database):
        table = database.get_table(self.tokens[0].value)

        columns = table.columns
        if len(self.tokens) > 1:
            columns = list(map(lambda t: t.value, flatten_tokens(self.tokens[1:])))
            columns = table.search_for_columns(columns)

        values_clause = None
        for clause in self.clauses:
            if isinstance(clause, Values):
                values_clause = clause
                break
        else:
            raise Exception("INSERT INTO statements require a Values clause")
        
        rows = values_clause.get_rows(columns)

        new_df = pd.DataFrame(rows, columns=columns)
        table.data = pd.concat((table.data, new_df))

    
statement_factory = lambda s: eval("".join(map(str.capitalize, s[0].value.split(" "))))(s[1:])
clause_factory = lambda c: eval("".join(map(str.capitalize, c[0].value.split(" "))))(c[1:])
function_factory = lambda f: eval("".join(map(str.capitalize, f[0].value.split(" "))))(f[1:])

def create_queries(tokens, database):
    multi_query = []
    current = []
    for token in tokens:
        if token.type == "special" and token.value == ";":
            if current:
                multi_query.append(current)
            current = []
        else:
            current.append(token)
    if current:
        multi_query.append(current)

    queries = []
    for tokens in multi_query:
        group = [tokens[0]]
        groups = []
        for token in tokens[1:]:
            if token.type in ["statement", "clause"]:
                groups.append(group)
                group = [token]
            else:
                group.append(token)
        groups.append(group)

        statement = None
        clauses = []

        for group in groups:
            if group[0].type == "statement":
                statement = group
            else:
                clauses.append(group)

        statement = statement_factory(statement)
        clauses = list(map(clause_factory, clauses))

        statement.clauses = clauses
        queries.append(Query(database, statement, clauses))
    
    return queries

if __name__ == "__main__":
    for query in create_queries(parser.tokenize("SELECT CustomerName, City FROM Customers;")):
        print(query.execute())