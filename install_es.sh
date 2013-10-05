wget -c --no-check-certificate https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-0.90.5.tar.gz
tar xfvz elasticsearch-0.90.5.tar.gz
mv elasticsearch-0.90.5 elasticsearch
elasticsearch/bin/plugin -install lukas-vlcek/bigdesk -install mobz/elasticsearch-head -install elasticsearch/elasticsearch-lang-python/1.2.0 -install elasticsearch/elasticsearch-lang-javascript/1.3.0 -install elasticsearch/elasticsearch-mapper-attachments/1.7.0 -install elasticsearch/elasticsearch-transport-thrift/1.5.0
elasticsearch/bin/plugin -install royrusso/elasticsearch-HQ
elasticsearch/bin/plugin -install elasticsearch/elasticsearch-river-twitter/1.2.0 
elasticsearch/bin/plugin -install richardwilly98/elasticsearch-river-mongodb/1.6.11
elasticsearch/bin/plugin -url http://bit.ly/145e9Ly -install river-jdbc
cd elasticsearch/plugins/river-jdbc
wget http://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.26.zip/from/http://cdn.mysql.com/ -O mysql-connector-java-5.1.26.zip
unzip mysql-connector-java-5.1.26.zip
mv mysql-connector-java-5.1.26/mysql-connector-java-5.1.26-bin.jar .
rm -rf mysql-connector-java-5.1.26
rm -rf mysql-connector-java-5.1.26.zip
wget http://jdbc.postgresql.org/download/postgresql-9.2-1003.jdbc4.jar
cd ..
cd ..
cd ..
