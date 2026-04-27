.. _ref_swan_model_visitor:

Swan model visitor
==================

.. currentmodule:: ansys.scadeone.core.svc.swan_visitor

.. _visitor: https://en.wikipedia.org/wiki/Visitor_pattern

The `visitor`_ pattern allows for a traversal of a data structure without changing the data structure itself.
Thus, several algorithms can be applied to the same data structure. 

The Swan visitor implements that pattern with a class which methods to visit each Swan object. T
he visitor is therefore responsible for the traversal. The visitor by itself does nothing 
but traversing the tree. To implement an algorithm, one needs to derive the visitor class and override all 
or some of the methods.

The advantage of that visitor is that the traversal can be controlled by a derived visitor class,
instead of the ``accept`` method as in the `visitor`_ pattern.


For a complete code example, see :ref:`ref_visitor_example`.

Overview
--------

The :py:class:`SwanVisitor` implements the base visitor. It provides:

* The :py:meth:`SwanVisitor.visit` which is the entry point to start visiting an object.
* The methods *SwanVisitor.visit_<class_name>(swan_obj: object, owner: object, property: str)*. There
  is one such method for each Swan classes. The :py:meth:`SwanVisitor.visit` method calls the 
  private :py:meth:`SwanVisitor._visit` method which dispatches the Swan object argument to the
  proper *SwanVisitor.visit_<class_name>* method. Arguments of *SwanVisitor.visit_<class_name>* are:

  * *swan_obj*: the visited object.
  * *owner*: owner of the *swan_object*. When an object is visited, it becomes the *owner* for its own properties which
    are visited. Note that there is a property for each *owner* constructor argument. 
    The *owner* is **None** for the root visited object.
  * *owner_property*: the name of the property in the *owner* which corresponds to the visited *swan_obj*.
    It is **None** for the root visited object.

For instance, if one visits an :py:class:`ArrayRepetition` object, there are two properties with the same
:py:class:`Expression` type. The corresponding default visitor method is:

.. code:: python

    def visit_ArrayRepetition(
        self,
        swan_obj: swan.ArrayRepetition,
        owner: Owner,
        owner_property: OwnerProperty
    ) -> None:
        """ArrayRepetition visitor function. Should be overridden."""
        # Visit base class(es)
        self.visit_Expression(swan_obj, owner, property)
        # Visit properties
        self._visit(swan_obj.expr, swan_obj, 'expr')
        self._visit(swan_obj.size, swan_obj,  'size')

The base class :py:class:`Expression` is visited first. Then the properties ``expr`` and ``size`` are visited.
For each property, the *owner* is obviously the currently visited *swan_obj*. Here one can see that
the *owner* notion is not enough to discriminate the context, as one visits the same type of object (an expression).
The corresponding property names ``expr`` and  ``size`` help to discriminated the context. In UML terminology, they would
correspond to a *role*.

Usage
-----

The default visitor does nothing but tree traversal. Therefore, one needs to derive 
a visitor with some meaningful operation.

.. code:: python

    from typing import Any, Union
    from ansys.scadeone.core.svc.swan_visitor import SwanVisitor, Owner, OwnerProperty

    class MyVisitor(SwanVisitor):

        def __init__(self, *args):
            # process my visitor own args
            super().__init__()

The methods of :py:class:`SwanVisitor` can be overridden as needed. If one wants to perform a systematic
action while visiting an item, override the :py:meth:`SwanVisitor._visit` method:

.. code:: python

    def _visit(
        self, swan_obj: Any,
        owner: Owner,
        owner_property: OwnerProperty
    ) -> None:
        # Add some pre-processing here
        super()._visit(swan_obj, owner, property)
        # add some post-process here

Override any method for which an action is required. Example for a sensor:

.. code:: python

    def visit_SensorDecl(
        self,
        swan_obj: swan.SensorDecl,
        owner: Owner,
        owner_property: OwnerProperty
    ) -> None:
        # do some pre-processing
        super().visit_SensorDecl(swan_obj, owner, property)
        # do some post-processing

Or one can take the default code and write specific processing. Example for an operator:

.. code:: python

    def visit_Operator(
        self,
        swan_obj: swan.Operator,
        owner: Owner,
        owner_property: OwnerProperty
    ) -> None:
        # do specific processing.
        # for instance, do not explore inputs/outputs, body, ...
        # which stops the traversal.


SwanVisitor class
-----------------

This section describes the methods of the :py:class:`SwanVisitor`.


.. py:class:: SwanVisitor
    :canonical: ansys.scadeone.core.svc.swan_visitor.SwanVisitor.visitor

    .. automethod:: visit

    .. automethod:: visit_builtin

    .. automethod:: visit_SwanItem


    A method is provided for each Swan class. The method name is *visit_<SwanClass>*.
    For instance, for the :py:class:`Operator` class, the method is *visit_Operator*.
    The method provides the traversal of the object and its properties. It should be overridden
    for a specific processing. Look at source in `ansys.scadeone.core.svc.swan_visitor.SwanVisitor.visitor.py`.


    .. py:method:: visit_<SwanClass>(swan_obj: object, owner: object, property: str) -> None

        Visit a Swan object of type <SwanClass>. This method should be overridden.

        :param swan_obj: the visited object.
        :param owner: owner of the *swan_object*. The *owner* is **None** for the root visited object.
        :param owner_property: the name of the property in the *owner* which corresponds to the visited *swan_obj*.
            It is **None** for the root visited object.
