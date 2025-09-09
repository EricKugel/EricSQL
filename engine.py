from inspect import signature

from operators import lambdas, precedence
from functions import *

from parser import Token

function_factory = lambda f: eval("".join(map(str.capitalize, f[0].value.split(" "))))(f[1:])
function_find_class = lambda f: eval("".join(map(str.capitalize, f.value.split(" "))))

def get_precedence(operator):
    if operator in precedence:
        return precedence[operator]
    else:
        return 0

# Modified shunting-yard algorithm, where tokens of type group are parsed recursively
def shunting_yard(tokens):
    output = []
    stack = []
    function_stack = []
    for token in tokens:
        if token.type == "operator":
            while stack and get_precedence(stack[-1].value) >= get_precedence(token.value):
                output.append(stack.pop())
            stack.append(token)
        elif token.type == "function":
            # func_class = function_find_class(token)
            # if not func_class.scalar:
            #     raise Exception("Something went wrong. This should be scalar.")
            function_stack.append(token)
        elif token.type == "group":
            output.extend(shunting_yard(token.value))
            output.extend(function_stack[::-1])
            function_stack = []
        elif token.type == "preevaluated":
            output.append(token)
            output.extend(function_stack[::-1])
            function_stack = []
        elif token.type == "special":
            output.extend(stack[::-1])
            stack = []
        else:
            output.append(token)

    output.extend(stack[::-1])
    return output

# TODO What is a case???
# TODO Preprocess aggregate functions which need column pairs (like covar)
def create_function(tokens, table, aggregate):
    # If this is aggregate, we actually need 2 functions:
    #   1) Inner-aggregate evaluation, which is basically just a non-aggregate evaluation
    #   2) Outer-level evaluation

    if aggregate:
        # Condense whatever's inside the function to one column
        new_tokens = []
        skip_next = False
        for i in range(len(tokens)):
            if skip_next:
                skip_next = False
                continue

            token = tokens[i]
            new_tokens.append(token)
            if token.type == "function" and token.value in aggregate_functions:
                skip_next = True
                arg_tokens = tokens[i + 1].value
                inner_func = create_function(arg_tokens, table, False)
                inner_row = []
                for _, row in table.data.iterrows():
                    inner_row.append(inner_func(row.to_dict()))
                new_tokens.append(Token("preevaluated", inner_row))
        tokens = new_tokens

    tokens = shunting_yard(tokens)
    new_tokens = []

    for token in tokens:
        if token.type == "unknown":
            _, name = table.find_column(token.value)
            new_tokens.append(Token("unknown", name))
        else:
            new_tokens.append(token)
    return lambda args: evaluate(new_tokens, args, table)

def check_for_aggregate(tokens):
    def is_aggregate(token):
        return token.type == "function" and token.value.lower() in aggregate_functions
    return any(map(is_aggregate, tokens))

def get_dependencies(tokens):
    return list(filter(lambda t: t.type == "unknown", tokens))

# TODO Logic for aggregates!
def evaluate(tokens, args, table):
    stack = []
    for token in tokens:
        if token.type not in ["operator", "function"]:
            if token.type == "unknown":
                # If aggregate, this basically is just a series of the column.
                token = Token("unknown", args[token.value])
            stack.append(token.value)
        else:
            func = None
            num_args = None
            if token.type == "function":
                func_class = function_find_class(token)
                func = func_class.execute
                num_args = func_class.args
            else:
                func = lambdas[token.value]
                num_args = len(signature(func).parameters)

            args = stack[-num_args:]
            stack = stack[:-num_args]

            stack.append(func(*args, table) if token.type == "function" else func(*args))

    return stack[0]

if __name__ == "__main__":
    # tokens = tokenize("min(sum(sum(1, 2)))")
    # print("  ".join(map(lambda t: str(t.value), shunting_yard(tokens))))
    # print(evaluate(shunting_yard(tokens), {}))
    pass