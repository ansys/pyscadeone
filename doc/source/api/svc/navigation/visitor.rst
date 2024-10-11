.. _Swan Model Visitor:

Swan Model Visitor
==================

.. currentmodule:: ansys.scadeone.core.svc.swan_visitor

.. _visitor: https://en.wikipedia.org/wiki/Visitor_pattern

The `visitor`_ pattern is a design pattern allowing to separate algorithm and object structure.

Data structure objects have an ``accept`` method, which has the visitor object as argument.
In turn, the visitor object does some process onto the calling object. By deriving the 
visitor class, different algorithms can be implemented. In that scheme, the data structure 
is responsible for the traversal. 

The Swan visitor works a little differently. The visitor knows about the Swan objects tree
and is responsible for the tree traversal. There is no ``accept`` method for the Swan classes.
The advantage is that the traversal can be controlled by a derived visitor class.

See :ref:`Visitor Example` for a complete code example.

Overview
--------

The :py:class:`SwanVisitor` implements the base visitor. It provides:

* The :py:meth:`SwanVisitor.visit` which is the entry point to start visiting an object.
* The methods *SwanVisitor.visit_<class_name>(swan_obj: object, owner: object, property: str)*. There
  is one such method for each Swan classes. The :py:meth:`SwanVisitor.visit` method calls the 
  private :py:meth:`SwanVisitor._visit` method which dispatches the Swan object argument to the
  proper *SwanVisitor.visit_<class_name>* method. Arguments of *SwanVisitor.visit_<class_name>* are:

  * *swan_obj*: the visited object.
  * *owner*: when an object is visited, the default visitor traverses the objects referenced by the properties
    set by the constructor. The *owner* is the owner of the property. *owner* is **None** for the root 
    visited object.
  * *property*: when visiting a property, its name is given to that parameter to know about the visit context.

For instance, if one visits an :py:class:`ArrayRepetition` object, there are two properties with the same
:py:class:`Expression` type. The corresponding default visitor method is:

.. code:: python

    def visit_ArrayRepetition(
        self,
        swan_obj: swan.ArrayRepetition,
        owner: Union[Any, None],
        property: Union[str, None]
    ) -> None:
        """ArrayRepetition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, 'expr')
        self._visit(swan_obj.size, swan_obj,  'size')

Visiting the ``expr`` and the ``size`` may lead to the call of the same visitor method. Therefore,
the property argument discriminates the context together with the ``owner``.

Note that the base class :py:class:`Expression` is visited first.

Usage
-----

The default visitor does nothing but tree traversal. Therefore, one needs to derive 
a visitor with some meaningful operation.

.. code:: python

    from typing import Any, Union
    from ansys.scadeone.core.svc.swan_visitor import SwanVisitor

    class MyVisitor(SwanVisitor):

        def __init__(self, *args):
            # process my visitor own args
            super().__init__()

The methods of :py:class:`SwanVisitor` can be overridden as needed. If one wants to perform a systematic
action while visiting an item, override the :py:meth:`SwanVisitor._visit` method:

.. code:: python

    def _visit(
        self, swan_obj: Any,
        owner: Union[Any,None],
        property: Union[str,None]
    ) -> None:
        # Add some pre-processing here
        super()._visit(swan_obj, owner, property)
        # add some post-process here

Override any method for which an action is required. Example for a sensor:

.. code:: python

    def visit_SensorDecl(
        self,
        swan_obj: swan.SensorDecl,
        owner: Union[Any, None],
        property: Union[str, None]
    ) -> None:
        # do some pre-processing
        super().visit_SensorDecl(swan_obj, owner, property)
        # do some post-processing

Or one can take the default code and write specific processing. Example for an operator:

.. code:: python

    def visit_Operator(
        self,
        swan_obj: swan.Operator,
        owner: Union[Any, None],
        property: Union[str, None]
    ) -> None:
        # do specific processing.
        # for instance, do not explore inputs/outputs, body, ...
        # which stops the traversal.

.. note::

    The visitor defines also some specific functions that have no specific behavior:

    - :py:meth:`SwanVisitor.visit_builtin`: this method is called for an object of type ``str``, ``bool``, ``int``, ``float``.
    - :py:meth:`SwanVisitor.visit_SwanItem`: this method is called when visiting a SwanItem, which is the base class of
      most of the Swan classes. If it has an action, it will be done for all instances derived from a SwanItem.


Visitor API
-----------

This section describes all the methods of the :py:class:`SwanVisitor`.

.. automodule:: ansys.scadeone.core.svc.swan_visitor
    :private-members:

