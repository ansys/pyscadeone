# Copyright (c) 2022-2024 ANSYS, Inc.
# Unauthorized use, distribution, or duplication is prohibited.
"""
This module contains the classes for global definitions:
constants (const) and sensors.
"""
from typing import Optional, Union

import ansys.scadeone.core.swan.common as common


class ConstDecl(common.Declaration):
    """Constant declaration, with an id, a type, and an optional expression."""

    def __init__(
        self,
        id: common.Identifier,
        type: Optional[common.TypeExpression],
        value: Optional[common.Expression] = None,
    ) -> None:
        super().__init__(id)
        self._type_expr = type
        self._value = value

    @property
    def type(self) -> Union[common.TypeExpression, None]:
        """Type of constant."""
        return self._type_expr

    @property
    def value(self) -> Union[common.Expression, None]:
        """Constant optional value. None if undefined."""
        return self._value

    def __str__(self) -> str:
        type = f": {self.type}" if self.type else ""
        decl = self.id
        init = f" = {self.value}" if self.value else ""
        return f"{decl}{type}{init}"


class SensorDecl(common.Declaration):
    """Sensor declaration with an id and a type."""

    def __init__(self, id: common.Identifier, type: common.TypeExpression) -> None:
        super().__init__(id)
        self._type = type

    @property
    def type(self) -> common.TypeExpression:
        """Sensor type."""
        return self._type

    def __str__(self) -> str:
        return f"{self.id}: {self.type}"
