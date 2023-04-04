# POC search material

## Setup Elasticsearch and Kibana with [Docker compose](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)

#### Start services
```
$ docker compose up
```

#### Start services with any changes
```
$ docker compose up --build --force-recreate
```
**Note:** In `docker-compose.yml` the services are include elasticsearch, kibana and indexer. If you want to auto import initial data when run `docker compose up`, you can uncomment service indexer.

## Login Kibana
- Go to `http://localhost:5601`
- username: `elastic`
- password: `xitgmLwmp`

**Note:** You can change password in `.env` file

## Call Elastic search api
- Host: `http://localhost:9200`
- Basic auth [username: `elastic`] [password: `xitgmLwmp`]

**Note:** You can change password in `.env` file

You can change CORS domain in `docker-compose.yml` at elasticsearch service.

## Import data from csv file with [Docker compose]

**Note:** Change host url, index name and setting/mapping before run command

Change index name in `.env` file in valiable ES_INDEX_NAME
```
ES_INDEX_NAME=<index name>
```
Config file path for import initial data
- /elastic-search-tempate/indexer/data

You can change file name or path but you must chang both in file indexer.py too
```
csv_file_path = os.path.join(<Folder name>, <File name>)
```

You can change settings and mappings config in file indexer.py in valiable settings
```
settings = {<Settings config>}
mappings = {<Mappings config>}
```

Go to `docker-compose.yml` and make sure to use indexer service

Run this command
```
$ docker compose up indexer
```

## Import data from csv file with [Python3]

**Note:** Change host url, index name and setting/mapping before run command

Change directory to indexer
```
$ cd indexer
```
Use these commands for run script import data with python
```
$ python3 -m venv env/local && source env/local/bin/activate
$ pip3 install -r requirements.txt
$ python3 indexer.py
```

## Insert / Update data

#### Insert
```
POST <index_name>/_doc
{
  "<field_name_1>": "<value1>",
  "<field_name_2>": "<value2>",
  "<field_name_3>": "<value3>"
}
```

#### Insert (example)
```
POST materials/_doc
{
	"material_id": 1,
	"spec_no": "MAT00001",
	"spec_name": "material one",
	"spec_shortname": "material one",
	"created_date": "2023/02/28",
	"status": "yes"
}
```

#### Update
```
PUT <index_name>/_doc/<id> 
{
  "<field_name_1>": "<value1>",
  "<field_name_2>": "<value2>",
  "<field_name_3>": "<value3>"
}
```

## Index mapping

#### Update mapping
```
PUT <index_name>/_mapping
{
  "properties": {
    "<field_name>": {
      "type": “<field_type>"
    },
    ...
  }
}
```

#### Update mapping (example)
```
PUT materials/_mapping
{
  "properties": {
    "status": {
      "type": "keyword"
    }
  }
}
```

#### Get mapping
```
GET <index_name>/_mapping 
```

## Query data

#### [Match](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html)
```
POST <index_name>/_search
{
  "query": {
    "match": {
      "<field_name>": "<value>"
    }
  }
} 
```

#### [Term](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-term-query.html)
```
POST <index_name>/_search
{
  "query": {
    "term": {
      "<field_name>": "<value>"
    }
  }
} 
```

#### [Should](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html)
```
POST <index_name>/_search
{
  "query":{
	"bool":{
	  "should":[
		{
		  "match":{
			"<field_name_1>":"<value1>"
		  }
		},
        {
          "match":{
        	"<field_name_2>":"<value2>"
          }
		}
	  ],
	  "minimum_should_match":1
	}
  }
}
```

#### [Must](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html)
```
POST <index_name>/_search
{
  "query":{
	"bool":{
	  "must":[
		{
		  "match":{
			"<field_name_1>":"<value1>"
		  }
		},
        {
          "match":{
        	"<field_name_2>":"<value2>"
          }
		}
	  ]
	}
  }
}
```

#### [Filter](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html)
```
POST <index_name>/_search
{
  "query":{
	"bool":{
	  "filter":[
		{
		  "term":{
			"<field_name_1>":"<value1>"
		  }
		},
        {
          "range":{
        	"<field_name_2>": {
			  "gte": "<start_date>",
			  "lte": "<end_date>", 
            }
          }
		}
	  ]
	}
  }
}
```

#### [Limit](https://www.elastic.co/guide/en/elasticsearch/reference/current/paginate-search-results.html)
```
POST <index_name>/_search
{
  "from": 0,
  "size": 10,
  "query": {
  	...
  }
} 
```

#### Count
```
GET <index_name>/_count
```

## [Wildcard](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-wildcard-query.html)
```
POST <index_name>/_search
{
  "query": {
    "wildcard": {
      "<field_name>": "<partial_text>*"
    }
  }
} 
```

#### Example
```
POST <index_name>/_search
{
  "query": {
    "wildcard": {
	  "spec_name": "mat*"
    }
  }
} 
```

## [Analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-analyzers.html)

#### Check value when use analyze 
```
POST <index_name>/_analyze
{
  "text": "<value>",
  "analyzer": "standard"
} 
```

#### Define analyze with field  
```
PUT <index_name>/_mapping
{
  "properties": {
	"<field_name>": {
	  "type": "text",
	  "analyzer": "standard"
	}
  }
} 
```

## Create a custom tokenizer and analyzer ([ngram](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-ngram-tokenizer.html))
```
PUT <index_name>
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "max_ngram_diff": "10",
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
          "max_gram": 10,
          "token_chars": []
        }
      }
    }
  }
}
```


#### Search data with ngram (example)
```
POST materials/_search
{
  "query": {
    "bool": {
      "should": [
        {
          "term": {
            "spec_no": {
              "value": "mat"
            }
          }
        }
      ]
    }
  }
}
```

## [Aliases](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-aliases.html)

#### Create alias
```
POST _aliases 
{
  "actions":[
    {
      "add": {
        "index": <index_name>,
        "alias": <alias_name>
      }
    }
  ]
} 
```

#### Switch alias & remove unused alias
```
POST _aliases 
{
  "actions":[
    {
      "add": {
        "index": <index_dest>,
        "alias": <alias_name>
      }
    },
    {
      "remove_index": {
        "index": "<index_source>"
      }
    }
  ]
} 
```
