FROM python:3.8
WORKDIR /app
RUN mkdir -p /app/data
ADD . /app
ADD ./data /app/data

ENV ELASTIC_PASSWORD=$ELASTIC_PASSWORD
ENV ES_INDEX_NAME=$ES_INDEX_NAME
ENV ES_HOST=elasticsearch

RUN pip install -r requirements.txt
CMD [ "python", "indexer.py"]