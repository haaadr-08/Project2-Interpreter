# Project 2 - Simple Interpreter

import re

variables = {}
let_variables = set()


def is_identifier(name):
    return re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name) is not None


def is_valid_number(num):
    return num == "0" or re.fullmatch(r"[1-9][0-9]*", num) is not None


def tokenize(expr):
    tokens = []
    i = 0

    while i < len(expr):
        ch = expr[i]

        if ch.isspace():
            i += 1

        elif ch.isdigit():
            start = i
            while i < len(expr) and expr[i].isdigit():
                i += 1
            tokens.append(expr[start:i])

        elif ch.isalpha():
            start = i
            while i < len(expr) and (expr[i].isalnum() or expr[i] == "_"):
                i += 1
            tokens.append(expr[start:i])

        elif ch in "+-*()":
            tokens.append(ch)
            i += 1

        else:
            return None

    return tokens


class Parser:
    def __init__(self, tokens, in_let):
        self.tokens = tokens
        self.pos = 0
        self.in_let = in_let
        self.error = None

    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def eat(self):
        tok = self.current()
        self.pos += 1
        return tok

    def parse_expr(self):
        value = self.parse_term()

        while self.current() == "+" or self.current() == "-":
            op = self.eat()
            right = self.parse_term()

            if op == "+":
                value += right
            else:
                value -= right

        return value

    def parse_term(self):
        value = self.parse_factor()

        while self.current() == "*":
            self.eat()
            right = self.parse_factor()
            value *= right

        return value

    def parse_factor(self):
        tok = self.current()

        if tok is None:
            self.error = "error"
            return 0

        if tok == "(":
            self.eat()
            value = self.parse_expr()

            if self.current() != ")":
                self.error = "error"
                return 0

            self.eat()
            return value

        if tok == "-":
            count = 0

            while self.current() == "-":
                self.eat()
                count += 1

            value = self.parse_factor()

            if count % 2 == 0:
                return value
            else:
                return -value

        if tok == "+":
            self.eat()
            return self.parse_factor()

        if tok.isdigit():
            self.eat()

            if not is_valid_number(tok):
                self.error = "error"
                return 0

            return int(tok)

        if is_identifier(tok):
            self.eat()

            if tok not in variables:
                self.error = "error, uninitialized variable"
                return 0

            if self.in_let and tok not in let_variables:
                self.error = "error, normal variables in let expression"
                return 0

            return variables[tok]

        self.error = "error"
        return 0


def evaluate_expression(expr, in_let):
    tokens = tokenize(expr)

    if tokens is None or len(tokens) == 0:
        return None, "error"

    parser = Parser(tokens, in_let)
    value = parser.parse_expr()

    if parser.error is not None:
        return None, parser.error

    if parser.current() is not None:
        return None, "error"

    return value, None


def process_line(line):
    line = line.strip()

    if line == "":
        return None

    if not line.endswith(";"):
        return "error"

    line = line[:-1].strip()

    is_let = False

    if line.startswith("let "):
        is_let = True
        line = line[4:].strip()

    if line.count("=") != 1:
        return "error"

    left, right = line.split("=")
    left = left.strip()
    right = right.strip()

    if not is_identifier(left):
        return "error"

    value, error = evaluate_expression(right, is_let)

    if error is not None:
        return error

    variables[left] = value

    if is_let:
        let_variables.add(left)

    return None


def run_program(program):
    for line in program.strip().split("\n"):
        result = process_line(line)

        if result is not None:
            print(result)
            return

    for name in variables:
        print(name, "=", variables[name])


program = """
let x = 1;
y = 2;
z = ---(x+y)*(x+-y);
"""

run_program(program)