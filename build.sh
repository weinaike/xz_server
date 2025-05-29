docker stop xiaozhi-esp32-server

docker build --network host -t xiaozhi-esp32-server:server_latest -f ./Dockerfile-server .

cd xz-server

docker-compose -f docker-compose.yml up -d

