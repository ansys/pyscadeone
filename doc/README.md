
# Doc generation
On Windows, use:

    > ./make.bat html 

to produce the doc.

    $ make html

also works, but there are no error displayed on Windows.


Use the `clean` target from time to time to ensure correct rebuild of the documentation

# Check
use:

    $ python check_classes.py

in `doc` folder to check if all classes are consistent: `.py` vs `.rst`. This is done by looking at `.. autoclass` and `class SomeClass` text. Some modules are documented using `..automodule` and are discarded (see
`check_class.py` code).
