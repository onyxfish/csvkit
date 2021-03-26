===========
Power tools
===========

csvjoin: merging related data
=============================

One of the most common operations that we need to perform on data is "joining" it to other, related data. For instance, given a dataset about equipment supplied to counties in Nebraska, one might reasonably want to merge that with a dataset containing the population of each county. :doc:`/scripts/csvjoin` allows us to take those two datasets (equipment and population) and merge them, much like you might do with a SQL ``JOIN`` query. In order to demonstrate this, let's grab a second dataset:

.. code-block:: bash

    curl -L -O https://raw.githubusercontent.com/wireservice/csvkit/master/examples/realdata/acs2012_5yr_population.csv

Now let's see what's in there:

.. code-block:: bash

    csvstat acs2012_5yr_population.csv

.. code-block:: none

    1. fips
      Number
      Nulls: False
      Min: 31001
      Max: 31185
      Sum: 2891649
      Mean: 31093
      Median: 31093
      Standard Deviation: 53.98147830506311726900562525
      Unique values: 93
      5 most frequent values:
          31001:	1
          31003:	1
          31005:	1
          31007:	1
          31009:	1
    2. name
      Text
      Nulls: False
      Unique values: 93
      Max length: 23
      5 most frequent values:
          Adams County, NE:	1
          Antelope County, NE:	1
          Arthur County, NE:	1
          Banner County, NE:	1
          Blaine County, NE:	1
    3. total_population
      Number
      Nulls: False
      Min: 348
      Max: 518271
      Sum: 1827306
      Mean: 19648.45161290322580645161290
      Median: 6294
      Standard Deviation: 62501.00530730896711321285542
      Unique values: 93
      5 most frequent values:
          31299:	1
          6655:	1
          490:	1
          778:	1
          584:	1
    4. margin_of_error
      Number
      Nulls: False
      Min: 0
      Max: 115
      Sum: 1800
      Mean: 19.35483870967741935483870968
      Median: 0
      Standard Deviation: 37.89707031274211909117708454
      Unique values: 15
      5 most frequent values:
          0:	73
          73:	2
          114:	2
          97:	2
          99:	2

    Row count: 93

As you can see, this data file contains population estimates for each county in Nebraska from the 2012 5-year ACS estimates. This data was retrieved from `Census Reporter <https://censusreporter.org/>`_ and reformatted slightly for this example. Let's join it to our equipment data:

.. code-block:: bash

    csvjoin -c fips data.csv acs2012_5yr_population.csv > joined.csv

Since both files contain a fips column, we can use that to join the two. In our output you should see the population data appended at the end of each row of data. Let's combine this with what we've learned before to answer the question "What was the lowest population county to receive equipment?":

.. code-block:: bash

    csvcut -c county,item_name,total_population joined.csv | csvsort -c total_population | csvlook | head

.. code-block:: bash

    | county     | item_name                                                      | total_population |
    | ---------- | -------------------------------------------------------------- | ---------------- |
    | MCPHERSON  | RIFLE,5.56 MILLIMETER                                          |              348 |
    | WHEELER    | RIFLE,5.56 MILLIMETER                                          |              725 |
    | GREELEY    | RIFLE,7.62 MILLIMETER                                          |            2,515 |
    | GREELEY    | RIFLE,7.62 MILLIMETER                                          |            2,515 |
    | GREELEY    | RIFLE,7.62 MILLIMETER                                          |            2,515 |
    | NANCE      | RIFLE,5.56 MILLIMETER                                          |            3,730 |
    | NANCE      | RIFLE,7.62 MILLIMETER                                          |            3,730 |
    | NANCE      | RIFLE,7.62 MILLIMETER                                          |            3,730 |

Two counties with fewer than one-thousand residents were the recipients of 5.56 millimeter assault rifles. This simple example demonstrates the power of joining datasets. Although SQL will always be a more flexible option, :doc:`/scripts/csvjoin` will often get you where you need to go faster.

csvstack: combining subsets
===========================

Frequently large datasets are distributed in many small files. At some point you will probably want to merge those files for bulk analysis. :doc:`/scripts/csvstack` allows you to "stack" the rows from CSV files with the same columns (and identical column names). To demonstrate, let's imagine we've decided that Nebraska and Kansas form a "region" and that it would be useful to analyze them in a single dataset. Let's grab the Kansas data:

.. code-block:: bash

    curl -L -O https://raw.githubusercontent.com/wireservice/csvkit/master/examples/realdata/ks_1033_data.csv

Back in :doc:`1_getting_started`, we had used in2csv to convert our Nebraska data from XLSX to CSV. However, we named our output `data.csv` for simplicity at the time. Now that we are going to be stacking multiple states, we should re-convert our Nebraska data using a file naming convention matching our Kansas data:

.. code-block:: bash

    in2csv ne_1033_data.xlsx > ne_1033_data.csv

