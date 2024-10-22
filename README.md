Install
=======

[![Python package](https://github.com/chdemko/pandoc-numbering/workflows/Python%20package/badge.svg?branch=develop)](https://github.com/chdemko/pandoc-numbering/actions/workflows/python-package.yml)
[![Hatch project](https://img.shields.io/badge/%F0%9F%A5%9A-Hatch-4051b5.svg)](https://github.com/pypa/hatch)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://pypi.org/project/black/)
[![Coveralls](https://img.shields.io/coveralls/github/chdemko/pandoc-numbering/develop.svg?logo=Codecov&logoColor=white)](https://coveralls.io/github/chdemko/pandoc-numbering?branch=develop)
[![Scrutinizer](https://img.shields.io/scrutinizer/g/chdemko/pandoc-numbering.svg?logo=scrutinizer)](https://scrutinizer-ci.com/g/chdemko/pandoc-numbering/)
[![Code Climate](https://codeclimate.com/github/chdemko/pandoc-numbering/badges/gpa.svg)](https://codeclimate.com/github/chdemko/pandoc-numbering/)
[![CodeFactor](https://img.shields.io/codefactor/grade/github/chdemko/pandoc-numbering/develop.svg?logo=codefactor)](https://www.codefactor.io/repository/github/chdemko/pandoc-numbering)
[![Codacy](https://img.shields.io/codacy/grade/36051716c52147bca7a7f4c1ca6bc998.svg?logo=codacy)](https://app.codacy.com/gh/chdemko/pandoc-numbering/dashboard)
[![PyPI version](https://img.shields.io/pypi/v/pandoc-numbering.svg?logo=pypi&logoColor=white)](https://pypi.org/project/pandoc-numbering/)
[![PyPI format](https://img.shields.io/pypi/format/pandoc-numbering.svg?logo=pypi&logoColor=white)](https://pypi.org/project/pandoc-numbering/)
[![License](https://img.shields.io/pypi/l/pandoc-numbering.svg?logo=pypi&logoColor=white)](https://raw.githubusercontent.com/chdemko/pandoc-numbering/develop/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/pandoc-numbering?logo=pypi&logoColor=white)](https://pepy.tech/project/pandoc-numbering)
[![Development Status](https://img.shields.io/pypi/status/pandoc-numbering.svg?logo=pypi&logoColor=white)](https://pypi.org/project/pandoc-numbering/)
[![Python version](https://img.shields.io/pypi/pyversions/pandoc-numbering.svg?logo=Python&logoColor=white)](https://pypi.org/project/pandoc-numbering/)
[![Pandoc version](https://img.shields.io/badge/pandoc-2.14%20|%202.15%20|%202.16%20|%202.17%20|%202.18%20|%202.19%20|%203.0%20|%203.1%20|%203.2%20|%203.3%20|%203.4%20|%203.5-blue.svg?logo=markdown)](https://pandoc.org/)
[![Latest release](https://img.shields.io/github/release-date/chdemko/pandoc-numbering.svg?logo=github)](https://github.com/chdemko/pandoc-numbering/releases)
[![Last commit](https://img.shields.io/github/last-commit/chdemko/pandoc-numbering/develop?logo=github)](https://github.com/chdemko/pandoc-numbering/commit/develop/)
[![Repo Size](https://img.shields.io/github/repo-size/chdemko/pandoc-numbering.svg?logo=github)](http://pandoc-numbering.readthedocs.io/en/latest/)
[![Code Size](https://img.shields.io/github/languages/code-size/chdemko/pandoc-numbering.svg?logo=github)](http://pandoc-numbering.readthedocs.io/en/latest/)
[![Source Rank](https://img.shields.io/librariesio/sourcerank/pypi/pandoc-numbering.svg?logo=libraries.io&logoColor=white)](https://libraries.io/pypi/pandoc-numbering)
[![Docs](https://img.shields.io/readthedocs/pandoc-numbering.svg?logo=read-the-docs&logoColor=white)](http://pandoc-numbering.readthedocs.io/en/latest/)

*pandoc-numbering* is a [pandoc] filter for numbering all kinds of things.

[pandoc]: http://pandoc.org/

Instructions
------------

*pandoc-numbering* requires [python], a programming language that comes
pre-installed on linux and Mac OS X, and which is easily installed
[on Windows].

Install *pandoc-numbering* using the bash command

~~~shell-session
$ pipx install pandoc-numbering
~~~

To upgrade to the most recent release, use

~~~shell-session
$ pipx upgrade pandoc-numbering
~~~

`pipx` is a script to install and run python applications in isolated environments from the Python Package Index, [PyPI]. It can be installed using instructions given [here](https://pipx.pypa.io/stable/).

Make sure you have the

* *tocloft*

LaTeX package. On linux you have to install some extra libraries **before**
*pandoc-numbering*. On a Debian-based system (including Ubuntu), you can
install it as root using

~~~shell-session
$ sudo apt-get install texlive-latex-extra
~~~

[python]: https://www.python.org/
[on Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi


Getting Help
------------

If you have any difficulties with *pandoc-numbering*, please feel welcome to
[file an issue] on github so that we can help.

[file an issue]: https://github.com/chdemko/pandoc-numbering/issues

Contribute
==========

Instructions
------------

Install `hatch`, then run

~~~shell-session
$ hatch run pip install pre-commit
$ hatch run pre-commit install
~~~

to install `pre-commit` before working on your changes.

Tests
-----

When your changes are ready, run

~~~shell-session
$ hatch test
$ hatch fmt --check
$ hatch run lint:check
$ hatch run docs:build
$ hatch build -t wheel
~~~

for running the tests, checking the style, building the documentation
and building the wheel.

