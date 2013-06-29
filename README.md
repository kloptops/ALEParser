ALEParser
=========

A simple python ALE (AvidLogExchange) parser.


About
-----
Originally written in early 2012 for a friend, I recently updated it to
be a class and to include line tracking with some better error handling.

TODO
----

- [x] turn it into a class.
- [x] allow it to accept strings, filenames and or file handles.
- [x] line tracking for better error messages.
- [ ] make it available on pypi, setup.py compatible.
- [ ] more documentation.
- [ ] better strict mode.
- [ ] better checking of valid arguments.
- [x] better testing framework.

Tests
-----

Run tests with nose and coverage:
nosetests --with-coverage --cover-html --cover-package=aleparser --cover-min-percentage=90

License
-------

ALEParser is licensed under the [unlicense](http://unlicense.org/) "license",
feel free to do whatever you wish with it.
