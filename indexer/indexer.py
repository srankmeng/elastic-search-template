from retry import retry
import pandas as pd
import elasticsearch
import elasticsearch.helpers
from elasticsearch import Elasticsearch
import os
import json
from dotenv import load_dotenv

@retry(elasticsearch.ConnectionError, max_delay=300, delay=5)
def indexer():
  load_dotenv()

  print("============== Connect elastic ==============")
  ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
  ES_INDEX_NAME = os.getenv('ES_INDEX_NAME')
  ES_HOST = os.getenv('ES_HOST') or "localhost"
  ES_PORT = 9200

  es_client = Elasticsearch(
      "http://{}:{}".format(ES_HOST, ES_PORT),
      basic_auth=("elastic", ELASTIC_PASSWORD),
      verify_certs=False,
  )

  print("=============== Read csv file ===============")
  csv_file_path = os.path.join("data", "initial_data.csv")
  df = pd.read_csv(csv_file_path)
  json_str = df.to_json(orient='records')
  json_records = json.loads(json_str)

  index_name = ES_INDEX_NAME

  settings = {
    "number_of_shards": 1,
    "max_ngram_diff": 100,
    "analysis": {
      "analyzer": {
        "trigrams": {
          "type": "custom",
          "tokenizer": "trigram_tokenizer",
          "filter": [
            "lowercase"
          ]
        }
      },
      "tokenizer": {
        "trigram_tokenizer": {
        "type": "ngram",
        "min_gram": 3,
        "max_gram": 100,
        "token_chars": []
        }
      }
    }
  }
  mappings = {
  "properties": {
      "CAL_METHOD": {
        "type": "text"
      },
      "CANCEL_FLAG": {
        "type": "text"
      },
      "CREATE_DATE": {
        "type": "date",
        "format": ["dd-MMM-yy"]
      },
      "CUSTOMER_CLASS": {
        "type": "text"
      },
      "DESTINATION_SITE": {
        "analyzer": "trigrams",
        "type": "text"
      },
      "DESTINATION_SITE_CODE": {
        "type": "keyword"
      },
      "EFFECTIVE_DATE": {
        "type": "date",
        "format": ["dd-MMM-yy"]
      },
      "LAST_UPDATE_DATE": {
        "type": "date",
        "format": ["dd-MMM-yy"]
      },
      "LAST_USER_ID": {
        "type": "text"
      },
      "MAX_RATE": {
        "type": "float"
      },
      "MIN_RATE": {
        "type": "float"
      },
      "ORIGIN_SITE": {
        "analyzer": "trigrams",
        "type": "text"
      },
      "ORIGIN_SITE_CODE": {
        "type": "keyword"
      },
      "PAYMENT_AMOUNT": {
        "type": "float"
      },
      "PLANT_CODE": {
        "type": "keyword"
      },
      "PRODUCT_GROUP": {
        "analyzer": "trigrams",
        "type": "text"
      },
      "PRODUCT_GROUP_CODE": {
        "type": "keyword"
      },
      "RECEIVE_AMOUNT": {
        "type": "float"
      },
      "TRANSPORT_TYPE": {
        "analyzer": "trigrams",
        "type": "text"
      },
      "TRANSPORT_TYPE_CODE": {
        "type": "keyword"
      },
      "TRIP_TYPE": {
        "analyzer": "trigrams",
        "type": "text"
      },
      "TRIP_TYPE_CODE": {
        "type": "keyword"
      },
      "TRUCK_CLASS": {
        "analyzer": "trigrams",
        "type": "text"
      },
      "TRUCK_CLASS_CODE": {
        "type": "keyword"
      },
      "USER_CREATE": {
        "type": "text"
      }
    }
  }

  if es_client.indices.exists(index=index_name):
    es_client.indices.delete(index=index_name)
  es_client.indices.create(index=index_name, settings=settings, mappings=mappings)
  
  action_list = []
  for row in json_records:
    record ={
      '_op_type': 'index',
      '_index': index_name,
      '_source': row
    }
    action_list.append(record)

  print("============= Start import data =============")
  elasticsearch.helpers.bulk(es_client, action_list)

  print("=========== Import data successful ==========")

if __name__ == "__main__":
  indexer()