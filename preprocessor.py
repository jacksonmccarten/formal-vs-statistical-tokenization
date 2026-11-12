'''
Saves the clang tokenization of file.c into output.c in the form
<token> <lexeme> <starting line> <starting column>

usage: python3 preprocess.py input.c output.c
'''
import sys
import re

# regular expression to match c preprocessor commands
pattern = r"^\s*#(.*)"

def remove_c_preprocessors():
    with open(sys.argv[1], "r") as input:
        input_text = input.read()

    with open(sys.argv[2], "w") as output:
            for line in input_text.splitlines():
                match = re.search(pattern, line)
                if not match:
                    output.write(f"{line}\n")

def main():
    if len(sys.argv) != 3:
        print("error must be called in form:\npython3 preprocess.py input.c output.c")
    remove_c_preprocessors()
    print(f"Preprocessed file saved to {sys.argv[2]}")

if __name__ == "__main__":
    main()