Now let's stack these two data files:

.. code-block:: bash

    csvstack ne_1033_data.csv ks_1033_data.csv > region.csv

Using csvstat we can see that our ``region.csv`` contains both datasets:

.. code-block:: bash

    csvstat -c state,acquisition_cost region.csv

.. code-block:: bash

    1. state
      Text
      Nulls: False
      Values: NE, KS
      Max length: 2
      5 most frequent values:
          KS:	1575
          NE:	1036
    8. acquisition_cost
      Number
      Nulls: False
      Min: 0.0
      Max: 658000
      Sum: 9440445.91
      Mean: 3615.643780160857908847184987
      Median: 138
      Standard Deviation: 23730.63142202547205726466358
      Unique values: 127
      5 most frequent values:
          120.0:	649
          499.0:	449
          138.0:	311
          6800.0:	304
          58.71:	218

    Row count: 2611

If you supply the :code:`-g` flag then :doc:`/scripts/csvstack` can also add a "grouping column" to each row, so that you can tell which file each row came from. In this case we don't need this, but you can imagine a situation in which instead of having a ``county`` column each of this datasets had simply been named ``nebraska.csv`` and ``kansas.csv``. In that case, using a grouping column would prevent us from losing information when we stacked them.

csvsql and sql2csv: ultimate power
==================================

Sometimes (almost always), the command-line isn't enough. It would be crazy to try to do all your analysis using command-line tools. Often times, the correct tool for data analysis is SQL. :doc:`/scripts/csvsql` and :doc:`/scripts/sql2csv` form a bridge that eases migrating your data into and out of a SQL database. For smaller datasets :doc:`/scripts/csvsql` can also leverage `sqlite <https://www.sqlite.org/>`_ to allow execution of ad hoc SQL queries without ever touching a database.

By default, :doc:`/scripts/csvsql` will generate a create table statement for your data. You can specify what sort of database you are using with the ``-i`` flag:

.. code-block:: bash

    csvsql -i sqlite joined.csv

.. code-block:: sql

    CREATE TABLE joined (
            state VARCHAR(2) NOT NULL,
            county VARCHAR(10) NOT NULL,
            fips DECIMAL NOT NULL,
            nsn VARCHAR(16) NOT NULL,
            item_name VARCHAR(62),
            quantity DECIMAL NOT NULL,
            ui VARCHAR(7) NOT NULL,
            acquisition_cost DECIMAL NOT NULL,
            total_cost DECIMAL NOT NULL,
            ship_date DATE NOT NULL,
            federal_supply_category DECIMAL NOT NULL,
            federal_supply_category_name VARCHAR(35) NOT NULL,
            federal_supply_class DECIMAL NOT NULL,
            federal_supply_class_name VARCHAR(63) NOT NULL,
            name VARCHAR(21) NOT NULL,
            total_population DECIMAL NOT NULL,
            margin_of_error DECIMAL NOT NULL
    );

Here we have the sqlite "create table" statement for our joined data. You'll see that, like :doc:`/scripts/csvstat`, :doc:`/scripts/csvsql` has done its best to infer the column types.

Often you won't care about storing the SQL statements locally. You can also use :doc:`/scripts/csvsql` to create the table directly in the database on your local machine. If you add the :code:`--insert` option the data will also be imported:

.. code-block:: bash

    csvsql --db sqlite:///leso.db --insert joined.csv

How can we check that our data was imported successfully? We could use the sqlite command-line interface, but rather than worry about the specifics of another tool, we can also use :doc:`/scripts/sql2csv`:

.. code-block:: bash

    sql2csv --db sqlite:///leso.db --query "select * from joined"

Note that the :code:`--query` parameter to :doc:`/scripts/sql2csv` accepts any SQL query. For example, to export Douglas county from the ``joined`` table from our sqlite database, we would run:

.. code-block:: bash

    sql2csv --db sqlite:///leso.db --query "select * from joined where county='DOUGLAS';" > douglas.csv

Sometimes, if you will only be running a single query, even constructing the database is a waste of time. For that case, you can actually skip the database entirely and :doc:`/scripts/csvsql` will create one in memory for you:

.. code-block:: bash

    csvsql --query "select county,item_name from joined where quantity > 5;" joined.csv | csvlook

SQL queries directly on CSVs! Keep in mind when using this that you are loading the entire dataset into an in-memory database, so it is likely to be very slow for large datasets.

Summing up
==========

:doc:`/scripts/csvjoin`, :doc:`/scripts/csvstack`, :doc:`/scripts/csvsql` and :doc:`/scripts/sql2csv` represent the power tools of csvkit. Using these tools can vastly simplify processes that would otherwise require moving data between other systems. But what about cases where these tools still don't cut it? What if you need to move your data onto the web or into a legacy database system? We've got a few solutions for those problems in our final section, :doc:`4_going_elsewhere`.
