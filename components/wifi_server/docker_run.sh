docker container rm -f wifi_server_container
docker run --name wifi_server_container -p 80:80 wifi_server
docker stop wifi_server_container
