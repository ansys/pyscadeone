Pragma
======

.. currentmodule:: ansys.scadeone.core.swan

From a lexical point of view, pragmas are of the form ``#pragma...#end`` where ``...`` is
any text, with ``##`` to denotes ``#`` to avoid confusion with an enclosed ``#end``. 
Practical pragmas are of the form ``#pragma pragma_name <some content> #end`` 
where *some content* is any character string, including spaces and newlines.

A :py:class:`Pragma` object stores a pragma information as a *key* for the pragma name and a *value*
for the pragma content (*value* can be empty). The :py:class:`Pragma` class is the base class for all pragmas, 
including diagram pragmas and other pragmas. It is also used to represent pragmas that 
are not (yet) known to the library.

.. figure:: pragma.svg

   Pragma class diagram

.. autoclass:: Pragma
    :exclude-members: to_str
