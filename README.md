# pandoc-numbering
[![Build Status](https://img.shields.io/travis/chdemko/pandoc-numbering.svg)](http://travis-ci.org/chdemko/pandoc-numbering)
[![PyPI version](https://img.shields.io/pypi/v/pandoc-numbering.svg)](https://pypi.python.org/pypi/pandoc-numbering/)
[![License](https://img.shields.io/pypi/l/pandoc-numbering.svg)](http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html)
[![Downloads](https://img.shields.io/pypi/dm/pandoc-numbering.svg)](https://pypi.python.org/pypi/pandoc-numbering/)
[![Python version](https://img.shields.io/pypi/pyversions/pandoc-numbering.svg)](https://pypi.python.org/pypi/pandoc-numbering/)
[![Development Status](https://img.shields.io/pypi/status/pandoc-numbering.svg)](https://pypi.python.org/pypi/pandoc-numbering/)

*pandoc-numbering* is a [pandoc] filter for numbering all kinds of things.

Each paragraph ended by a `#` character will be numbered. The text preceding the `#` character is used a as key
to determine the number used as a replacement for the `#` character.

* if it's a new key, a new numbering is started with index 1;
* if it's an existing key, the last number is incremented.

You can add an identifier to the `#` character. It does not change the behavior explained above. It allows to be cross-referred
in links:

* `[](#identifier "title")` the empty text is replaced by the associated key concatenated with the associated number;
* `[text](#identifier "title")` the `#` character is replaced by the associated number in the text.

In both cases, the `#` character is replaced by the associated number in the title.

You can add a sequence of '#.' characters before the last '#' character. In this sequence, the '#' characters are replaced by the numbering of the current headers.

If you want to hide the numbering of the headers, you can replace the beginning of the '#.' sequence by a '_.' sequence.

Demonstration: Using [pandoc-numbering-sample.md] as input gives output files in [pdf], [tex], [html], [epub], [md] and
other formats.

~~~
$ cat pandoc-numbering-sample.md
% Sample use of automatic numbering
% Ch. Demko <chdemko@gmail.com>
% 04/11/2015

This is the first section
=========================

Exercise #

This is the first exercise. Have also a look at the [](#exercise:second).

> Theorem (Needed for the [second exercise](#exercise:second)) #.#theorem:first
> 
> This is a the first theorem.
> Look at the [exercise](#exercise:second "Go to the exercise #").

Exercise (This is the second exercise) #exercise:second

Use [_theorem #_](#theorem:first)

Example _.#

This is the first example of the first section

Example _.#

This is the second example of the first section


This is the second section
==========================

Example _.#

This is the first example of the second section

> Theorem #.#
> 
> Another theorem. Can be useful in [](#exercise:1)

> Theorem #.#
> 
> A last theorem.

Example _.#

This is the second example of the second section

Exercise #

This is the third exercise.

Unnumbered ##
~~~

Converting the `pandoc-numbering-sample.md` file will give:

~~~
---
author:
- 'Ch. Demko <chdemko@gmail.com>'
date: '04/11/2015'
title: Sample use of automatic numbering
---

This is the first section
=========================

<span id="exercise:1">**Exercise 1**</span>

This is the first exercise. Have also a look at the [Exercise
2](#exercise:second).

> <span id="theorem:first">**Theorem 1.1** *(Needed for the [second
> exercise](#exercise:second))*</span>
>
> This is a the first theorem. Look at the
> [exercise](#exercise:second "Go to the exercise 2").

<span id="exercise:second">**Exercise 2** *(This is the second
exercise)*</span>

Use [*theorem 1.1*](#theorem:first)

<span id="example:1.1">**Example 1**</span>

This is the first example of the first section

<span id="example:1.2">**Example 2**</span>

This is the second example of the first section

This is the second section
==========================

<span id="example:2.1">**Example 1**</span>

This is the first example of the second section

> <span id="theorem:2.1">**Theorem 2.1**</span>
>
> Another theorem. Can be useful in [Exercise 1](#exercise:1)

> <span id="theorem:2.2">**Theorem 2.2**</span>
>
> A last theorem.

<span id="example:2.2">**Example 2**</span>

This is the second example of the second section

<span id="exercise:3">**Exercise 3**</span>

This is the third exercise.

Unnumbered \#
~~~

This version of pandoc-numbering was tested using pandoc 1.15.1, pandoc 1.16 and pandoc 1.17 and is known to work under linux, Mac OS X and Windows.

[pandoc]: http://pandoc.org/
[pandoc-numbering-sample.md]: https://raw.githubusercontent.com/chdemko/pandoc-numbering/master/pandoc-numbering-sample.md

Usage
-----

To apply the filter, use the following option with pandoc:

    --filter pandoc-numbering

Installation
------------

pandoc-numbering requires [python], a programming language that comes pre-installed on linux and Mac OS X, and which is easily installed [on Windows].  Either python 2.7 or 3.x will do.

Install pandoc-numbering as root using the bash command

    pip install pandoc-numbering 

To upgrade to the most recent release, use

    pip install --upgrade pandoc-numbering 

`pip` is a script that downloads and installs modules from the Python Package Index, [PyPI].  It should come installed with your python distribution.  If you are running linux, `pip` may be bundled separately. On a Debian-based system (including Ubuntu), you can install it as root using

    apt-get update
    apt-get install python-pip

[python]: https://www.python.org/
[on Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi


Getting Help
------------

If you have any difficulties with pandoc-numbering, please feel welcome to [file an issue] on github so that we can help.

[file an issue]: https://github.com/chdemko/pandoc-numbering/issues
