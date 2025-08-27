from inspect import signature

from parser import Token, tokenize
from operators import lambdas, precedence
from functions import *

function_factory = lambda f: eval("".join(map(str.capitalize, f[0].value.split(" "))))(f[1:])
function_find_class = lambda f: eval("".join(map(str.capitalize, f[0].value.split(" "))))

def flatten_tokens(tokens):
    if isinstance(tokens, Token) and tokens.type != "group":
        return [tokens]
    elif isinstance(tokens, Token):
        tokens = [tokens]

    all_tokens = []
    for token in tokens:
        if token.type == "group":
            all_tokens.extend(flatten_tokens(token.value))
        elif token.type == "special":
            continue
        else:
            all_tokens.append(token)

    return all_tokens

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
            func_class = function_find_class(token)
            # if not func_class.scalar:
            #     raise Exception("Something went wrong. This should be scalar.")
            function_stack.append(token)
        elif token.type == "group":
            output.extend(shunting_yard(token.value))
            output.extend(function_stack)
            function_stack = []
        elif token.type == "special":
            continue
        else:
            output.append(token)

    output.extend(stack)
    return output

def get_dependencies(tokens):
    return list(filter(lambda t: t.type == "unknown", tokens))

def evaluate(tokens, args):
    stack = []
    for token in tokens:
        if token.type not in ["operator", "function"]:
            stack.append(token)
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

            arg_tokens = stack[-num_args:]
            stack = stack[:-num_args]
            stack.append(func(*arg_tokens))

    return stack[0]

if __name__ == "__main__":
    tokens = tokenize("1+3*2")
    print(tokens)
    print(evaluate(shunting_yard(tokens), {}))