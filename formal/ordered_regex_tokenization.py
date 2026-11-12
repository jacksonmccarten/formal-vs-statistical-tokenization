'''
Saves the ordered regex tokenization of file.c into output.c in the form
<token> <lexeme> <starting line> <starting column>

usage: python3 clang_tokenization.py input.c output.c
'''
import sys
import re

TOKEN_PATTERNS = [
    # Whitespace and comments
    ("WHITESPACE",       r"\s+"),
    ("COMMENT",          r"//[^\n]*|/\*[\s\S]*?\*/"),

    # Literals
    ("string_literal",   r'"(?:\\.|[^"\\])*"'),
    ("char_constant",    r"'(?:\\.|[^'\\])*'"),
    ("numeric_constant", r"(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?)(?:[uUlLfF]*)"),

    # Identifiers
    ("identifier",       r"[a-zA-Z_][a-zA-Z0-9_]*"),

    # Multi-character operators
    ("ellipsis",         r"\.\.\."),
    ("lesslessequal",    r"<<="),
    ("greatergreaterequal", r">>="),
    ("arrow",            r"->"),
    ("plusplus",         r"\+\+"),
    ("minusminus",       r"--"),
    ("ampamp",           r"&&"),
    ("pipepipe",         r"\|\|"),
    ("equalequal",       r"=="),
    ("exclaimequal",     r"!="),
    ("lessequal",        r"<="),
    ("greaterequal",     r">="),
    ("lessless",         r"<<"),
    ("greatergreater",   r">>"),
    ("plusequal",        r"\+="),
    ("minusequal",       r"-="),
    ("starequal",        r"\*="),
    ("slashequal",       r"/="),
    ("percentequal",     r"%="),
    ("ampequal",         r"&="),
    ("pipeequal",        r"\|="),
    ("caretequal",       r"\^="),
    ("hashhash",         r"##"),

    # Single-character operators
    ("plus",             r"\+"),
    ("minus",            r"-"),
    ("star",             r"\*"),
    ("slash",            r"/"),
    ("percent",          r"%"),
    ("amp",              r"&"),
    ("pipe",             r"\|"),
    ("caret",            r"\^"),
    ("tilde",            r"~"),
    ("exclaim",          r"!"),
    ("less",             r"<"),
    ("greater",          r">"),
    ("equal",            r"="),

    # Punctuation
    ("l_paren",          r"\("),
    ("r_paren",          r"\)"),
    ("l_brace",          r"\{"),
    ("r_brace",          r"\}"),
    ("l_square",         r"\["),
    ("r_square",         r"\]"),
    ("semi",             r";"),
    ("comma",            r","),
    ("period",           r"\."),
    ("colon",            r":"),
    ("question",         r"\?"),
    ("hash",             r"#"),
]

KEYWORDS = [
    # C Keywords
    ("alignas",        r"alignas"),
    ("alignof",        r"alignof"),
    ("auto",           r"auto"),
    ("bool",           r"bool"),
    ("break",          r"break"),
    ("case",           r"case"),
    ("char",           r"char"),
    ("const",          r"const"),
    ("constexpr",      r"constexpr"),
    ("continue",       r"continue"),
    ("default",        r"default"),
    ("do",             r"do"),
    ("double",         r"double"),
    ("else",           r"else"),
    ("enum",           r"enum"),
    ("extern",         r"extern"),
    ("false",          r"false"),
    ("float",          r"float"),
    ("for",            r"for"),
    ("goto",           r"goto"),
    ("if",             r"if"),
    ("inline",         r"inline"),
    ("int",            r"int"),
    ("long",           r"long"),
    ("nullptr",        r"nullptr"),
    ("register",       r"register"),
    ("restrict",       r"restrict"),
    ("return",         r"return"),
    ("short",          r"short"),
    ("signed",         r"signed"),
    ("sizeof",         r"sizeof"),
    ("static",         r"static"),
    ("static_assert",  r"static_assert"),
    ("struct",         r"struct"),
    ("switch",         r"switch"),
    ("thread_local",   r"thread_local"),
    ("true",           r"true"),
    ("typedef",        r"typedef"),
    ("typeof",         r"typeof"),
    ("typeof_unqual",  r"typeof_unqual"),
    ("union",          r"union"),
    ("unsigned",       r"unsigned"),
    ("void",           r"void"),
    ("volatile",       r"volatile"),
    ("while",          r"while"),
    ("_Atomic",        r"_Atomic"),
    ("_BitInt",        r"_BitInt"),
    ("_Complex",       r"_Complex"),
    ("_Decimal128",    r"_Decimal128"),
    ("_Decimal32",     r"_Decimal32"),
    ("_Decimal64",     r"_Decimal64"),
    ("_Generic",       r"_Generic"),
    ("_Imaginary",     r"_Imaginary"),
    ("_Noreturn",      r"_Noreturn"),
]

pattern = re.compile("|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_PATTERNS))

def get_ordered_regex_tokenization(input_text):
    pos = 0
    current_line = 1
    current_character = 1
    longest_match = None     

    with open(sys.argv[2], "w") as output:
        while (len(input_text) > 0):    
            for pattern in TOKEN_PATTERNS:
                match = re.match(pattern[1], input_text)

                if match and (longest_match is None or len(match.group()) > len(longest_match.group())):
                    longest_match = match
                    token = pattern[0]
                    lexeme = longest_match.group()
            
            for pattern in KEYWORDS:
                match = re.match(pattern[1], input_text)

                if match and (longest_match is None or len(match.group()) >= len(longest_match.group())):
                    longest_match = match
                    token = pattern[0]
                    lexeme = longest_match.group()

            if (token != "WHITESPACE" and token != "COMMENT"):
                output.write(f"{token}\t{lexeme}\t{current_line}\t{current_character}\n")

            # Update line and column position
            newline_count = lexeme.count("\n")

            if newline_count > 0:
                current_line += newline_count
                current_character = len(lexeme.rsplit("\n", 1)[-1]) + 1
            else:
                current_character += len(lexeme)

            # Advance through input
            pos += len(lexeme)
            input_text = input_text[len(lexeme):]
            longest_match = None
        
        #removes empty line
        output.seek(output.tell() - 1)
        output.truncate()

def main():
    if len(sys.argv) != 3:
        print("error must be called in form:\npython3 clang_tokenization.py input.c output.c")
    else:
        with open(sys.argv[1], "r") as input:
                    input_text = input.read()
        
        get_ordered_regex_tokenization(input_text)
        print(f"Ordered regex tokenization saved to {sys.argv[2]}")

if __name__ == "__main__":
    main()