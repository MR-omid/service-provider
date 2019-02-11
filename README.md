REQUIREMENTS
===========

#### `ubuntu 16.04 LTS`


INSTALLATION
============

***NOTICE:*** *open terminal at /F.SystemAPI.01 dir and use it for running below commands*


Python Requirements
-------------------
```
$ sudo -H ./install.sh
```

CONFIGURATION
=============

Update configs
-------------
*update database address, username, password, app version*
```
$ nano core/constants.py
```

Update Database
---------------
```
$  python3 console/debug/update_version.py
```
*for prepare and create database tables and inserting default value to database*

***NOTICE:***   
*this command update database version up to app version.  
you can set app version in core/constants.py,  
also this command truncate your database if app version is 1.0 and debug_mode value is true (that exist in components/mode).
if you do not prepare your database before, version of your database set as 0.0*


RUNNING
=======
running SystemAPI in debug mode by following command:
```
$ sudo nohup python3 console/debug/manager.py -a start &
```

running SystemAPI in release mode by following command:
```
$ sudo nohup python3 console/release/manager.py -a start &
```


stop SystemAPI from running (replace {mode} by debug or release:
```
$ sudo python3 console/{mode}/manager.py -a stop
```

get status of SystemAPI processes:
```
$ sudo python3 console/{mode}/manager.py -a status
```