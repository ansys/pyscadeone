# Copyright (C) 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

import pytest

from ansys.scadeone.core.common.versioning import gen_swan_version
from ansys.scadeone.core.common.storage import SwanString
from ansys.scadeone.core.common.logger import LOGGER, LoggerLevel
from ansys.scadeone.core.model.loader import SwanParser
from ansys.scadeone.core.swan import ModuleBase

LOGGER.level = LoggerLevel.DEBUG
LOGGER.log_to_console()


def code(swan_code, module) -> SwanString:
    # code helper to generate SwanString with version header
    return SwanString(gen_swan_version() + "\n" + swan_code, module)


@pytest.fixture(scope="session")
def parser() -> SwanParser:
    return SwanParser(LOGGER)


@pytest.fixture
def body_loader(parser, model):
    # This fixture allows to load a module body from Swan code, and add it to the model.
    def _load(body: list[str]) -> ModuleBase | None:
        if body:
            module = parser.module_body(code(body[0], body[1]))
            model.add_body(module)
            return module
        return None

    return _load


@pytest.fixture
def interface_loader(parser, model):
    # This fixture allows to load a module interface from Swan code, and add it to the model.
    def _load(interface: list[str]) -> ModuleBase | None:
        if interface:
            module = parser.module_interface(code(interface[0], interface[1]))
            model.add_interface(module)
            return module
        return None

    return _load


@pytest.fixture
def decl_check(caplog):
    # This fixture allows to check declaration properties (is_public, is_external) module,
    # and expected log if any.
    def _check(
        name: str,
        module: ModuleBase | None,
        expected: bool,
        property: str,
        log: bool,
    ):
        if module is None:
            # no module, not check
            return
        d = module.get_declaration(name, local_only=True)
        if d is None:
            # no such decl, not check
            return
        res = getattr(d, property)
        assert res == expected, (
            f"Expected decl {d.id}.{property} == {expected} in module {module.name}."
        )
        if log:
            assert "is declared in interface and body of module" in caplog.text, (
                f"Expected log about inconsistent declaration for {name}"
            )

    return _check


@pytest.fixture
def check(body_loader, interface_loader, decl_check):
    # This fixture is automatically used for each test, and
    # allows to check that if a declaration is expected in body and interface.
    def _check(name: str, body, interface, expected, property, log):
        body_mod = body_loader(body)
        interface_mod = interface_loader(interface)
        (log1, log2) = log if isinstance(log, list) else (log, log)
        decl_check(name, body_mod, expected, property, log1)
        decl_check(name, interface_mod, expected, property, log2)

    return _check


class TestPublic:
    @pytest.mark.parametrize(
        "name, body, interface, is_public, log",
        [
            # ----- Constant -----
            # body only, public
            ("C1", ["const C1: int32;", "M"], None, True, False),
            # interface only, public
            ("C2", None, ["const C2: int32;", "M"], True, False),
            # body and interface, public
            ("C3", ["const C3: int32;", "M"], ["const C3: int32;", "M"], True, True),
            # only in body and not in interface, not public
            ("C4", ["const C4: int32;", "M"], ["const X: int32;", "M"], False, False),
            # other interface declaration, public (only check done)
            # ----- Type -----
            # body only, public
            ("T1", ["type T1 = int32;", "M"], None, True, False),
            # interface only, public
            ("T2", None, ["type T2 = int32;", "M"], True, False),
            # body and interface, public
            ("T3", ["type T3 = int32;", "M"], ["type T3 = int32;", "M"], True, True),
            # only in body and not in interface, not public
            ("T4", ["type T4 = int32;", "M"], ["type X = int32;", "M"], False, False),
            # ----- Sensor -----
            # body only, public
            ("S1", ["sensor S1: int32;", "M"], None, True, False),
            # interface only, public
            ("S2", None, ["sensor S2: int32;", "M"], True, False),
            # body and interface, public
            ("S3", ["sensor S3: int32;", "M"], ["sensor S3: int32;", "M"], True, True),
            # only in body and not in interface, not public
            ("S4", ["sensor S4: int32;", "M"], ["sensor X: int32;", "M"], False, False),
            # ----- Group -----
            # body only, public
            ("G1", ["group G1 = (int32);", "M"], None, True, False),
            # interface only, public
            ("G2", None, ["group G2 = (int32);", "M"], True, False),
            # body and interface, public
            ("G3", ["group G3 = (int32);", "M"], ["group G3 = (int32);", "M"], True, True),
            # only in body and not in interface, not public
            ("G4", ["group G4 = (int32);", "M"], ["group X = (int32);", "M"], False, False),
        ],
    )
    def test_public_decl(
        self,
        name,
        body,
        interface,
        is_public,
        log,
        check,
    ):
        check(name, body, interface, is_public, "is_public", log)

    @pytest.mark.parametrize(
        "name, body, interface, is_public, log",
        [
            # Body only, not interface
            ["OP1", ["function OP1 (a: int32)  returns (b: int32) b = a;", "M"], None, True, False],
            # Interface only, not body
            ["OP2", None, ["function OP2 (a: int32)  returns (b: int32);", "M"], True, False],
            # Body and interface, definition and declaration => public
            [
                "OP3",
                ["function OP3 (a: int32) returns (b: int32) b = a;", "M"],
                ["function OP3 (a: int32) returns (b: int32);", "M"],
                True,
                False,
            ],
            # Body and interface, definition and not declaration => private
            [
                "OP4",
                ["function OP4 (a: int32) returns (b: int32) b = a;", "M"],
                ["function XX (a: int32) returns (b: int32);", "M"],
                False,
                False,
            ],
            # Body and interface, two declarations, no definition => public (only check done), warning
            [
                "OP5",
                ["function OP5 (a: int32) returns (b: int32);", "M"],
                ["function OP5 (a: int32) returns (b: int32);", "M"],
                True,
                True,
            ],
        ],
    )
    def test_public_operator(self, name, body, interface, is_public, log, check):
        check(name, body, interface, is_public, "is_public", log)


class TestExternal:
    @pytest.mark.parametrize(
        "name, body, interface, is_external, log",
        [
            # ---- Constant ----
            # Body only, not interface
            ("C1_decl", ["const C1_decl: int32;", "M"], None, True, False),
            ("C2_def", ["const C2: int32 = 42;", "M"], None, False, False),
            # Interface only, no body
            ("C3_decl", None, ["const C3_decl: int32;", "M"], True, False),
            ("C4_def", None, ["const C4: int32 = 42;", "M"], False, False),
            # Warnings
            # /!\ Don't care if definition are not the same, only check declaration presence
            ("C5_decl", ["const C5_decl: int32;", "M"], ["const C5_decl: int32;", "M"], True, True),
            (
                "C6_def",
                ["const C6_def: int32 = 42;", "M"],
                ["const C6_def: int32 = 43;", "M"],
                False,
                True,
            ),
            # ---- Type ----
            # Body only, not interface
            ("T1_decl", ["type T1_decl;", "M"], None, True, False),
            ("T2_def", ["type T2 = int32;", "M"], None, False, False),
            # Interface only, no body
            ("T3_decl", None, ["type T3_decl;", "M"], True, False),
            ("T4_def", None, ["type T4 = int32;", "M"], False, False),
            # Warnings
            # /!\ Don't care if definition are not the same, only check declaration presence
            ("T5_decl", ["type T5_decl;", "M"], ["type T5_decl;", "M"], True, True),
            (
                "T6_def",
                ["type T6_def = int32;", "M"],
                ["type T6_def = float64;", "M"],
                False,
                True,
            ),
        ],
    )
    def test_decl(self, name, body, interface, is_external, log, check):
        check(name, body, interface, is_external, "is_external", log)

    @pytest.mark.parametrize(
        "name, body, interface, is_external, log",
        [
            # ---- Operator with definition => not is_external ----
            # Body only, not interface
            [
                "OP1_def",
                ["function OP1_def (a: int32)  returns (b: int32) b = a;", "M"],
                None,
                False,
                False,
            ],
            # Body and interface
            [
                "OP2_def",
                ["function OP2_def (a: int32)  returns (b: int32) b = a;", "M"],
                ["function OP2_def (a: int32)  returns (b: int32);", "M"],
                False,
                False,
            ],
            # ---- Operator without definition  => is_external ----
            # Body only, not interface
            [
                "OP3_decl",
                ["function OP3_decl (a: int32) returns (b: int32);", "M"],
                None,
                True,
                False,
            ],
            # Interface only, no body
            [
                "OP4_decl",
                None,
                ["function OP4_decl (a: int32) returns (b: int32);", "M"],
                True,
                False,
            ],
            # Body and interface declarations => is_external, and warning
            # Logging is only expected for interface, as one looks for alternative *declaration* in body
            # but not the opposite.
            [
                "OP5_decl",
                ["function OP5_decl (a: int32) returns (b: int32);", "M"],
                ["function OP5_decl (a: int32) returns (b: int32);", "M"],
                True,
                [False, True],
            ],
        ],
    )
    def test_operator(self, name, body, interface, is_external, log, check):
        check(name, body, interface, is_external, "is_external", log)

    @pytest.mark.parametrize(
        "name, body, interface",
        [
            ("S1", ["sensor S1: int32;", "M"], None),
            ("S2", None, ["sensor S2: int32;", "M"]),
            ("G1", ["group G1 = (int32);", "M"], None),
            ("G2", None, ["group G2 = (int32);", "M"]),
        ],
    )
    def test_sensor_group(self, name, body, interface, body_loader, interface_loader):
        body_mod = body_loader(body)
        interface_mod = interface_loader(interface)
        for module in [body_mod, interface_mod]:
            if module is None:
                continue
            d = module.get_declaration(name, local_only=True)
            assert not d.is_external, (
                f"Expected decl {d.id} to not be external in module {module.name}."
            )
