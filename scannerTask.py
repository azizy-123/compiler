import re

# === [1] TOKEN SPECIFICATIONS ===
TOKEN_SPECIFICATIONS = [
    ('Comments', r'//.*?$|/\*.*?\*/'),
    ('Character_constants', r"'.'"),
    ('Special_characters', r'[{}();]'),
    ('Numeric_constants', r'\b\d+(\.\d+)?([eE][+-]?\d+)?\b'),
    ('Operators', r'(\+\+|--|==|!=|<=|>=|<<=|>>=|\+=|-=|\*=|/=|%=|&=|\|=|\^=|<<|>>|->|&&|\|\||::|[+\-*/%=&|^~<>!]=?|[<>]=?|[+\-*/%=&|^~<>!])'),
    ('Identifiers', r'[a-zA-Z_]\w*'),
    ('Keywords', r'\b(if|else|switch|case|default|while|for|do|break|continue|goto|int|short|long|float|double|void|bool|char|string|signed|unsigned|auto|const|static|new|delete|using|namespace|try|throw|catch|class|struct|union|public|private|protected|friend|this|virtual|return|true|false)\b'),
    ('NEWLINE', r'\n'),
    ('SKIP', r'[ \t]+'),
    ('MISMATCH', r'.'),
]

# === [2] TOKEN CLASS ===
class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"<{self.type}, {self.value}>"

# === [3] TOKENIZER FUNCTION ===
def tokenize(code):
    tokens = []
    line_num = 1
    line_start = 0
    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPECIFICATIONS)
    get_token = re.compile(tok_regex, re.MULTILINE | re.DOTALL).match

    pos = 0
    match = get_token(code)
    while match is not None:
        type = match.lastgroup
        value = match.group(type)
        if type == 'NEWLINE':
            line_start = match.end()
            line_num += 1
        elif type == 'SKIP':
            pass
        elif type == 'MISMATCH':
            print(f"Unexpected character {value!r} at line {line_num}")
        else:
            column = match.start() - line_start
            tokens.append(Token(type, value, line_num, column))
        pos = match.end()
        match = get_token(code, pos)
    return tokens

# === [4] MAIN FUNCTION ===
def main():
    print("Enter your C++ code below (end with an empty line):")
    cpp_code = ""
    while True:
        line = input()
        if line == "":
            break
        cpp_code += line + "\n"

    try:
        tokens = tokenize(cpp_code)

        print("\n=== TOKENIZED OUTPUT ===")
        for token in tokens:
            print(token)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# === [5] ENTRY POINT ===
if __name__ == "__main__":
    main()
