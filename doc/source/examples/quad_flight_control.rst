.. _QuadFlightControl python setup: 

===============================
QuadFlightControl Example Setup
===============================

We use the **QuadFlightControl** example provided with Scade One. 
This example is located in the ``examples/QuadFlightControl``
folder of the Scade One installation directory. 

As the setup is almost the same for each example using the *QuadFlightControl*,
we present here the proper setting for other scripts.

Note that the ``ScadeOne`` instance is created with the ``install_dir`` parameter
set. 

.. code:: python

    from pathlib import Path
    from typing import cast

    from ansys.scadeone.core import ScadeOne
    import ansys.scadeone.core.swan as swan

    # Update according to your installation
    s_one_install = Path(r"C:\Scade One")

    quad_flight_project = (
        s_one_install / "examples/QuadFlightControl/QuadFlightControl" / "QuadFlightControl.sproj"
    )

    app = ScadeOne(install_dir=s_one_install)
    model = app.load_project(quad_flight_project).model

.. note::
    The import of the ``cast`` operation is sometimes used to indicate
    the type of an object to Python linters. This operation has no overhead
    and is not used in all scripts.