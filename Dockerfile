FROM python:3.7
WORKDIR /controller
ADD requirements.txt .
RUN pip3 install -r requirements.txt

ARG gif_dir=/bin/temp
ENV GIF_DIRECTORY=$gif_dir

COPY . .
EXPOSE 5000
CMD ["python3", "web-controller.py"]