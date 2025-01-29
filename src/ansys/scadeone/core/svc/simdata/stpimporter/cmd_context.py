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

from pathlib import Path
import re
from typing import Any, cast

import ansys.scadeone.core.svc.simdata as sd

from .sss_parser import SSSParser as Parser
from .swan_context import SwanContext
from .utils import ConverterLogger, SDType

# cSpell: ignore sdtype, sdio

SSSParser = Parser()

VarPathRE = re.compile(r"^(?:\w+::)*\w+(?:/\w+)?$")


class SDContextBase:
    def get_alias_value(self, alias: str) -> Any:
        pass

    def get_enum(self, _: str) -> Any:
        pass

    def get_constant_value(self, _: str) -> Any:
        pass

    def get_constant(self, _: str) -> Any:
        pass

    @property
    def evaluated_cmd(self) -> str:
        pass

    def failed_cmd(self, error: str):
        ConverterLogger.exception(f"Failed command: {self.evaluated_cmd}\nReason: {error}")


class Atom:
    """Stores SSS values from parsing. The values are the first element of the
     token list, then it is a value which can be a string, a number, a boolean,
    a char or a list of these types. A string between simple-quote denotes a
    character."""

    def __init__(self, tokens: list):
        # token is a list of list
        self._tokens = tokens

    @property
    def value(self):
        return self._tokens[0]

    def check_value(self, ctx: SDContextBase, sd_type: sd.Type):
        # ConverterLogger.exception if the value is not supported
        value = self._check_value(self.value, ctx, sd_type)
        self._tokens[0] = value

    def _check_array_value(self, value, ctx: SDContextBase, base_type: sd.Type, dims: list[int]):
        """Checks an array value and performs processing of "<string>".
        A value must be resolved: no alias
        """
        if len(dims) > 1:
            return [
                self._check_array_value(sub_value, ctx, base_type, dims[1:]) for sub_value in value
            ]
        if (
            isinstance(base_type, sd.PredefinedType)
            and base_type.kind == sd.PredefinedTypeKind.CHAR
            and not isinstance(value, list)
        ):
            assert isinstance(value, str) and value[0] == '"'
            chars = SSSParser.string_to_chars(value)
            if len(chars) > dims[0]:
                chars = chars[0 : dims[0]]
            else:
                chars += ["\0"] * (dims[0] - len(chars))
            return chars
        return [self._check_value(v, ctx, base_type) for v in value]

    def _check_atomic_value(self, value, ctx: SDContextBase, sd_type):
        """Checks an atomic value, i.e.
        - a numeric value,
        - a char,
        - an enum,
        - a constant expr,
        - an alias,
        - float specials (error),
        - SSS specials: ? or <empty>

        '"<string>"' value must have been processed by _check_array_value
        """
        if isinstance(value, str):
            if value == "?" or value == "<empty>":
                ctx.failed_cmd(f"Unsupported partial value ({value})")
            if value[0] == "'":
                # char
                return SSSParser.to_char(value)
            if value[0] == '"':
                assert isinstance(sd_type, sd.ArrayType)
                res = self._check_array_value(value, ctx, sd_type.base_type, sd_type.dims)
                return res
            if value in ("NaN", "qNaN", "sNaN", "+Inf", "-Inf"):
                # unsupported float values
                ctx.failed_cmd(f"Unsupported float: {value}")

            if alias := cast(Atom, ctx.get_alias_value(value)):
                alias.check_value(ctx, sd_type)
                return alias.value

            if isinstance(sd_type, sd.EnumType):
                if enum_val := ctx.get_enum(value):
                    return enum_val
                # could be a constant
                if cst_value := ctx.get_constant_value(value):
                    ctx.failed_cmd(f"Invalid enum from constant: {value} (not implemented)")
                ctx.failed_cmd(f"Invalid enum from: {value}")

            cst_value = ctx.get_constant_value(value)
            if cst_value is not None:
                return cst_value
            # Can be a char value
            if (
                isinstance(sd_type, sd.PredefinedType)
                and sd_type.kind == sd.PredefinedTypeKind.CHAR
                and len(value) == 1
            ):
                return value

            ctx.failed_cmd(f"Invalid value from: {value}")
        # other types: int, float, bool
        if isinstance(sd_type, sd.EnumType) and isinstance(value, int):
            ctx.failed_cmd(f"Integer value not supported for enum\n{ctx.evaluated_cmd}")
        return value

    def _check_value(self, value, ctx: SDContextBase, sd_type: sd.Type) -> Any:
        """Checks if the value is supported and returns it.
        Performs alias resolution.
        """
        if not isinstance(value, list):
            return self._check_atomic_value(value, ctx, sd_type)

        if isinstance(sd_type, sd.StructType):
            # value must be a list
            assert isinstance(value, list)
            field_types = [f.sd_type for f in sd_type.fields]
            res = [self._check_value(v, ctx, t) for v, t in zip(value, field_types)]
            return res

        if isinstance(sd_type, sd.EnumType):
            assert isinstance(value, list)
            return [self._check_value(v, ctx, sd_type) for v in value]

        if isinstance(sd_type, sd.ArrayType):
            res = self._check_array_value(value, ctx, sd_type.base_type, sd_type.dims)
            return res

    def __str__(self):
        return str(self.value)


class SwanVar:
    """Class to separate the module, the scope and the name of a sss variable name string"""

    def __init__(self, var: str) -> None:
        self._module = None
        self._scope = None
        name_split = var.split("::")
        if len(name_split) == 2:
            self._module = name_split[0]
        var = name_split[-1]
        name_split = var.split("/")
        if len(name_split) == 2:
            self._scope = name_split[0]
        self._name = name_split[-1]

    @property
    def module(self) -> str:
        """Gets module of swan variable"""
        return self._module

    @property
    def scope(self) -> str:
        """Gets scope of swan variable"""
        return self._scope

    @property
    def name(self) -> str:
        """Gets name of swan variable"""
        return self._name

    def __str__(self):
        return f"module {self._module}: scope {self._scope}: name {self._name}"


class SDVar:
    """
    Parent class for simdata variables state
    """

    def __init__(self, name: str, element: sd.Element) -> None:
        self._name = name
        self._next_value = None  # values to be applied next cycles apply
        self._active_cycles = 0  # number of times to be played next
        self._element = element  # simdata file element
        self._sustain = (
            0  # number of times to be played again before back to none, zero = not limit
        )

    @property
    def name(self) -> str:
        """Gets variable name"""
        return self._name

    @property
    def element(self) -> sd.Element:
        """Gets associated simdata element"""
        return self._element

    @property
    def type(self) -> sd.Type:
        """Gets associated simdata element type"""
        return self.element.sd_type if self.element else None

    @property
    def active_cycles(self) -> int:
        """Gets number of cycles left to assign in the current state"""
        return self._active_cycles

    @property
    def sustain(self) -> int:
        """Gets cycles to play in case of checks"""
        return self._sustain

    @sustain.setter
    def sustain(self, sustain: int) -> None:
        """Sets cycles to play for a check"""
        self._sustain = sustain

    @property
    def value(self):
        """Gets the next value to be assigned to variable"""
        return self._next_value

    @value.setter
    def value(self, value=None) -> None:
        """Updates the value of sd variable after appending previous values
        to file element if any.
        If no value given, will only append previous values.

        Parameters
        ----------
        value : Any, optional
            new value to affect
        """
        pass

    def cycle_start(self, past_cycles: int) -> None:
        """Defines when this element is initialized

        Parameters
        ----------
        past_cycles : int
            number of cycles spent before element initialization
        """
        pass

    def add_cycles(self, n: int) -> None:
        """Increases number of cycles to append to sd variable.

        Parameters
        ----------
        n : int
            number of new cycles
        """
        pass

    def terminate(self) -> None:
        """Final operation for variable.
        Sets remaining values to file if any"""
        pass


class SDVarSimple(SDVar):
    """Class for simple predefined type SD variables"""

    def __init__(self, name: str, element: sd.Element) -> None:
        super().__init__(name, element)

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, value=None) -> None:
        if self._active_cycles > 0:
            if self._next_value is None:
                self._element.append_nones(self._active_cycles)
            else:
                self._element.append_values([self._next_value], self._active_cycles)
            self._active_cycles = 0

        self._next_value = None if value is None else value.value

    def cycle_start(self, past_cycles: int) -> None:
        self._element.append_nones(past_cycles)

    def add_cycles(self, n: int) -> None:
        total_cycles = self._active_cycles + n
        if self._sustain and self._sustain <= total_cycles:
            self._active_cycles = self._sustain
            self.value = None

            self._active_cycles = total_cycles - self._sustain
            self._sustain = 0
        else:
            self._active_cycles = total_cycles

    def terminate(self) -> None:
        self.value = None


