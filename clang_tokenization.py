'''
Saves the clang tokenization of file.c into output.c in the form
<token> <lexeme> <starting line> <starting column>

usage: python3 clang_tokenization.py input.c output.c
'''
import sys
import subprocess
import re

# regular expression to match raw clang output
pattern = r"^(\w+) '(.*)'\t[\s\S]*?\tLoc=<(.+?):(\d+):(\d+)"

def get_clang_tokenization(path):
    clang_raw = subprocess.run(
        ["clang", "-fsyntax-only", "-Xclang", "-dump-tokens", path],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )

    with open(sys.argv[2], "w") as output:
        for line in clang_raw.stderr.splitlines():
            match = re.search(pattern, line)
            if match:
                token = match.groups()[0]
                lexeme = match.groups()[1]
                starting_line = match.groups()[-2]
                starting_column = match.groups()[-1]
                if(token != "eof"):
                    output.write(f"{token}\t{lexeme}\t{starting_line}\t{starting_column}\n")
                else:
                    #removes empty line
                    output.seek(output.tell() - 1)
                    output.truncate()
                    return True
            else:
                return False

def main():
    if len(sys.argv) != 3:
        print("error must be called in form:\npython3 clang_tokenization.py input.c output.c")
    else:
        if(get_clang_tokenization(sys.argv[1])):
            print(f"Clang tokenization saved to {sys.argv[2]}")
        else:
            print("Error formatting clang tokenizing.")

if __name__ == "__main__":
    main()