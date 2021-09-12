docker container rm -f dequeuer_container
docker run --name dequeuer_container -p 28574:80 dequeuer
docker stop dequeuer_container
