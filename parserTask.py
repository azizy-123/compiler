import re
from enum import Enum
from typing import List, Tuple

class TokenType(Enum):
    # Keywords
    KEYWORD = "KEYWORD"
    # Data types
    DATATYPE = "DATATYPE"
    # Identifiers and literals
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    CHAR = "CHAR"
    # Operators
    OPERATOR = "OPERATOR"
    # Delimiters
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    # Special
    PREPROCESSOR = "PREPROCESSOR"
    COMMENT = "COMMENT"
    WHITESPACE = "WHITESPACE"
    UNKNOWN = "UNKNOWN"

class Token:
    def __init__(self, type: TokenType, value: str, line: int, col: int):
        self.type = type
        self.value = value
        self.line = line
        self.col = col
    
    def __repr__(self):
        return f"Token({self.type.value}, '{self.value}', Line: {self.line}, Col: {self.col})"

class Lexer:
    def __init__(self):
        # C/C++ Keywords
        self.keywords = {
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
            'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto',
            'if', 'int', 'long', 'register', 'return', 'short', 'signed',
            'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
            'unsigned', 'void', 'volatile', 'while', 'class', 'namespace',
            'using', 'public', 'private', 'protected', 'virtual', 'bool',
            'true', 'false', 'new', 'delete', 'this', 'try', 'catch', 'throw'
        }
        
        # Data types
        self.datatypes = {
            'int', 'float', 'double', 'char', 'void', 'long', 'short',
            'unsigned', 'signed', 'bool', 'string'
        }
        
        # Operators
        self.operators = {
            '+', '-', '*', '/', '%', '=', '==', '!=', '<', '>', '<=', '>=',
            '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '++', '--',
            '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '->', '.', '::'
        }
        
        # Token patterns
        self.token_patterns = [
            (r'#\s*\w+.*', TokenType.PREPROCESSOR),
            (r'//.*', TokenType.COMMENT),
            (r'/\*[\s\S]*?\*/', TokenType.COMMENT),
            (r'"(?:[^"\\]|\\.)*"', TokenType.STRING),
            (r"'(?:[^'\\]|\\.)'", TokenType.CHAR),
            (r'\b\d+\.?\d*([eE][+-]?\d+)?\b', TokenType.NUMBER),
            (r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', TokenType.IDENTIFIER),
            (r'[+\-*/%=!<>&|^~]{1,2}', TokenType.OPERATOR),
            (r'::', TokenType.OPERATOR),
            (r'->', TokenType.OPERATOR),
            (r';', TokenType.SEMICOLON),
            (r',', TokenType.COMMA),
            (r'\(', TokenType.LPAREN),
            (r'\)', TokenType.RPAREN),
            (r'\{', TokenType.LBRACE),
            (r'\}', TokenType.RBRACE),
            (r'\[', TokenType.LBRACKET),
            (r'\]', TokenType.RBRACKET),
            (r'\s+', TokenType.WHITESPACE),
        ]
    
    def tokenize(self, code: str) -> List[Token]:
        tokens = []
        lines = code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            col = 0
            while col < len(line):
                matched = False
                
                for pattern, token_type in self.token_patterns:
                    regex = re.match(pattern, line[col:])
                    if regex:
                        value = regex.group(0)
                        
                        # Classify keywords and datatypes
                        if token_type == TokenType.IDENTIFIER:
                            if value in self.keywords or value in self.datatypes:
                                token_type = TokenType.KEYWORD
                        
                        # Skip whitespace tokens
                        if token_type != TokenType.WHITESPACE:
                            tokens.append(Token(token_type, value, line_num, col + 1))
                        
                        col += len(value)
                        matched = True
                        break
                
                if not matched:
                    tokens.append(Token(TokenType.UNKNOWN, line[col], line_num, col + 1))
                    col += 1
        
        return tokens

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type != TokenType.COMMENT]
        self.pos = 0
        self.errors = []
    
    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def consume(self, expected_type=None):
        token = self.current_token()
        if token:
            if expected_type and token.type != expected_type:
                self.errors.append(f"Expected {expected_type.value}, got {token.type.value} at line {token.line}")
                return None
            self.pos += 1
            return token
        return None
    
    def parse(self) -> bool:
        """Main parsing function - checks basic C/C++ syntax rules"""
        self.errors = []
        
        # Check for unknown tokens
        for token in self.tokens:
            if token.type == TokenType.UNKNOWN:
                self.errors.append(f"Unknown token '{token.value}' at line {token.line}, col {token.col}")
        
        # Check balanced braces, brackets, and parentheses
        self.check_balanced_delimiters()
        
        # Check semicolons after statements
        self.check_statement_structure()
        
        return len(self.errors) == 0
    
    def check_balanced_delimiters(self):
        stack = []
        pairs = {
            TokenType.LPAREN: TokenType.RPAREN,
            TokenType.LBRACE: TokenType.RBRACE,
            TokenType.LBRACKET: TokenType.RBRACKET
        }
        
        for token in self.tokens:
            if token.type in pairs:
                stack.append((token.type, token))
            elif token.type in pairs.values():
                if not stack:
                    self.errors.append(f"Unmatched closing delimiter '{token.value}' at line {token.line}")
                else:
                    open_type, open_token = stack.pop()
                    if pairs[open_type] != token.type:
                        self.errors.append(f"Mismatched delimiters: '{open_token.value}' at line {open_token.line} and '{token.value}' at line {token.line}")
        
        for open_type, token in stack:
            self.errors.append(f"Unclosed delimiter '{token.value}' at line {token.line}")
    
    def check_statement_structure(self):
        """Basic check for statement structure"""
        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            
            # Skip preprocessor directives
            if token.type == TokenType.PREPROCESSOR:
                i += 1
                continue
            
            # Check for statements that should end with semicolon
            if token.type == TokenType.KEYWORD and token.value in {'return', 'break', 'continue'}:
                # Find next semicolon or brace
                j = i + 1
                found_semicolon = False
                while j < len(self.tokens):
                    if self.tokens[j].type == TokenType.SEMICOLON:
                        found_semicolon = True
                        break
                    if self.tokens[j].type in {TokenType.LBRACE, TokenType.RBRACE}:
                        break
                    j += 1
                
                if not found_semicolon and j < len(self.tokens):
                    if self.tokens[j].type != TokenType.LBRACE:
                        self.errors.append(f"Missing semicolon after '{token.value}' statement at line {token.line}")
            
            i += 1

def main():
    print("=" * 60)
    print("C/C++ Code Parser and Validator")
    print("=" * 60)
    print("\nEnter your C/C++ code below.")
    print("Type 'END' on a new line when finished:\n")
    
    # Read multi-line input
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        except EOFError:
            break
    
    code = '\n'.join(lines)
    
    if not code.strip():
        print("\nNo code entered!")
        return
    
    print("\n" + "=" * 60)
    print("TOKENIZATION RESULTS")
    print("=" * 60)
    
    # Tokenize
    lexer = Lexer()
    tokens = lexer.tokenize(code)
    
    # Display tokens
    for token in tokens:
        print(token)
    
    print("\n" + "=" * 60)
    print("SYNTAX VALIDATION")
    print("=" * 60)
    
    # Parse and validate
    parser = Parser(tokens)
    is_valid = parser.parse()
    
    if is_valid:
        print("\n✓ CODE IS VALID")
        print("The code follows basic C/C++ syntax rules.")
    else:
        print("\n✗ CODE IS INVALID")
        print("\nErrors found:")
        for error in parser.errors:
            print(f"  - {error}")
    
    print("\n" + "=" * 60)
    print(f"Result: {is_valid}")
    print("=" * 60)

if __name__ == "__main__":
    main()