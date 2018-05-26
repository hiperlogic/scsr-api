echo "Building the container, this may take a while!"
docker-compose build
echo "starting the container as server... wait up! this will take a while!"
docker-compose run --service-ports web &
sleep 20
echo "Starting the execution of the tests. After that the system will end."
docker exec -it scsr-api_web_run_1 python3 scsr_api/modeltests.py -v
