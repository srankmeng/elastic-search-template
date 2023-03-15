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
    ES_PORT = os.getenv('ES_PORT')
    ES_INDEX_NAME = os.getenv('ES_INDEX_NAME')

    es_client = Elasticsearch(
        "http://localhost:{}".format(ES_PORT),
        basic_auth=("elastic", ELASTIC_PASSWORD),
        verify_certs=False,
    )

    print("=============== Read csv file ===============")
    csv_file_path = os.path.join("data", "initial_data.csv")
    df = pd.read_csv(csv_file_path)
    json_str = df.to_json(orient='records')
    json_records = json.loads(json_str)

    index_name = ES_INDEX_NAME
    number_of_shards = 1
    es_params = {
        "index": index_name,
        "body": {
            "settings": {"index": {
                "number_of_shards": number_of_shards,
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
            }},
            "mappings": {
                "properties": {
                    "spec_no": {
                        "type": "keyword"
                    },
                    "spec_issue_no": {
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "spec_name": {
                        "analyzer": "trigrams",
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "spec_shortname": {
                        "analyzer": "trigrams",
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    },
                    "status": {
                        "type": "keyword"
                    },
                    "cross_reference": {
                        "type": "keyword"
                    },
                    "effective_date": {
                        "type": "date",
                        "format": ["dd-MMM-yy h.mm.ss a"]
                    },
                    "originator": {
                        "analyzer": "trigrams",
                        "type": "text",
                        "fields": {
                            "keyword": {
                                "type": "keyword"
                            }
                        }
                    }
                }
                
            },
        },
    }
    if es_client.indices.exists(index=index_name):
        es_client.indices.delete(index=index_name)
    es_client.indices.create(**es_params)
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