# To start the application server: #

`docker-compose run --service-ports web`

## To start the application shell: ##

`docker exec -it scsr-api_web_run_`**XXX**` python3 scsr_api/manage.py shell`

* where **XXX** is the number of the docker process. It can be retrieved with: docker ps

This will be the shell to use to test the commands or to manually verify the validity of the structures.
The 'commandsTest' file do provide some commands used to verify the data.
Init the python in this shell, import the packages and good testing!

## To start the python in the docker environment: ##

`docker exec -it scsr-api_web_run_`**XXX**` python3`

## To perform the tests designed: (where tests.py is the file with the tests to perform) ##

`docker exec -it scsr-api_web_run_`**XXX**` python3 scsr_api/tests.py -v`

## To open MongoDB shell in db container:

`docker exec -it scsr_api_db_1 mongo`

# Maintenance #

## If some new libraries needs installing: ##
* npm: just npm install
* python: add to requirements.txt
* And finally:

`docker-compose build`


