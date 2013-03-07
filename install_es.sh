wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.0.Beta1.tar.gz
tar xfvz elasticsearch-0.90.0.Beta1.tar.gz
mv elasticsearch-0.90.0.Beta1 elasticsearch
elasticsearch/bin/plugin -install lukas-vlcek/bigdesk -install mobz/elasticsearch-head -install elasticsearch/elasticsearch-lang-python/1.2.0 -install elasticsearch/elasticsearch-lang-javascript/1.3.0 -install elasticsearch/elasticsearch-mapper-attachments/1.7.0 -install elasticsearch/elasticsearch-thrift/1.5.0