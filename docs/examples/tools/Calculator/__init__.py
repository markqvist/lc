# Copyright (c) 2026 Mark Qvist - See LICENSE.md and README.md

import json
import urllib.request
import urllib.parse
from typing import List

from lc.toolkit import Toolkit, tool

import sympy as sp


def normalize_exponentiation(equation: str) -> str:
    """Convert various exponentiation notations to Sympy format."""
    # Convert ^ to ** (but preserve existing **)
    if "^" in equation:
        equation = equation.replace("^", "**")
    return equation


def normalize_operators(equation: str) -> str:
    """Convert various exponentiation notations to Sympy format."""
    # Convert ^ to ** (but preserve existing **)
    if "×" in equation:
        equation = equation.replace("×", "*")
    if "÷" in equation:
        equation = equation.replace("÷", "/")
    if "π" in equation:
        equation = equation.replace("π", "pi")
    return equation


def normalize_result(expr):
    if not type(expr) in [list]:
        if expr.is_integer:
            result = expr
        else:
            try:
                result = round(expr.evalf(), 5)
            except:
                try:
                    result = expr.evalf()
                except:
                    result = expr
    else:
        result = expr
    return result


class Calculator(Toolkit):

    @tool(gate_level=0)
    def calculate(self, expression: str) -> str:
        """
        Calculate the result of an expression using sympy expression syntax.
        All trigonometric functions are evaluated in radians, so if passing degrees as input to trigonometric functions, you must include a conversion to radians (pi/180).

        :param expression: The expression to calculate.
        :return: The result of the expression.
        """

        try:
            # Parse the expression using sympy
            expression = normalize_exponentiation(expression)
            expression = normalize_operators(expression)

            expr = sp.sympify(expression)
            result = normalize_result(expr)
            return f"{expression} = {result}"

        except (sp.SympifyError, ValueError) as e:
            print(e)
            return "Invalid expression"

    def simplify(self, expression: str) -> str:
        """
        Simplifies an expression.

        :param expression: The expression to simplify.
        :return: The result of the simplification.
        """
        try:
            # Parse the expression using sympy
            expr = sp.sympify(expression).simplify()
            result = normalize_result(expr)
            return f"{expression} = {result}"

        except (sp.SympifyError, ValueError) as e:
            print(e)
            return "Invalid expression"
