docker build -t xiaozhi-esp32-server:web_latest -f ./Dockerfile-web .

docker login --username=weinaike@qq.com crpi-vitbwrstzgakrrjz.cn-hangzhou.personal.cr.aliyuncs.com
docker tag xiaozhi-esp32-server:web_latest crpi-vitbwrstzgakrrjz.cn-hangzhou.personal.cr.aliyuncs.com/yes-tek/xiaozhi-esp32-server:web_latest
docker push crpi-vitbwrstzgakrrjz.cn-hangzhou.personal.cr.aliyuncs.com/yes-tek/xiaozhi-esp32-server:web_latest