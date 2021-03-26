=======
sql2csv
=======

Description
===========

Executes arbitrary commands against a SQL database and outputs the results as a CSV::

    usage: sql2csv [-h] [-v] [-l] [-V] [--db CONNECTION_STRING] [--query QUERY]
                   [-e ENCODING] [-H]
                   [FILE]

    Execute an SQL query on a database and output the result to a CSV file.

    positional arguments:
      FILE                  The file to use as SQL query. If both FILE and QUERY
                            are omitted, query will be read from STDIN.

    optional arguments:
      -h, --help            show this help message and exit
      --db CONNECTION_STRING
                            An sqlalchemy connection string to connect to a
                            database.
      --query QUERY         The SQL query to execute. If specified, it overrides
                            FILE and STDIN.
      -e ENCODING, --encoding ENCODING
                            Specify the encoding of the input query file.
      -H, --no-header-row   Do not output column names.

Examples
========

Load sample data into a table using :doc:`csvsql` and then query it using `sql2csv`::

    csvsql --db "sqlite:///dummy.db" --tables "test" --insert examples/dummy.csv
    sql2csv --db "sqlite:///dummy.db" --query "select * from test"

Load data about financial aid recipients into PostgreSQL. Then find the three states that received the most, while also filtering out empty rows::

    createdb recipients
    csvsql --db "postgresql:///recipients" --tables "fy09" --insert examples/realdata/FY09_EDU_Recipients_by_State.csv
    sql2csv --db "postgresql:///recipients" --query "select * from fy09 where \"State Name\" != '' order by fy09.\"TOTAL\" limit 3"

You can even use it as a simple SQL calculator (in this example an in-memory SQLite database is used as the default)::

    sql2csv --query "select 300 * 47 % 14 * 27 + 7000"

The connection string `accepts parameters <https://docs.sqlalchemy.org/en/rel_1_0/core/engines.html#engine-creation-api>`_. For example, to set the encoding of a MySQL database::

    sql2csv --db 'mysql://user:pass@host/database?charset=utf8' --query "SELECT myfield FROM mytable"
