========================
Tips and Troubleshooting
========================

Tips
====

Reading compressed CSVs
-----------------------

csvkit has builtin support for reading ``gzip`` or ``bz2`` compressed input files. This is automatically detected based on the file extension. For example::

    csvstat examples/dummy.csv.gz
    csvstat examples/dummy.csv.bz2

Please note, the files are decompressed in memory, so this is a convenience, not an optimization.

Specifying STDIN as a file
--------------------------

Most tools use ``STDIN`` as input if no filename is given, but tools that accept multiple inputs like :doc:`/scripts/csvjoin` and :doc:`/scripts/csvstack` don't. To use ``STDIN`` as an input to these tools, use ``-`` as the filename. For example, these three commands produce the same output::

    csvstat examples/dummy.csv
    cat examples/dummy.csv | csvstat
    cat examples/dummy.csv | csvstat -

:doc:`/scripts/csvstack` can take a filename and ``STDIN`` as input, for example::

    cat examples/dummy.csv | csvstack examples/dummy3.csv -

Alternately, you can pipe in multiple inputs like so::

    csvjoin -c id <(csvcut -c 2,5,6 a.csv) <(csvcut -c 1,7 b.csv)

Troubleshooting
===============

Installation
------------

csvkit is supported on non-end-of-life versions of Python.

It is tested on macOS, and has also been used on Linux and Windows.

If installing on macOS, you may need to install Homebrew first::

    /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    brew install python
    pip install csvkit

If installing on Ubuntu, you may need to install Python's development headers first::

    sudo apt-get install python-dev python-pip python-setuptools build-essential
    pip install csvkit

If the installation is successful but csvkit's tools fail, you may need to update Python's setuptools package first::

    pip install --upgrade setuptools
    pip install --upgrade csvkit

On macOS, if you see ``OSError: [Errno 1] Operation not permitted``, try::

    sudo pip install --ignore-installed csvkit

If you use Python 2 and have a recent version of pip, you may need to run pip with :code:`--allow-external argparse`.

If you use Python 2 on FreeBSD, you may need to install `py-sqlite3 <https://www.freshports.org/databases/py-sqlite3/>`_.

.. note ::

    Need more speed? If you use Python 2, :code:`pip install cdecimal` for a boost.

CSV formatting and parsing
--------------------------

* Are values appearing in incorrect columns?
* Does the output combine multiple fields into a single column with double-quotes?
* Does the outplit split a single field into multiple columns?
* Are :code:`csvstat -c 1` and :code:`csvstat --count` reporting inconsistent row counts?
* Do you see ``Row # has # values, but Table only has # columns.``?

These may be symptoms of CSV sniffing gone wrong. As there is no single, standard CSV format, csvkit uses Python's `csv.Sniffer <https://docs.python.org/3.5/library/csv.html#csv.Sniffer>`_ to deduce the format of a CSV file: that is, the field delimiter and quote character. By default, the entire file is sent for sniffing, which can be slow. You can send a small sample with the :code:`--snifflimit` option. If you're encountering any cases above, you can try setting :code:`--snifflimit 0` to disable sniffing and set the :code:`--delimiter` and :code:`--quotechar` options yourself.

Although these issues are annoying, in most cases, CSV sniffing Just Works™. Disabling sniffing by default would produce a lot more issues than enabling it by default.

CSV data interpretation
-----------------------

* Are the numbers ``1`` and ``0`` being interepted as ``True`` and ``False``?
* Are phone numbers changing to integers and losing their leading ``+`` or ``0``?
* Is the Italian comune of "None" being treated as a null value?

These may be symptoms of csvkit's type inference being too aggressive for your data. CSV is a text format, but it may contain text representing numbers, dates, booleans or other types. csvkit attempts to reverse engineer that text into proper data types—a process called "type inference".

For some data, type inference can be error prone. If necessary you can disable it with the :code:`--no-inference` switch. This will force all columns to be treated as regular text.

Slow performance
----------------

csvkit's tools fall into two categories: Those that load an entire CSV into memory (e.g. :doc:`/scripts/csvstat`) and those that only read data one row at a time (e.g. :doc:`/scripts/csvcut`). Those that stream results will generally be very fast. See :doc:`contributing` for a full list. For those that buffer the entire file, the slowest part of that process is typically the "type inference" described in the previous section.

If a tool is too slow to be practical for your data try setting the :code:`--snifflimit` option or using the :code:`--no-inference`.

Database errors
---------------

Are you seeing this error message, even after running :code:`pip install psycopg2`, :code:`pip install mysql-connector-python` or :code:`pip install mysqlclient`?

::

    You don't appear to have the necessary database backend installed for connection string you're trying to use. Available backends include:

    PostgreSQL: pip install psycopg2
    MySQL:      pip install mysql-connector-python OR pip install mysqlclient

    For details on connection strings and other backends, please see the SQLAlchemy documentation on dialects at:

    https://www.sqlalchemy.org/docs/dialects/

First, make sure that you can open a ``python`` interpreter and run :code:`import psycopg2`. If you see an error containing ``mach-o, but wrong architecture``, you may need to reinstall ``psycopg2`` with :code:`export ARCHFLAGS="-arch i386" pip install --upgrade psycopg2` (`source <https://www.destructuring.net/2013/07/31/trouble-installing-psycopg2-on-osx/>`_). If you see another error, you may be able to find a solution on StackOverflow.

Python standard output encoding errors
--------------------------------------

If, when running a command like :code:`csvlook dummy.csv | less` you get an error like::

    'ascii' codec can't encode character u'\u0105' in position 2: ordinal not in range(128)

The simplest option is to set the encoding that Python uses for standard streams, using the :code:`PYTHONIOENCODING` environment variable::

    PYTHONIOENCODING=utf8 csvlook dummy.csv | less
