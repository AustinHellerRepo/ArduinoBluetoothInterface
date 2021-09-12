docker container rm -f dequeuer_container
docker run --name dequeuer_container --network host dequeuer "24711775-5D70-4613-AEDA-9367F32C7048" "http://0.0.0.0:80" 28574 128 128 10
docker stop dequeuer_container
