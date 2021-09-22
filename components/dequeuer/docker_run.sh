docker container rm -f dequeuer_container
docker run --name dequeuer_container --network host dequeuer "10C54083-FBC2-4777-A8EA-CF26EDFD24EB" "http://0.0.0.0:80" 28574 10 "0.1" "0.1" "0.1" 128 128 5
docker stop dequeuer_container
