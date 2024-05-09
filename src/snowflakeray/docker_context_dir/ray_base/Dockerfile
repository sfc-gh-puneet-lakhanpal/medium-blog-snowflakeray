FROM python:3.9-slim
RUN apt-get update -y
RUN apt-get install -y unzip git net-tools sudo
RUN pip3 install --upgrade pip
COPY ray_requirements.txt ./
RUN pip3 install -r ray_requirements.txt
COPY usecase_requirements.txt ./
RUN pip3 install -r usecase_requirements.txt
COPY entrypoint.sh ./