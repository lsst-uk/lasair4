The Lasair "parallel" system is to execute multiple tasks on multiple workers, controlled by a head node that can connect to each worker through SSH. It is built with the  "parallel-SSH" library at https://pypi.org/project/parallel-ssh/

Each task is defined by a command line, and each worker by an IP-address, with the assumption that the SSH doesn't require a password. When a worker has finished a task, it is given another, until there are no more tasks left.

Note that there is a approx 60 second delay after the task is finished, before the head node's "finished" function reports true, and a subsequent task sent to that host. So this system works efficiently with large (multi-minute) tasks.

There are two applications of the system so far:
* "busy" is a prototype: it just runs a busy process on the worker
* "rebuild_objects" computes new features for objects in the Lasair database. The light curve is fetched from Cassandra for each one, and the same code used as in the real-time pipeline. To get the same results, only the latest 30 days of the light curve are used. CSV files are created, which can be ingested into the database using the program "csv_to_database".
