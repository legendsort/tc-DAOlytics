
# Table of Contents

1.  [Running the program](#org9a21006)
    1.  [Installing the python package](#orgec082de)
    2.  [TODO Creating the analyzer object:](#orgef4b7b7)
    3.  [TODO Setting the run frequency](#org1b4bc27)
2.  [Running without the package](#org254080e)

This package compiles the scripts into an object, which can run continuously.
The package scrapes data from the database, processes is and pushes the result
into the database.

**Why python package?**
In future this will make it easier to integrate into services runable on the server.


<a id="org9a21006"></a>

# Running the program


<a id="orgec082de"></a>

## Installing the python package

Inside of the analyzer directory:

To install:

    make install

To load (development):

    make load

To unload:

    make unload

To reinstall when developing:

    make reload


<a id="orgef4b7b7"></a>

## TODO Creating the analyzer object:

    from rndaoanalyzer import RnDaoAnalyzer
    a = Analyzer()
    a.set_database_info(db_info)
    a.run_once()


<a id="org1b4bc27"></a>

## TODO Setting the run frequency

How often should the analyzer be ran.

    a.set_analyzer_frequency()
    a.run_forever()

*This can also be done with a crontab.*


<a id="org254080e"></a>

# Running without the package

Install the packages from the requirements.txt (in rndao<sub>analyzer</sub>)

Create the environment variables

    RNDAO_DB_USER=user
    RNDAO_DB_PASSWORD=password
    RNDAO_DB_HOST=host:port

The expected mongo url string is in the following format:

    f"mongodb://{self.db_user}:{self.db_password}@{self.db_host}"

where python script replaces the variables with actual values

