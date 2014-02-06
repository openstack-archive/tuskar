======================
Debugging with iPython
======================

Requirements
------------

::

    $ yum install python-ipython
    $ cd tuskar
    $ find . | grep no-global-site-packages.txt | xargs rm

The 'find' will allow you to import 'global' packages in Tox.

Debugging
---------

Place these two lines in the place you want to debug/drop to shell:

::

    import IPython
    IPython.embed()

Then start Tuskar as usual and do a GET/POST/etc. Once the code
execution hits these two lines, you will be dropped into the iPython shell
and you will have access to all local variables and the env defined in the
context of where you placed that two lines.

Tweaks
------

`ipythonrc <https://github.com/queezythegreat/settings/tree/master/ipython>`_
-> Colors on console, tab completion for methods and more ;-)
