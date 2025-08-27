from collections import namedtuple

Token = namedtuple("Token", ["type", "value"])

alphabet = "abcdefghijklmnopqrstuvwxyz"
alphaBET = alphabet + alphabet.upper()
variables = alphaBET + "_."

numbers = "0.123456789"

statements = ["select", "select distinct", "insert into", "update", "delete"]
clauses = ["where", "values", "group by", "having", "top", "from", "order by", "join", "union", "union all"]
operators = ["distinct", "and", "or", "not", "like", "in", "between", "as", "=", ">", "<", ">=", "<=", "!=", "*", "+", "-", "%", "/", "//", "asc", "desc"]
functions = ["count", "sum", "min", "max", "avg"]
keywords = statements + clauses + operators + functions

unsupported = ["as"]

special_operators = [",", ";", "=", ">", "<", "!", "*", "+", "-", "%", "/"]

open_char_to_close = {
    '"': '"',
    "'": "'",
    "(": ")",
    "[": "]"
}

def create_token(token_string):
    def is_number(string):
        try:
            return float(string)
        except ValueError:
            return False

    if token_string in [",", ";"]:
        return Token("special", token_string)
    elif token_string[0] in ["'", '"']:
        return Token("string", token_string[1:-1].replace("\\'", "'"))
    elif token_string[0] in open_char_to_close:
        return Token("group", tokenize(token_string[1:-1]))
    elif (number := is_number(token_string)):
        return Token("number", number)
    elif token_string.lower() in keywords:
        token_string = token_string.lower()
        if token_string in statements:
            return Token("statement", token_string)
        elif token_string in clauses:
            return Token("clause", token_string)
        elif token_string in operators:
            return Token("operator", token_string)
        elif token_string in functions:
            return Token("function", token_string)
    else:
        return Token("unknown", token_string)

def condense(tokens):
    new_tokens = []
    for token in tokens:
        if token.type == "group":
            grouped = condense(token.value)
            while len(grouped) == 1 and grouped[0].type == "group":
                grouped = grouped[0].value
            new_tokens.append(Token("group", grouped))
        else:
            new_tokens.append(token)

    tokens = new_tokens
    new_tokens = []
    skip_next = False

    def join(new_value):
        nonlocal skip_next
        if new_value in statements:
            new_tokens.append(Token("statement", new_value))
        elif new_value in clauses:
            new_tokens.append(Token("clause", new_value))
        elif new_value in operators:
            new_tokens.append(Token("operator", new_value))
        elif new_value in functions:
            new_tokens.append(Token("function", new_value))
        skip_next = True

    for i, token in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue
        if token.type in {"statement", "clause", "operator", "function", "unknown"} and i < len(tokens) - 1 and tokens[i + 1].type in {"statement", "clause", "operator", "function", "unknown"}:
            if (new_value := (token.value + " " + tokens[i + 1].value).lower()) in keywords:
                join(new_value)
            elif (new_value := (token.value + tokens[i + 1].value).lower()) in keywords:
                join(new_value)
            else:
                new_tokens.append(token)
        else:
            new_tokens.append(token)

    # The following code automatically groups csvs (e.g. 1 2, 3 4 => 1 (2, 3) 4)
    # Removing because this method makes it very difficult to do expressions

    # tokens = new_tokens
    # new_tokens = []

    # keep_appending = True
    # group = []
    # skip_comma = False
    # for i in range(len(tokens)):
    #     if tokens[i].type == "special" and tokens[i].value == ",":
    #         if ((i > 0 and tokens[i - 1].type in ["statement", "clause", "operator", "function"]) or 
    #             (i < len(tokens) - 1 and tokens[i + 1].type in ["statment", "clause", "operator", "function"])):
    #             skip_comma = True
    #         else:
    #             keep_appending = True
    #             continue

    #     if not keep_appending:
    #         if not group:
    #             pass
    #         elif len(group) == 1:
    #             new_tokens.append(group[0])
    #         else:
    #             new_tokens.append(Token("group", group))
    #         group = []
    #         keep_appending = True
        
    #     if keep_appending:
    #         group.append(tokens[i]) if not skip_comma else None
    #         skip_comma = False
    #         keep_appending = False

    # if len(group) == 1:
    #     new_tokens.append(group[0])
    # else:
    #     new_tokens.append(Token("group", group))

    return new_tokens

def tokenize(query_string):
    tokens = []
    token = ""

    def flush():
        nonlocal token
        if token:
            tokens.append(create_token(token))
        token = ""

    def pop():
        nonlocal query_string
        char = query_string[0]
        query_string = query_string[1:]
        return char

    while len(query_string) > 0:
        char = pop()
        if char.isspace():
            flush()
        elif char in special_operators:
            flush()
            token += char
            flush()
        elif char in open_char_to_close:
            flush()
            opening, closing = char, open_char_to_close[char]
            left = 1
            while left != 0:
                token += char
                char = pop()
                if token[-1] == "\\":
                    pass
                elif char == closing:
                    left -= 1
                elif char == opening:
                    left += 1
            token += char
            flush()
        else:
            token += char
    
    flush()
    tokens = condense(tokens)
    return tokens

if __name__ == "__main__":
    print(tokenize("1+2*PRICE>=SALE"))