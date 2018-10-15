FROM alpine:3.7

EXPOSE 3031
EXPOSE 9191
VOLUME /usr/src/app/public
WORKDIR /usr/src/app

RUN apk add --no-cache \
        uwsgi-python3 \
        python3

COPY . .
RUN rm -rf public/*

RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "uwsgi", "--ini", "project.ini" ]