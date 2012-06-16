wget https://github.com/downloads/elasticsearch/elasticsearch/elasticsearch-0.19.4.zip
unzip elasticsearch-0.19.4.zip
mv elasticsearch-0.19.4 elasticsearch
elasticsearch/bin/plugin -install lukas-vlcek/bigdesk -install mobz/elasticsearch-head -install elasticsearch/elasticsearch-lang-python/1.1.0 -install elasticsearch/elasticsearch-lang-javascript/1.1.0 -install elasticsearch/elasticsearch-mapper-attachments/1.4.0