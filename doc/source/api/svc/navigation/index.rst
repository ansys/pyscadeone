Model Navigation
================

This section describes the API to navigate through model elements. 

A Swan API object represents a Swan *construct* and gives access to each construct *children*
of the *construct* as a *raw* low-level access, but higher-level access is sometimes required,
like accessing an instance through its *path_id* (or name).

A general tree walk is implemented by the :py:class:`Visitor` class.

.. toctree::
   :maxdepth: 2

   namespace
   diagram
   visitor