class SDVarStruct(SDVar):
    """Class for structured variables.
    Structured values are only assigned at the end of parsing,
    due to how structured simdata types do not support more than one sequence"""

    def __init__(self, name: str, element: sd.Element) -> None:
        super().__init__(name, element)
        self._sequence_value = []

    @property
    def value(self):
        return super().value

    @value.setter
    def value(self, value=None) -> None:
        if value is None:
            self._next_value = None
            return
        else:
            eval_value = value.value
            self._next_value = eval_value

    def cycle_start(self, past_cycles: int) -> None:
        self._sequence_value = [None] * past_cycles

    def add_cycles(self, n: int) -> None:
        self._sequence_value += [self._next_value] * n

    def terminate(self) -> None:
        if None in self._sequence_value:
            if any(self._sequence_value):
                ConverterLogger.warning(
                    "Structured types do not support combination of values and nones. "
                    "Structured values must be defined for every cycle. "
                    f"Variable {self._name} will not be initialized."
                )
            self._element.append_nones(len(self._sequence_value))
        else:
            try:
                self._element.append_values(self._sequence_value)
            except Exception as e:
                raise e


class SDVarNone(SDVar):
    """Class for unsupported SD variables.
    That is complex structure type variables or which type was not found"""

    pass


class SDContext(SDContextBase):
    """
    Context for simdata writing
    Contains current state of it: cycle number, list of SDvariables with their respective state,
    sd file and associated swan context in order to find variable types
    """

    def __init__(self, swan_ctx: SwanContext) -> None:
        self._vars: dict[str, SDVar] = {}
        self._vars_aliases = {}
        self._values_aliases: dict[str, Atom] = {}
        self._sdf = None
        self._sdio_type = None
        self._current_cycle = 0
        self._swan_ctx = swan_ctx
        self._cmds = []
        self._evaluated_cmd = None

    @property
    def evaluated_cmd(self) -> str:
        return self._evaluated_cmd

    def parse_file(self, file: Path) -> None:
        """Parse content of a file and append commands"""
        ConverterLogger.info(f"Parsing file:\n{file}")
        self._cmds.extend(SSSParser.parse_file(file))

    def reset_vars(self) -> None:
        """Resets all the simdata variables"""
        self._vars = {}
        self._vars_aliases = {}

    @property
    def sdf(self) -> sd.FileBase:
        """Gets current associated simdata file"""
        return self._sdf

    @sdf.setter
    def sdf(self, value: sd.FileBase) -> None:
        """Associates a simdata file"""
        self._sdf = value

    @property
    def sdio_type(self) -> SDType:
        """Gets conversion mode : input or output (checks)"""
        return self._sdio_type

    @sdio_type.setter
    def sdio_type(self, type: SDType) -> None:
        """Sets conversion mode : input or output"""
        self._sdio_type = type

    def init_var(self, sig_name: str, type: sd.Type, is_sensor: bool = False):
        swan_var = SwanVar(sig_name)
        short_name = swan_var.name
        element = self._sdf.add_element(
            sig_name.replace("::", "_") if is_sensor else short_name, type
        )

        if type is None:
            self._vars[sig_name] = SDVarNone(sig_name, element)
            ConverterLogger.error(f"Unsupported type: variable {sig_name} will not be converted!")
            return
        elif isinstance(type, sd.PredefinedType) or isinstance(type, sd.EnumType):
            self._vars[sig_name] = SDVarSimple(sig_name, element)
        else:
            self._vars[sig_name] = SDVarStruct(sig_name, element)

        if self._current_cycle > 0:
            self._vars[sig_name].cycle_start(self._current_cycle)

    def init_all_vars(self) -> None:
        """Inits all inputs or outputs by creating SD elements
        with their respective type"""

        if self._sdio_type == SDType.INPUT:
            items = self._swan_ctx.inputs.items()
        elif self._sdio_type == SDType.OUTPUT:
            items = self._swan_ctx.outputs.items()
        else:
            items = []
        for sig_name, type in items:
            self.init_var(sig_name, type)

    def get_var(self, sss_name: str) -> SDVar:
        """Gets an SD element from its name"""

        # check if name is an alias
        sss_name = self._vars_aliases.get(sss_name, sss_name)
        if sss_name.find("/") == -1:
            # Sensor
            resolved_name = self.get_sensor(sss_name)
        else:
            # Operator I/O, probes
            if sss_name.find("::") == -1:
                resolved_name = self._swan_ctx.operator_module + "::" + sss_name
            else:
                (path, name) = sss_name.split("/")
                resolved_path, _ = self._swan_ctx.get_renamed("operator", path)
                resolved_name = resolved_path + "/" + name

        if resolved_name not in self._vars:
            ConverterLogger.exception(f"Variable {resolved_name} not found")

        return self._vars[resolved_name]

    def get_sensor(self, name: str) -> str:
        """Gets the sensor name from the swan context and returns its full name"""
        (resolved_name, _) = self._swan_ctx.get_renamed("sensor", name)
        if resolved_name not in self._vars:
            sensor_type = self._swan_ctx.get_sensor_sd_type(resolved_name)
            if sensor_type is not None:
                self.init_var(resolved_name, sensor_type, True)
            else:
                ConverterLogger.error(f"A Swan variable could not be found: {name}")
                self._vars[resolved_name] = SDVarNone(resolved_name, None)
        return resolved_name

    def is_supported_name(self, name: str) -> bool:
        """Test if the variable name passes some checks"""

        if not name:
            ConverterLogger.error("Variable name cannot be empty")
            return False
        m = VarPathRE.match(name)
        if m is None:
            ConverterLogger.error(f"Variable name not supported: {name}")
            return False
        return True

    def get_alias_value(self, alias: str) -> Any:
        """Gets the value of an alias"""
        if alias in self._values_aliases:
            (value, complex) = self._values_aliases[alias]
            if value:
                return value
            ConverterLogger.exception(f"Unsupported alias value: {alias} {' '.join(complex)}")
        return None

    def get_enum(self, value: str) -> Any:
        """Finds the enum value from the swan context"""
        return self._swan_ctx.get_enum(value)

    def get_constant_value(self, value: str) -> Any:
        """Finds the constant value from the swan context"""
        return self._swan_ctx.get_constant_value(value, no_const_ok=True)

    def get_constant(self, value: str) -> Any:
        """Finds the constant value from the swan context"""
        return self._swan_ctx.get_constant(value)

    def eval_cmds(self) -> None:
        self.init_all_vars()
        for cmd in self._cmds:
            ConverterLogger.debug(f"Eval: {str(cmd)}")
            self._evaluated_cmd = str(cmd)
            try:
                cmd.eval(self)
            except Exception:
                pass
        self.finish()
        self.reset_vars()

    def eval_alias(self, name: str, variable: str) -> None:
        """Creates alias for a variable

        Parameters
        ----------
        name : str
            alias
        variable : str
            full name variable
        """

        if self.is_supported_name(variable):
            self._vars_aliases[name] = variable

    def eval_alias_value(self, alias: str, value: Atom, complex: str) -> None:
        """Creates alias for a value

        Parameters
        ----------
        alias : str
            alias
        value : Any
            value
        """
        self._values_aliases[alias] = (value, complex)

    def eval_set(self, name: str, value: Atom) -> None:
        """Sets a variable to a value

        Parameters
        ----------
        name : str
            variable name
        value : Any
            value with the variable type
        """
        if self.is_supported_name(name) and self._sdio_type == SDType.INPUT:
            sd_var = self.get_var(name)
            if sd_var.type is None:
                return
            value.check_value(self, sd_var.type)
            try:
                sd_var.value = value
            except Exception as e:
                self.failed_cmd(str(e))

    def eval_cycle(self, nb: int) -> None:
        """Increment cycles for all sd variables

        Parameters
        ----------
        nb : int
            number of cycles
        """

        for sig in self._vars.values():
            sig.add_cycles(nb)
        self._current_cycle += nb

    # Oracles
    def eval_check(self, name: str, value: Atom, sustain: int, real: Any) -> None:
        """Sets an oracle check

        Parameters
        ----------
        name : str
            variable name
        value : Any
            value with the check variable type
        sustain : int
            number of cycles persistence
        """

        if self.is_supported_name(name) and self._sdio_type == SDType.OUTPUT:
            if real:
                ConverterLogger.warning(f"Unsupported SSM::check real option {self.evaluated_cmd}")
            sd_var = self.get_var(name)
            if sd_var.type is None:
                return
            value.check_value(self, sd_var.type)
            try:
                sd_var.value = value
                sd_var.sustain = sustain
            except Exception as e:
                self.failed_cmd(str(e))

    def eval_uncheck(self, name: str) -> None:
        """Removes an oracle check

        Parameters
        ----------
        name : str
            check variable name
        """

        if self._sdio_type == SDType.OUTPUT:
            sd_var = self.get_var(name)
            sd_var.value = None

    def finish(self) -> None:
        """
        Final operations to apply to sd file creation
        Must be called at the end of the sss files parsing
        Fills any variable so that the number of values is equal for all of them.
        Fills oracles with nones.
        Ignore variables that never got any value.
        """

        for sd_var in self._vars.values():
            sd_var.terminate()

        self._current_cycle = 0

    def eval_unsupported(self, line: str) -> None:
        """Logs a SSM command that will not be treated

        Parameters
        ----------
        line : str
            The command line
        """
        if self._sdio_type == SDType.INPUT:
            # Arbitrary choice to avoid logging twice the same lines
            ConverterLogger.warning(f"Unsupported command: {line}")


class SSSCmd:
    """
    Parent class for SSM commands
    """

    def eval(self, context: SDContext) -> None:
        pass


class SSSCycle(SSSCmd):
    """SSM::cycle [[ <integer> ]]
    Apply cycles to registered values"""

    def __init__(self, cycle) -> None:
        super().__init__()
        self._cycle = int(cycle)

    def eval(self, context: SDContext) -> None:
        context.eval_cycle(self._cycle)

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name} {self._cycle}"


class SSSSet(SSSCmd):
    """SSM::set <var> <val>
    Setting values"""

    def __init__(self, signal: str, value: Atom) -> None:
        super().__init__()
        self._value = value
        self._signal = signal

    def eval(self, context: SDContext) -> None:
        context.eval_set(self._signal, self._value)

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name} {self._signal} {self._value}"


class SSSCheck(SSSCmd):
    """SSM::check <var> <expected val> {{ <check var arg> }
    Not supported for images check"""

    def __init__(self, signal, value: Atom, sustain, real) -> None:
        super().__init__()
        self._value = value
        self._signal = signal
        self._sustain = sustain
        self._real = real

    def eval(self, context: SDContext) -> None:
        context.eval_check(self._signal, self._value, self._sustain, self._real)

    def __str__(self) -> str:
        name = self.__class__.__name__
        real = f"real={self._real}" if self._real else ""
        if self._sustain == 0:
            sustain = "sustain=forever"
        elif self._sustain == 1:
            sustain = ""
        else:
            sustain = f"sustain={self._sustain}"
        return f"{name} {self._signal} {self._value} {sustain} {real}"


