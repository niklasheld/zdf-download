FROM python:3.8-alpine

RUN apk add  --no-cache ffmpeg
RUN apk add  --no-cache youtube-dl

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD python zdf-download.py