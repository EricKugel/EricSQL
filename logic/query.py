import logic.parser

from logic.table import Table
from logic.parser import Token

import pandas as pd

from logic.statements import *
from logic.operators import *
from logic.clauses import *
from logic.functions import *

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
    for query in create_queries(logic.parser.tokenize("SELECT CustomerName, City FROM Customers;")):
        print(query.execute())