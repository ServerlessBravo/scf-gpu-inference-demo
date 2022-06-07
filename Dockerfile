FROM tensorflow/tensorflow:latest-gpu-jupyter

# 指定工作目录
WORKDIR /usr/src/app

# 安装依赖
RUN apt-get update \ 
  && apt-get install -y python3 \ 
  && apt-get install -y python3-pip \
  && pip3 install matplotlib \
  && pip3 install tensorflow_hub

COPY . .

# 容器启动命令
CMD [ "python3", "-u", "/usr/src/app/app.py" ]
EXPOSE 9000

