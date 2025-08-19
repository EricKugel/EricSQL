from parser import Token

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