Diagram navigation
==================

The diagram navigation API allows to find the sources and the targets of a block in a diagram.

Only the :py:class:`DefBlock`, :py:class:`ExprBlock`, :py:class:`Block`, and :py:class:`Block` are concerned, as they are connected by :py:class:`Wire`.

The ``sources`` and ``targets`` properties are defined for these classes.
The :ref:`diagram_nav_ex` example shows how to use these properties.

Sources property
----------------

The ``sources`` property provides the list of block sources, that is, all the blocks
that are connected to the block inputs. 

The list is a tuple of the form: (*diagram_object*, *source_adaptation*, List[*target_adaptation*]|None), where:

diagram_object:
    is a diagram object connected as a source of the current block.

source_adaptation:
    is an adaptation from the *diagram_object*, giving which outputs of the source
    and how the outputs are connected (index, name, and so on).

    Note that there may be no *source_adaptation* if there is a single connection.

target_adaptation:
    is an adaptation to the current object, giving which input of the current block
    and how the input is connected (index, name, and so on).

    One may have several *target_adaptation* if the source is connected to several
    inputs. The *target_adaptation* is *None* if there is no specific adaptation.


Targets property
----------------

The ``targets`` property provides the list of block targets, that is, all the blocks
that are connected to the block outputs. 

The list is a tuple of the form: (*diagram_object*, *source_adaptation*, *target_adaptation*), where:

diagram_object:
    is a diagram object connected as an output of the current block.

source_adaptation:
    is an adaptation from the *diagram_object*, giving which inputs of the target 
    and how the inputs are connected (index, name, and so on).

target_adaptation:
    is an adaptation to the current object, giving which input and how the input is connected (index, name, and so on).




