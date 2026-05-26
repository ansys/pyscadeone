Code generation pragmas
=======================

.. currentmodule:: ansys.scadeone.core.swan

Code generation
----------------

The :py:class:`CGPragma` class stores pragmas used by the code generator.
Please refer to the code generation documentation for more details on how to use these pragmas.

The recognized pragmas are defined in the :py:class:`CGPragmaKind` enumeration.
Use the method :py:meth:`CGPragma.kind` to determine the kind of the pragma, and use
the appropriate method to retrieve the pragma content is any.

.. autoclass:: CGPragma

.. autoclass:: CGPragmaKind

