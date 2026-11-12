# formal-vs-statistical-tokenization
This repository is a Schreyer Honors Option project comparing two ways of tokenizing source code: formal, rule-based lexers like those inside real compilers, and learned tokenizers that infer the rules from data. Five tokenizers are implemented for the same subset of C, defined in the lexical specification: three formal lexers that differ in mechanism, and two learned approaches, one that reverse-engineers a lexer with LearnLib and one LLM-style classifier trained on examples. Each tokenizer is run on a held-out test corpus of C code and scored against clang's lexer as the reference, using token accuracy, boundary F1, runtime, and memory. The goal is to show where each approach succeeds, where it breaks down, and why.

## Formal (rule-based) tokenizers

### 1. Table-driven DFA, maximal munch (`dfa_maximal_munch.py`)
All token rules are compiled into one deterministic finite automaton stored as a transition table. The lexer runs the DFA as far as it can, remembers the last accepting state, and emits the longest match. Lexer generators: flex (PostgreSQL), re2c (PHP)

### 2. Ordered regex, first match (`regex_first_match.py`)
An ordered list of regular expressions is tried at each position, and the first one that matches wins, even if a later rule would match more text. Correctness depends on rule order and lookaheads rather than on a longest-match guarantee. Syntax highlighters: Pygments, TextMate/VS Code grammars

### 3. Hand-written scanner (`handwritten_scanner.py`)
The automaton is written directly as control flow: the scanner branches on the current character and uses lookahead and explicit state to decide where each token ends. This makes context-dependent cases such as line splicing, comments, and string escapes straightforward to handle. Production compilers: GCC, Clang, rustc, Go, javac

## Learned tokenizers

### 4. Automata learning with LearnLib

LearnLib's **TTT** algorithm (with **L\*** for comparison with van Rooijen's thesis) learns a Mealy machine of one formal lexer, treated as a black box, using membership queries and a random-walk equivalence oracle. The alphabet is reduced to character classes (letter, digit, each operator character, quote, whitespace, other) to keep the number of queries manageable. The learned machine is then run as a tokenizer on the test corpus. This measures how completely black-box learning recovers a lexer that was never seen as code.

### 5. LLM-style boundary classifier

A small transformer encoder reads the input byte by byte and classifies each byte as the start of a token (with its type), the inside of a token, or discarded (whitespace and comments). It is trained on clang's gold tokens for the training corpus, so it learns the lexer from examples, not from rules. Like a decision model such as Jev, it returns a typed answer at each position instead of generating text, which makes it a learned, classifier-based tokenizer in the sense of the project description.

## Usage

Used to remove preprocessor directives to prevent clang from lexing linked code.
```
for file in corpus/evaluation/data/*.c; do
    python3 preprocessor.py "$file" "corpus/evaluation/preprocessed_data/$(basename "$file" .c)_preprocessed.c"
done
```

Used to generate clang tokenization of cleaned c-code.
```
for file in corpus/evaluation/preprocessed_data/*.c; do
    python3 clang_tokenization.py "$file" "corpus/evaluation/clang_tokenization/$(basename "$file" .c)_clang_tokenization.c"
done
```

Used to evaluate tokenization against clang tokenization.
```
python3 evaluation.py formal/ordered_regex_tokenization.py corpus/evaluation/preprocessed_data/ formal/ordered_regex_output ordered_regex
```