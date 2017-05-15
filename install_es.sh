
wget -c --no-check-certificate https://download.elastic.co/elasticsearch/elasticsearch/elasticsearch-1.7.3.tar.gz
tar xfvz elasticsearch-1.7.3.tar.gz
mv elasticsearch-1.7.3 elasticsearch
#elasticsearch/bin/plugin -install lukas-vlcek/bigdesk
cd elasticsearch
bin/plugin -install mobz/elasticsearch-head
bin/plugin -install elastic/elasticsearch-lang-python/2.7.0
bin/plugin -install elastic/elasticsearch-lang-javascript/2.7.0
bin/plugin -install elastic/elasticsearch-mapper-attachments/2.7.1
bin/plugin -install elastic/elasticsearch-transport-thrift/2.7.0
bin/plugin -install royrusso/elasticsearch-HQ
bin/plugin -install elastic/elasticsearch-river-twitter/2.6.0
#bin/plugin --install com.github.richardwilly98.elasticsearch/elasticsearch-river-mongodb/2.0.1
#elasticsearch/bin/plugin -url http://bit.ly/145e9Ly -install river-jdbc
#cd elasticsearch/plugins/river-jdbc
#wget http://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-5.1.26.zip/from/http://cdn.mysql.com/ -O mysql-connector-java-5.1.26.zip
#unzip mysql-connector-java-5.1.26.zip
#mv mysql-connector-java-5.1.26/mysql-connector-java-5.1.26-bin.jar .
#rm -rf mysql-connector-java-5.1.26
#rm -rf mysql-connector-java-5.1.26.zip
#wget http://jdbc.postgresql.org/download/postgresql-9.2-1003.jdbc4.jar
#cd ..
#cd ..
#cd ..
