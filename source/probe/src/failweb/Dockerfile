FROM python:3.12-alpine
#RUN apk add --no-cache pipenv
COPY . /app
WORKDIR /app
RUN pip install pipenv; /usr/local/bin/pipenv install
CMD ["pipenv", "run", "python", "web/server.py"]
EXPOSE 80
