======================
Contributing to csvkit
======================

csvkit actively encourages contributions from people of all genders, races, ethnicities, ages, creeds, nationalities, persuasions, alignments, sizes, shapes, and journalistic affiliations. You are welcome here.

We seek contributions from developers and non-developers of all skill levels. We will typically accept bug fixes and documentation updates with minimal fuss. If you want to work on a larger feature—great! The maintainers will be happy to provide feedback and code review on your implementation.

Before making any changes or additions to csvkit, please be sure to read the rest of this document, especially the "Principles of development" section.

Getting Started
===============

Set up your environment for development::

    git clone git://github.com/wireservice/csvkit.git
    cd csvkit
    mkvirtualenv csvkit

    # If running Python 2:
    pip install -r requirements-py2.txt

    # If running Python 3:
    pip install -r requirements-py3.txt

    python setup.py develop
    tox

Principles of development
=========================

csvkit is to tables as Unix text processing commands (cut, grep, cat, sort) are to text. As such, csvkit adheres to `the Unix philosophy <https://en.wikipedia.org/wiki/Unix_philosophy>`_.

#. Small is beautiful.
#. Make each program do one thing well.
#. Build a prototype as soon as possible.
#. Choose portability over efficiency.
#. Store data in flat text files.
#. Use software leverage to your advantage.
#. Use shell scripts to increase leverage and portability.
#. Avoid captive user interfaces.
#. Make every program a filter.

As there is no single, standard CSV format, csvkit encourages popular formatting options:

* Output targets broad compatibility: Quoting is done with double-quotes and only when required. Fields are delimited with commas. Rows are terminated with Unix line endings ("\\n").

* Output favors consistency over brevity: Numbers always include at least one decimal place, even if they are round. Dates and times are output in ISO 8601 format. Null values are rendered as empty strings.

How to contribute
=================

#. Fork the project on `GitHub <https://github.com/wireservice/csvkit>`_.
#. Look through the `open issues <https://github.com/wireservice/csvkit/issues>`_ for a task that you can realistically expect to complete in a few days. Don't worry about the issue's priority; instead, choose something you'll enjoy. You're more likely to finish something if you enjoy hacking on it.
#. Comment on the issue to let people know you're going to work on it so that no one duplicates your effort. It's good practice to provide a general idea of how you plan to resolve the issue so that others can make suggestions.
#. Write tests for any changes to the code's behavior. Follow the format of the tests in the ``tests/`` directory to see how this works. You can run all the tests with the command ``tox``, or just your Python version's with ``nosetests`` (faster).
#. Write the code. Try to be consistent with the style and organization of the existing code. A good contribution won't be refused for stylistic reasons, but large parts of it may be rewritten and nobody wants that.
#. As you're working, periodically merge in changes from the upstream master branch to avoid having to resolve large merge conflicts. Check that you haven't broken anything by running the tests.
#. Write documentation for any user-facing features.
#. Once it works, is tested, and is documented, submit a pull request on GitHub.
#. Wait for it to be merged or for a comment about what needs to be changed.
#. Rejoice.

A note on new tools
===================

As a general rule, csvkit is no longer adding new tools. This is the result of limited maintenance time as well as a desire to keep the toolkit focused on the most common use cases. Exceptions may be made to this rule on a case-by-case basis. We, of course, welcome patches to improve existing tools or add useful features.

If you decide to build your own tool, we encourage you to create and maintain it as a separate Python package. You will probably want to use the `agate <https://agate.readthedocs.io/>`_ library, which csvkit uses for most of its CSV reading and writing. Doing so will safe time and make it easier to maintain common behavior with csvkit’s core tools.

Streaming versus buffering
==========================

csvkit tools operate in one of two fashions: Some, such as :doc:`/scripts/csvsort`, buffer their entire input into memory before writing any output. Other tools—those that can operate on individual records—write write a row immediately after reading a row. Records are "streamed" through the tool. Streaming tools produce output faster and require less memory than buffering tools.

For performance reasons tools should always offer streaming when possible. If a new feature would undermine streaming functionality it must be balanced against the utility of having a tool that can efficiently operate over large datasets.

Currently, the following tools stream:

* :doc:`/scripts/csvclean`
* :doc:`/scripts/csvcut`
* :doc:`/scripts/csvformat`
* :doc:`/scripts/csvgrep`
* :doc:`/scripts/csvstack`
* :doc:`/scripts/sql2csv`

Currently, the following tools buffer:

* :doc:`/scripts/csvjoin`
* :doc:`/scripts/csvjson` unless :code:`--stream --no-inference --snifflimit 0` is set and :code:`--skip-lines` isn't set
* :doc:`/scripts/csvlook`
* :doc:`/scripts/csvpy`
* :doc:`/scripts/csvsort`
* :doc:`/scripts/csvsql`
* :doc:`/scripts/csvstat`
* :doc:`/scripts/in2csv` unless :code:`--format ndjson --no-inference` is set, or unless :code:`--format csv --no-inference --snifflimit 0` is set and :code:`--no-header-row` and :code:`--skip-lines` aren't set

Legalese
========

To the extent that contributors care, they should keep the following legal mumbo-jumbo in mind:

The source of csvkit and therefore of any contributions are licensed under the permissive `MIT license <https://www.opensource.org/licenses/mit-license.php>`_. By submitting a patch or pull request you are agreeing to release your contribution under this license. You will be acknowledged in the AUTHORS file. As the owner of your specific contributions you retain the right to privately relicense your specific contributions (and no others), however, the released version of the code can never be retracted or relicensed.
