
# Table of Contents

1.  [Running the program](#orgea1e55a)
    1.  [Installing the python package](#orgb2133ca)
    2.  [TODO Creating the analyzer object:](#org623742e)
    3.  [TODO Setting the run frequency](#orga8a899f)

This package compiles the scripts into an object, which can run continuously.
The package scrapes data from the database, processes is and pushes the result
into the database.

**Why python package?**
In future this will make it easier to integrate into services runable on the server.


<a id="orgea1e55a"></a>

# Running the program


<a id="orgb2133ca"></a>

## Installing the python package

Inside of the analyzer directory:

    make load

To uninstall:

    make unload

To reinstall when developing:

    make reload


<a id="org623742e"></a>

## TODO Creating the analyzer object:

    from rndaoanalyzer import analyzer
    a = Analyzer()
    a.set_database(db_info)
    a.run_once()


<a id="orga8a899f"></a>

## TODO Setting the run frequency

How often should the analyzer be ran.

    a.set_analyzer_frequency()
    a.run_forever()

*This can also be done with a crontab.*

