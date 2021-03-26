======
csvsql
======

Description
===========

Generate SQL statements for a CSV file or execute those statements directly on a database. In the latter case supports both creating tables and inserting data::

    usage: csvsql [-h] [-d DELIMITER] [-t] [-q QUOTECHAR] [-u {0,1,2,3}] [-b]
                  [-p ESCAPECHAR] [-z FIELD_SIZE_LIMIT] [-e ENCODING] [-L LOCALE]
                  [-S] [--blanks] [--date-format DATE_FORMAT]
                  [--datetime-format DATETIME_FORMAT] [-H] [-K SKIP_LINES] [-v]
                  [-l] [--zero] [-V]
                  [-i {firebird,mssql,mysql,oracle,postgresql,sqlite,sybase,crate}]
                  [--db CONNECTION_STRING] [--query QUERY] [--insert]
                  [--prefix PREFIX] [--tables TABLE_NAMES] [--no-constraints]
                  [--unique-constraint UNIQUE_CONSTRAINT] [--no-create]
                  [--create-if-not-exists] [--overwrite] [--db-schema DB_SCHEMA]
                  [-y SNIFF_LIMIT] [-I] [--chunk-size NUM]
                  [FILE [FILE ...]]

    Generate SQL statements for one or more CSV files, or execute those statements
    directly on a database, and execute one or more SQL queries.

    positional arguments:
      FILE                  The CSV file(s) to operate on. If omitted, will accept
                            input as piped data via STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      -i {firebird,mssql,mysql,oracle,postgresql,sqlite,sybase,crate}, --dialect {firebird,mssql,mysql,oracle,postgresql,sqlite,sybase,crate}
                            Dialect of SQL to generate. Only valid when --db is
                            not specified.
      --db CONNECTION_STRING
                            If present, a sqlalchemy connection string to use to
                            directly execute generated SQL on a database.
      --query QUERY         Execute one or more SQL queries delimited by ";" and
                            output the result of the last query as CSV. QUERY may
                            be a filename.
      --insert              In addition to creating the table, also insert the
                            data into the table. Only valid when --db is
                            specified.
      --prefix PREFIX       Add an expression following the INSERT keyword, like
                            OR IGNORE or OR REPLACE.
      --tables TABLE_NAMES  A comma-separated list of names of tables to be
                            created. By default, the tables will be named after
                            the filenames without extensions or "stdin".
      --no-constraints      Generate a schema without length limits or null
                            checks. Useful when sampling big tables.
      --unique-constraint UNIQUE_CONSTRAINT
                            A column-separated list of names of columns to include
                            in a UNIQUE constraint.
      --no-create           Skip creating a table. Only valid when --insert is
                            specified.
      --create-if-not-exists
                            Create table if it does not exist, otherwise keep
                            going. Only valid when --insert is specified.
      --overwrite           Drop the table before creating. Only valid when
                            --insert is specified and --no-create is not
                            specified.
      --db-schema DB_SCHEMA
                            Optional name of database schema to create table(s)
                            in.
      -y SNIFF_LIMIT, --snifflimit SNIFF_LIMIT
                            Limit CSV dialect sniffing to the specified number of
                            bytes. Specify "0" to disable sniffing entirely.
      -I, --no-inference    Disable type inference when parsing the input.
      --chunk-size NUM
                            Chunk size for batch insert into the table.
                            Only valid when --insert is specified.

See also: :doc:`../common_arguments`.

For information on connection strings and supported dialects refer to the `SQLAlchemy documentation <https://www.sqlalchemy.org/docs/dialects/>`_.

If you prefer not to enter your password in the connection string, store the password securely in a `PostgreSQL Password File <https://www.postgresql.org/docs/9.1/static/libpq-pgpass.html>`_, a `MySQL Options File <https://dev.mysql.com/doc/refman/5.7/en/option-files.html>`_ or similar files for other systems.

.. note::

    Using the :code:`--query` option may cause rounding (in Python 2) or introduce `Python floating point issues <https://docs.python.org/3.4/tutorial/floatingpoint.html>`_ (in Python 3).

.. note::

    Alternatives to :doc:`csvsql` are `q <https://github.com/harelba/q>`_ and `textql <https://github.com/dinedal/textql>`_.

Examples
========

Generate a statement in the PostgreSQL dialect::

    csvsql -i postgresql examples/realdata/FY09_EDU_Recipients_by_State.csv

Create a table and import data from the CSV directly into PostgreSQL::

    createdb test
    csvsql --db postgresql:///test --tables fy09 --insert examples/realdata/FY09_EDU_Recipients_by_State.csv

For large tables it may not be practical to process the entire table. One solution to this is to analyze a sample of the table. In this case it can be useful to turn off length limits and null checks with the :code:`--no-constraints` option::

    head -n 20 examples/realdata/FY09_EDU_Recipients_by_State.csv | csvsql --no-constraints --tables fy09

Create tables for an entire folder of CSVs and import data from those files directly into PostgreSQL::

    createdb test
    csvsql --db postgresql:///test --insert examples/*_converted.csv

If those CSVs have identical headers, you can import them into the same table by using :doc:`csvstack` first::

    createdb test
    csvstack examples/dummy?.csv | csvsql --db postgresql:///test --insert

Group rows by one column::

    csvsql --query "select * from 'dummy3' group by a" examples/dummy3.csv

You can also use CSVSQL to "directly" query one or more CSV files. Please note that this will create an in-memory SQL database, so it won't be very fast::

    csvsql --query  "select m.usda_id, avg(i.sepal_length) as mean_sepal_length from iris as i join irismeta as m on (i.species = m.species) group by m.species" examples/iris.csv examples/irismeta.csv

Concatenate two columns::

    csvsql --query "select a || b from 'dummy3'" examples/dummy3.csv

If a column contains null values, you must ``COALESCE`` the column::

    csvsql --query "select a || COALESCE(b, '') from 'sort_ints_nulls'" --no-inference examples/sort_ints_nulls.csv
