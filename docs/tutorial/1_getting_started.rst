===============
Getting started
===============

About this tutorial
===================

There is no better way to learn how to use a new tool than to see it applied in a real world situation. To that end, this tutorial explains how to use csvkit tools by analyzing a real dataset.

The data we will be using is a subset of the United States Defense Logistic Agency Law Enforcement Support Office's (LESO) 1033 Program dataset, which describes how surplus military arms have been distributed to local police forces. This data was widely cited in the aftermath of the Ferguson, Missouri protests. The particular data we are using comes from an `NPR report <https://www.npr.org/2014/09/02/342494225/mraps-and-bayonets-what-we-know-about-the-pentagons-1033-program>`_ analyzing the data.

This tutorial assumes you have some basic familiarity with the command line. If you don't have much experience, fear not! This has been written with beginners in mind. No prior experience with data processing or analysis is assumed.

Installing csvkit
=================

Installing csvkit is easy:

.. code-block:: bash

    sudo pip install csvkit

If you have problems installing, look for help  in the :doc:`../tricks` section of the documentation.

.. note::

    If you're familiar with `virtualenv <https://virtualenv.readthedocs.org/en/latest/>`_, it is better to install csvkit in its own environment. If you are doing this, then you should leave off the ``sudo`` in the previous command.

Getting the data
================

Let's start by creating a clean workspace:

.. code-block:: bash

    mkdir csvkit_tutorial
    cd csvkit_tutorial

Now let's fetch the data:

.. code-block:: bash

    curl -L -O https://raw.githubusercontent.com/wireservice/csvkit/master/examples/realdata/ne_1033_data.xlsx

in2csv: the Excel killer
========================

For purposes of this tutorial, I've converted this data to Excel format. (NPR published it in CSV format.) If you have Excel you can open the file and take a look at it, but really, who wants to wait for Excel to load? Instead, let's convert it to a CSV:

.. code-block:: bash

    in2csv ne_1033_data.xlsx

You should see a CSV version of the data dumped into your terminal. All csvkit tools write to the terminal output, called "standard out", by default. This isn't very useful, so let's write it to a file instead:

.. code-block:: bash

    in2csv ne_1033_data.xlsx > data.csv

``data.csv`` will now contain a CSV version of our original file. If you aren't familiar with the ``>`` syntax, it means "redirect standard out to a file". If that's hard to remember it may be more convenient to think of it as "save to".

We can verify the that the data is saved to the new file by using the ``cat`` command to print it:

.. code-block:: bash

    cat data.csv

:doc:`/scripts/in2csv` can convert a variety of common file formats to CSV, including both ``.xls`` and ``.xlsx`` Excel files, JSON files, and fixed-width formatted files.

csvlook: data periscope
=======================

Now that we have some data, we probably want to get some idea of what's in it. We could open it in Excel or Google Docs, but wouldn't it be nice if we could just take a look in the command line? To do that, we can use :doc:`/scripts/csvlook`:

.. code-block:: bash

    csvlook data.csv

At first the output of :doc:`/scripts/csvlook` isn't going to appear very promising. You'll see a mess of data, pipe character and dashes. That's because this dataset has many columns and they won't all fit in the terminal at once. You have two options:

1. Pipe the output to ``less -S`` to display the lines without wrapping and use the arrow keys to scroll left and right:

.. code-block:: bash

    csvlook data.csv | less -S

2. Reduce which columns of our dataset are displayed before we look at it. This is what will do in the next section.

csvcut: data scalpel
====================

:doc:`/scripts/csvcut` is the original csvkit tool. It inspired the rest. With it, we can select, delete and reorder the columns in our CSV. First, let's just see what columns are in our data:

.. code-block:: bash

    csvcut -n data.csv

.. code-block:: bash

      1: state
      2: county
      3: fips
      4: nsn
      5: item_name
      6: quantity
      7: ui
      8: acquisition_cost
      9: total_cost
     10: ship_date
     11: federal_supply_category
     12: federal_supply_category_name
     13: federal_supply_class
     14: federal_supply_class_name

As you can see, our dataset has fourteen columns. Let's take a look at just columns ``2``, ``5`` and ``6``:

.. code-block:: bash

    csvcut -c 2,5,6 data.csv

Now we've reduced our output CSV to only three columns.

We can also refer to columns by their names to make our lives easier:

.. code-block:: bash

    csvcut -c county,item_name,quantity data.csv

Putting it together with pipes
==============================

Now that we understand :doc:`/scripts/in2csv`, :doc:`/scripts/csvlook` and :doc:`/scripts/csvcut` we can demonstrate the power of csvkit's when combined with the standard command-line "pipe". Try this command:

.. code-block:: bash

    csvcut -c county,item_name,quantity data.csv | csvlook | head

In addition to specifying filenames, all csvkit tools accept an input file via "standard in". This means that, using the ``|`` ("pipe") character we can use the output of one csvkit tool as the input of the next.

In the example above, the output of :doc:`/scripts/csvcut` becomes the input to :doc:`/scripts/csvlook`. This also allow us to pipe output to standard Unix commands such as ``head``, which prints only the first ten lines of its input. Here, the output of :doc:`/scripts/csvlook` becomes the input of ``head``.

Piping is a core feature of csvkit. Of course, you can always write the output of each command to a file using ``>``. However, it's often faster and more convenient to use pipes to chain several commands together.

We can also pipe :doc:`/scripts/in2csv`, allowing us to combine all our previous operations into one:

.. code-block:: bash

    in2csv ne_1033_data.xlsx | csvcut -c county,item_name,quantity | csvlook | head

Summing up
==========

All the csvkit tools work with standard input and output. Any tool can be piped into another and into another. The output of any tool can be redirected to a file. In this way they form a data processing "pipeline" of sorts, allowing you to do non-trivial, repeatable work without creating dozens of intermediary files.

Make sense? If you think you've got it figured out, you can move on to :doc:`2_examining_the_data`.
