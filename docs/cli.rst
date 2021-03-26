=========
Reference
=========

csvkit is composed of command-line tools that can be divided into three major categories: Input, Processing, and Output. Documentation and examples for each tool are described on the following pages.

Input
=====

.. toctree::
    :maxdepth: 1

    scripts/in2csv
    scripts/sql2csv

Processing
==========

.. toctree::
    :maxdepth: 1

    scripts/csvclean
    scripts/csvcut
    scripts/csvgrep
    scripts/csvjoin
    scripts/csvsort
    scripts/csvstack

To change field values (i.e. to run ``sed`` or ``awk``-like commands on CSV files), consider `miller <https://github.com/johnkerl/miller>`_ (``mlr put``).

To transpose CSVs, consider `csvtool <https://colin.maudry.com/csvtool-manual-page/>`_. Install ``csvtool`` on Linux using your package manager, or on macOS using::

    brew install ocaml
    opam install csv
    ln -s ~/.opam/system/bin/csvtool /usr/local/bin/
    csvtool --help

Output and Analysis
===================

.. toctree::
    :maxdepth: 1

    scripts/csvformat
    scripts/csvjson
    scripts/csvlook
    scripts/csvpy
    scripts/csvsql
    scripts/csvstat

* To draw plots, consider `jp <https://github.com/sgreben/jp>`_.
* To diff CSVs, consider `daff <https://github.com/paulfitz/daff>`_.
* To explore CSVs interactively, consider `VisiData <https://visidata.org>`_.

Alternatives to :doc:`csvsql` are `q <https://github.com/harelba/q>`_ and `textql <https://github.com/dinedal/textql>`_.

Common arguments
================

.. toctree::
    :maxdepth: 2

    common_arguments
