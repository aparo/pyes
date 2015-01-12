class River(object):
    def __init__(self, index_name=None, index_type=None, bulk_size=100, bulk_timeout=None):
        self.name = index_name
        self.index_name = index_name
        self.index_type = index_type
        self.bulk_size = bulk_size
        self.bulk_timeout = bulk_timeout

    def serialize(self):
        res = self._serialize()
        index = {}
        if self.name:
            index['name'] = self.name
        if self.index_name:
            index['index'] = self.index_name
        if self.index_type:
            index['type'] = self.index_type
        if self.bulk_size:
            index['bulk_size'] = self.bulk_size
        if self.bulk_timeout:
            index['bulk_timeout'] = self.bulk_timeout
        if index:
            res['index'] = index
        return res

    def __repr__(self):
        return str(self.serialize())

    def _serialize(self):
        raise NotImplementedError


class RabbitMQRiver(River):
    type = "rabbitmq"

    def __init__(self, host="localhost", port=5672, user="guest",
                 password="guest", vhost="/", queue="es", exchange="es",
                 routing_key="es", exchange_declare=True, exchange_type="direct",
                 exchange_durable=True, queue_declare=True, queue_durable=True,
                 queue_auto_delete=False, queue_bind=True, **kwargs):
        super(RabbitMQRiver, self).__init__(**kwargs)
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost
        self.queue = queue
        self.exchange = exchange
        self.routing_key = routing_key
        self.exchange_declare = exchange_declare
        self.exchange_type = exchange_type
        self.exchange_durable = exchange_durable
        self.queue_declare = queue_declare
        self.queue_durable = queue_durable
        self.queue_auto_delete = queue_auto_delete
        self.queue_bind = queue_bind

    def _serialize(self):
        return {
            "type": self.type,
            self.type: {
                "host": self.host,
                "port": self.port,
                "user": self.user,
                "pass": self.password,
                "vhost": self.vhost,
                "queue": self.queue,
                "exchange": self.exchange,
                "routing_key": self.routing_key,
                "exchange_declare": self.exchange_declare,
                "exchange_type": self.exchange_type,
                "exchange_durable": self.exchange_durable,
                "queue_declare": self.queue_declare,
                "queue_durable": self.queue_durable,
                "queue_auto_delete": self.queue_auto_delete,
                "queue_bind": self.queue_bind
            }
        }


class TwitterRiver(River):
    type = "twitter"

    def __init__(self, user=None, password=None, **kwargs):
        self.user = user
        self.password = password
        self.consumer_key = kwargs.pop('consumer_key', None)
        self.consumer_secret = kwargs.pop('consumer_secret', None)
        self.access_token = kwargs.pop('access_token', None)
        self.access_token_secret = kwargs.pop('access_token_secret', None)
        # These filters may be lists or comma-separated strings of values
        self.tracks = kwargs.pop('tracks', None)
        self.follow = kwargs.pop('follow', None)
        self.locations = kwargs.pop('locations', None)
        super(TwitterRiver, self).__init__(**kwargs)

    def _serialize(self):
        result = {"type": self.type}
        if self.user and self.password:
            result[self.type] = {"user": self.user,
                                 "password": self.password}
        elif (self.consumer_key and self.consumer_secret and self.access_token
              and self.access_token_secret):
            result[self.type] = {"oauth": {
                "consumer_key": self.consumer_key,
                "consumer_secret": self.consumer_secret,
                "access_token": self.access_token,
                "access_token_secret": self.access_token_secret,
            }
            }
        else:
            raise ValueError("Twitter river requires authentication by username/password or OAuth")
        filter = {}
        if self.tracks:
            filter['tracks'] = self.tracks
        if self.follow:
            filter['follow'] = self.follow
        if self.locations:
            filter['locations'] = self.locations
        if filter:
            result[self.type]['filter'] = filter
        return result


class CouchDBRiver(River):
    type = "couchdb"

    def __init__(self, host="localhost", port=5984, db="mydb", filter=None,
                 filter_params=None, script=None, user=None, password=None,
                 **kwargs):
        super(CouchDBRiver, self).__init__(**kwargs)
        self.host = host
        self.port = port
        self.db = db
        self.filter = filter
        self.filter_params = filter_params
        self.script = script
        self.user = user
        self.password = password

    def serialize(self):
        result = {
            "type": self.type,
            self.type: {
                "host": self.host,
                "port": self.port,
                "db": self.db,
                "filter": self.filter,
            }
        }
        if self.filter_params is not None:
            result[self.type]["filter_params"] = self.filter_params
        if self.script is not None:
            result[self.type]["script"] = self.script
        if self.user is not None:
            result[self.type]["user"] = self.user
        if self.password is not None:
            result[self.type]["password"] = self.password
        return result


class JDBCRiver(River):
    type = "jdbc"

    def __init__(self, dbhost="localhost", dbport=5432, dbtype="postgresql",
                 dbname=None, dbuser=None, dbpassword=None, poll_time="5s",
                 sql="", name=None, params=None, **kwargs):
        super(JDBCRiver, self).__init__(**kwargs)
        self.dbsettings = {
            'dbhost': dbhost,
            'dbport': dbport,
            'dbtype': dbtype,
            'dbname': dbname,
            'dbuser': dbuser,
            'dbpassword': dbpassword,
        }
        self.poll_time = poll_time
        self.sql = sql
        self.params = params or {}
        if name is not None:
            self.name = name

    def _serialize(self):
        ret = {
            "type": self.type,
            self.type: {
                "driver": "org.%(dbtype)s.Driver" % self.dbsettings,
                "url": "jdbc:%(dbtype)s://%(dbhost)s:%(dbport)s/%(dbname)s" \
                       % self.dbsettings,
                "user": "%(dbuser)s" % self.dbsettings,
                "password": "%(dbpassword)s" % self.dbsettings,
                "strategy": "simple",
                "poll": self.poll_time,
                "sql": self.sql.replace('\n', ' '),
            }
        }

        ret.update(self.params)

        return ret


class MongoDBRiver(River):
    type = "mongodb"

    def __init__(self, servers, db, collection, index_name, mapping_type, gridfs=False, options=None, bulk_size=1000,
                 filter=None, script=None, **kwargs):
        super(MongoDBRiver, self).__init__(**kwargs)
        self.name = index_name
        self.index_type = mapping_type
        self.bulk_size = bulk_size
        self.mongodb = {
            "servers": servers,
            "db": db,
            "collection": collection,
            "options": options or {},
            "gridfs": gridfs,
            "filter": filter
        }
        if script:
          self.mongodb['script'] = script

    def _serialize(self):
        result = {
            'type': self.type,
            'mongodb': self.mongodb
        }
        return result
