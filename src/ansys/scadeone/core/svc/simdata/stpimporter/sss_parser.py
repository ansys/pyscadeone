# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ===============================
# SSS Parser
# ===============================
# cSpell: ignore pyparsing, alphanums, printables, Hexa

from pathlib import Path
import re
from pyparsing import (
    DelimitedList,
    Forward,
    Group,
    Literal,
    Optional,
    ParseException,
    QuotedString,
    Regex,
    Suppress,
    Word,
    alphanums,
    nums,
    oneOf,
    printables,
    rest_of_line,
)
from .utils import ConverterLogger


class SSSParser:
    def __init__(self) -> None:
        self._ctors = None
        self._cmds = []
        self._defs = None

    def initialize(self, **sss_ctors) -> None:
        self._ctors = sss_ctors
        self._cmds = []
        self._bnf()

    def reset_cmd(self):
        self._cmds = []

    @staticmethod
    def merge_multiline(input_string: str) -> str:
        """Reunify multiline strings that are separated by a backslash"""
        buffer = []
        lines = input_string.splitlines()
        current_line = ""
        for line in lines:
            if line.endswith("\\"):
                current_line += line[:-1] + " "
            else:
                current_line += line
                buffer.append(current_line)
                current_line = ""
        lined_string = "\n".join(buffer)
        return lined_string

    def parse_file(self, file: Path):
        """Parse a SSS file and return the commands"""
        try:
            try:
                output_string = file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                output_string = file.read_text()
            lined_string = self.merge_multiline(output_string)
            self._defs.parse_string(lined_string, parse_all=True)
            cmds = self._cmds
            self._cmds = []
            return cmds

        except ParseException as e:
            ConverterLogger.exception(f"Error parsing file\n{file}\n{e.explain(depth=0)}")

    # Helper to parse an atom
    WS = {
        "\\n": "\n",
        "\\r": "\r",
        "\\t": "\t",
        "\\0": "\0",
    }

    @staticmethod
    def to_char(text: str):
        # Convert a string representing a char, potentially as '\\xhh", or ' \\n'
        # into the corresponding char
        # Text may be surrounded by single quotes or not
        if len(text) == 1:
            return text
        if text[0] == "'":
            text = text[1:-1]
        if text in SSSParser.WS:
            return SSSParser.WS[text]
        # handle '\'
        if text[0] != "\\":
            return text
        text = "0" + text[1:]
        char = "%c" % int(text, 16)
        return char

    HexaRe = re.compile(r"\\x[0-9a-fA-F]{2}")

    @staticmethod
    def string_to_chars(txt):
        # parse a string '"..."'. String must start with '"' and end with '"'
        def _parse_string(txt):
            if txt == '"':
                return []
            if txt[0:2] in ("\\n", "\\r", "\\t", "\\0"):
                char = txt[0:2]
                rest = txt[2:]
            elif SSSParser.HexaRe.match(txt[0:4]):
                char = txt[0:4]
                rest = txt[4:]
            elif txt[0] == "\\":
                char = txt[1]
                rest = txt[2:]
            else:
                char = txt[0]
                rest = txt[1:]
            return [SSSParser.to_char(char)] + _parse_string(rest)

        if txt[0] == '"':
            res = _parse_string(txt[1:])
            return res
        return []

    LCB, RCB = map(Suppress, "{}")

    @staticmethod
    def _bool_or_ident(txt: str):
        return (
            txt[0].lower() == "t"
            if txt in ("true", "false", "TRUE", "FALSE", "True", "False", "t", "f", "T", "F")
            else txt
        )

    @staticmethod
    def _parse_atom():
        # define the grammar
        LPAR, RPAR = map(Suppress, "()")
        int_value = Regex(r"[-+]?\d+").set_parse_action(lambda t: int(t[0]))
        hex_value = Regex(r"0x[0-9a-fA-F]+").set_parse_action(lambda t: int(t[0], 16))
        bin_value = Regex(r"0b[01]+").set_parse_action(lambda t: int(t[0], 2))
        oct_value = Regex(r"0o[0-7]+").set_parse_action(lambda t: int(t[0], 8))

        float_value = Regex(
            r"[-+]?\d*\.\d*(?:[eE][-+]?\d+)?|[-+]?\d+[eE][-+]?\d+"
        ).set_parse_action(lambda t: float(t[0]))
        float_special = oneOf("NaN qNaN sNaN +Inf -Inf").set_parse_action(lambda t: t[0])
        char_value = Literal("'''") ^ QuotedString("'", unquote_results=False)
        string_value = QuotedString('"', esc_char="\\", unquote_results=False)
        ident_or_kw = Regex(r"[\w+:]+")
        ident_or_kw.set_parse_action(lambda t: SSSParser._bool_or_ident(t[0]))

        value = Forward()
        atom = (  # order is important: hex/bin/oct before float before int
            hex_value
            | bin_value
            | oct_value
            | float_special
            | float_value
            | int_value
            | char_value
            | string_value
            | ident_or_kw
            | Literal("?")
            | Group(LPAR + DelimitedList(value) + RPAR)
        )
        value << Optional(atom).set_parse_action(lambda t: t if len(t) else ["<empty>"])
        return value ^ Group(SSSParser.LCB + value + SSSParser.RCB).set_parse_action(lambda t: t[0])

    def _bnf(self):
        # Build the parser

        variable = Regex(r"[\w\[\]\./:]+") ^ QuotedString(quote_char="{", end_quote_char="}")

        ident = Word(alphanums + "_")

        value = SSSParser._parse_atom()

        value.set_parse_action(lambda t: self._ctors["atom"](t.as_list()))

        set_def = (
            Literal("SSM::set")
            + variable.set_results_name("variable")
            + value.set_results_name("value")
        )

        cycle_def = Literal("SSM::cycle") + Optional(Word(nums).set_results_name("number"))

        check_image_def = Literal("SSM::check image") + rest_of_line

        complex_expr_def = (
            Word("{") + (Word("in") ^ Word("not") ^ (Word(alphanums) + Word("->"))) + rest_of_line
        ).set_results_name("check")

        check_complex_def = (
            Literal("SSM::check") + variable.set_results_name("variable") + complex_expr_def
        )

        check_arg = (
            Literal("sustain") + Literal("=") + Word(printables).set_results_name("sustain")
        ) ^ (Literal("real") + Literal("=") + Word(printables).set_results_name("real"))

        check_def = (
            Literal("SSM::check")
            + variable.set_results_name("variable")
            + value.set_results_name("value")
            + check_arg[...]
        )

        uncheck_def = Literal("SSM::uncheck") + variable

        alias_def = (
            Literal("SSM::alias")
            + Word(printables).set_results_name("alias")
            + variable.set_results_name("variable")
        )

        complex_alias_value_def = (
            Literal("SSM::alias_value") + ident.set_results_name("alias") + complex_expr_def
        )

        alias_value_def = (
            Literal("SSM::alias_value")
            + ident.set_results_name("alias")
            + value.set_results_name("value")
        )

        tolerance_def = Literal("SSM::set_tolerance") + rest_of_line.set_results_name("line")

        unsupported_def = Literal("SSM::") + rest_of_line

        comments_def = Literal("#") + rest_of_line

        def set_act(tokens) -> None:
            """Action for SSM::set command"""
            self._cmds.append(self._ctors["sss_set"](tokens.variable, tokens.value))

        def cycle_act(tokens) -> None:
            """Action for SSM::cycle command"""
            if tokens.number:
                number = tokens.number
            else:
                number = 1
            self._cmds.append(self._ctors["sss_cycle"](number))

        def check_act(tokens) -> None:
            """Action for SSM::check command"""
            if not tokens.sustain:
                sustain = 1
            elif str(tokens.sustain).lower() == "forever":
                sustain = 0
            else:
                sustain = int(tokens.sustain)
            self._cmds.append(
                self._ctors["sss_check"](tokens.variable, tokens.value, sustain, tokens.real)
            )

        def tolerance_act(tokens) -> None:
            """Action for SSM::tolerance command"""
            self._cmds.append(self._ctors["sss_tolerance"](tokens.line))

        def alias_act(tokens) -> None:
            """Action for SSM::alias command"""
            self._cmds.append(self._ctors["sss_alias"](tokens.alias, tokens.variable))

        def alias_value_act(tokens) -> None:
            """Action for SSM::alias_value command"""
            self._cmds.append(
                self._ctors["sss_alias_value"](tokens.alias, tokens.value, tokens.check)
            )

        def undefined_act(tokens) -> None:
            """Unsupported actions -> to be logged"""
            self._cmds.append(self._ctors["unsupported"](" ".join(tokens)))

        def no_act(tokens) -> None:
            """No action for comments"""
            pass

        comments_def.set_parse_action(no_act)

        set_def.set_parse_action(set_act)
        cycle_def.set_parse_action(cycle_act)
        check_def.set_parse_action(check_act)
        tolerance_def.set_parse_action(tolerance_act)
        alias_def.set_parse_action(alias_act)
        alias_value_def.set_parse_action(alias_value_act)
        complex_alias_value_def.set_parse_action(alias_value_act)

        check_image_def.set_parse_action(undefined_act)
        check_complex_def.set_parse_action(undefined_act)
        uncheck_def.set_parse_action(undefined_act)
        unsupported_def.set_parse_action(undefined_act)

        statement_def = (
            cycle_def
            | comments_def
            | check_image_def
            | check_complex_def
            | check_def
            | uncheck_def
            | tolerance_def
            | complex_alias_value_def
            | alias_value_def
            | alias_def
            | set_def
            | unsupported_def
        )

        self._defs = statement_def[...]
