FROM python:3.12-alpine

RUN apk add --no-cache ffmpeg
RUN apk add --no-cache yt-dlp

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD python app.py