class SSSTolerance(SSSCmd):
    """SSM::set_tolerance {{ <tolerance arg> }}
    Not supported in sd files"""

    def __init__(self, line) -> None:
        super().__init__()
        self._line = line

    def eval(self, context: SDContext) -> None:
        context.eval_unsupported(f"SSM::set_tolerance{self._line}")

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name} {self._line}"


class SSSUncheck(SSSCmd):
    """SSM::uncheck <var>
    Not supported in sd files"""

    def __init__(self, line) -> None:
        super().__init__()
        self._line = line

    def eval(self, ctx: SDContext) -> None:
        ctx.eval_unsupported(f"SSM::uncheck {self._line}")

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name} {self._line}"


class SSSAlias(SSSCmd):
    """SSM::alias <alias> <var>"""

    def __init__(self, signal, value) -> None:
        super().__init__()
        self._value = value
        self._signal = signal

    def eval(self, context: SDContext) -> None:
        context.eval_alias(self._signal, self._value)

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name} {self._signal} {self._value}"


class SSSAliasValue(SSSCmd):
    """SSM::alias_value <alias> <var>"""

    def __init__(self, alias: str, value: Atom, complex: str) -> None:
        super().__init__()
        self._alias = alias
        self._value = value
        self._complex = complex

    def eval(self, context: SDContext) -> None:
        context.eval_alias_value(self._alias, self._value, self._complex)

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name} {self._alias} {self._value}"


class SSSUnsupported(SSSCmd):
    """Unsupported SSM actions"""

    def __init__(self, line) -> None:
        super().__init__()
        self._line = line

    def eval(self, context: SDContext) -> None:
        context.eval_unsupported(self._line)

    def __str__(self) -> str:
        name = self.__class__.__name__
        return f"{name} {self._line}"


SSSParser.initialize(
    atom=Atom,
    sss_set=SSSSet,
    sss_check=SSSCheck,
    sss_alias=SSSAlias,
    sss_alias_value=SSSAliasValue,
    sss_cycle=SSSCycle,
    sss_tolerance=SSSTolerance,
    unsupported=SSSUnsupported,
)
