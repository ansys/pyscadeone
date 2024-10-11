========
Overview
========

The PyScadeOne API is built around the :py:class:`ansys.scadeone.core.ScadeOne` class.
This class is the entry point to other APIs to manipulate project and Swan models.

Here is the class diagram showing the relationships between classes.

.. uml::
   :align: center
   
   @startuml ScadeOne

   ScadeOne "1" *-- "*" Project

   note left of ScadeOne
   Scade One instance
   end note

   note left of Project
   Loaded project(s) see [[/api/project.html Project]]
   end note
   Project --> "*" Project
   note right on link
   Project dependencies
   end note

   Project *-- Model
   note right of Model
   A [[/api/model.html Model]] object contains the Swan modules of
   the project.
   end note

   Model "1" *-- "*" ModuleBody
   Model "1" *-- "*" ModuleInterface

   note as ModuleNote
   Module body and interface classes are
   described in the [[/api/language Swan section]]
   end note

   ModuleBody .. ModuleNote
   ModuleInterface .. ModuleNote

   @enduml

A *ScadeOne* instance is created as follows:

.. code:: python

   from ansys.scadeone.core import ScadeOne
   
   app = ScadeOne(install_dir="<Scade One installation dir>")
   project = app.load_project("project.sproj")

or it can be created using a context manager:

.. code:: python

   from ansys.scadeone.core import ScadeOne

   with ScadeOne(install_dir="<Scade One installation dir>") as app:
      project = app.load_project("project.sproj")


.. note::
   The ``install_dir`` parameter can be a ``str`` or a ``Path`` value.
   It is necessary to set it if the project relies on Scade One standard libraries.


PyScadeOne uses the **ScadeOneException** exception when an error occurs from the API.
Errors, warnings, etc. are logged into the `'pyscadeone.log` file located in the 
folder where the script is launched.

Check out section :ref:`sec_modeler` for more details. 
