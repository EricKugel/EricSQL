from helpers import flatten_tokens

import pandas as pd

aggregate_functions = ["max", "min", "sum", "count"]

# "preevaluated" as an aggregate function value is a list of token values. Thus if a Price column 
# is $1, $2, $3 and SUM(2 * Price) is called, preevaluated will have a value [2, 4, 6].

# args do not include the table, which should be passed for each function call.
class Function():
    pass

class Count(Function):
    args = 1
    def execute(preevaluated, table):
        token_value = preevaluated[0]
        if token_value != "*":
            # TODO: The exceptions write themselves
            raise Exception("I'm really sorry but functions like COUNT with a variable number of arguments are soooo much work to implement. Would you mind using syntax like this instead, with just an asterisk? SELECT COUNT(*) FROM (SELECT DISTINCT CustomerID FROM Customers)")
        
        return len(table.data.drop_duplicates())
    
class Max(Function):
    args = 1
    def execute(preevaluated, table):
        return max(preevaluated)
    
class Min(Function):
    args = 1
    def execute(preevaluated, table):
        return min(preevaluated)

# TODO: Expressions
# TODO: What is numeric?
class Sum(Function):
    args = 1
    def execute(preevaluated, table):
        column = pd.Series(preevaluated).dropna()
        return sum(column)