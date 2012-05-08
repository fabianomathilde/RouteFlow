import threading
import time

import pymongo as mongo
import bson

import IPC

FROM_FIELD = "from"
TO_FIELD = "to"
TYPE_FIELD = "type"
READ_FIELD = "read"
CONTENT_FIELD = "content"

# 1 MB for the capped collection
CC_SIZE = 1048576

def put_in_envelope(from_, to, msg):
    envelope = {}

    envelope[FROM_FIELD] = from_
    envelope[TO_FIELD] = to
    envelope[READ_FIELD] = False
    envelope[TYPE_FIELD] = msg.get_type()

    envelope[CONTENT_FIELD] = {}
    for (k, v) in msg.items():
        envelope[CONTENT_FIELD][k] = v

    return envelope

def take_from_envelope(envelope, factory):
    msg = factory.build_for_type(envelope[TYPE_FIELD]);
    msg.from_dict(envelope[CONTENT_FIELD]);
    return msg;


class MongoIPCMessageService(IPC.IPCMessageService):
    def __init__(self, address, db, id_):
        self._db = db
        try:
            tmp = address.split(":")
            if len(tmp) == 2:
                self._address = (tmp[0], int(tmp[1]))
            elif len(tmp) == 1:
                self._address = (tmp[0],)
        except:
            raise ValueError, "Invalid address: " + str(address)
        self._id = id_
        self._producer_connection = mongo.Connection(*self._address)
        
        
    def listen(self, channel_id, factory, processor, block=True):
        worker = threading.Thread(target=self._listen_worker, args=(channel_id, factory, processor))
        worker.start()
        if block:
            worker.join()
        
    def send(self, channel_id, to, msg):
        self._create_channel(self._producer_connection, channel_id)
        collection = self._producer_connection[self._db][channel_id]
        collection.insert(put_in_envelope(self.get_id(), to, msg))
        return True

    def _listen_worker(self, channel_id, factory, processor):
        connection = mongo.Connection(*self._address)
        self._create_channel(connection, channel_id)
        
        collection = connection[self._db][channel_id]
        cursor = collection.find({TO_FIELD: self.get_id(), READ_FIELD: False}, sort=[("_id", mongo.ASCENDING)])

        while True:
            for envelope in cursor:
                msg = take_from_envelope(envelope, factory)
                processor.process(envelope[FROM_FIELD], envelope[TO_FIELD], channel_id, msg);
                collection.update({"_id": envelope["_id"]}, {"$set": {READ_FIELD: True}})
            time.sleep(0.05)
            cursor = collection.find({TO_FIELD: self.get_id(), READ_FIELD: False}, sort=[("_id", mongo.ASCENDING)])

    def _create_channel(self, connection, name):
        db = connection[self._db]
        try:
            collection = mongo.collection.Collection(db, name, None, True, capped=True, size=CC_SIZE)
            collection.ensure_index([("_id", mongo.ASCENDING)])
            collection.ensure_index([(TO_FIELD, mongo.ASCENDING)])
        # TODO: improve this catch. It should be more specific, but pymongo
        # behavior doesn't match its documentation, so we are being dirty.
        except:
            pass

class MongoIPCMessage(dict, IPC.IPCMessage):
    def __init__(self, type_, **kwargs):
        dict.__init__(self)
        self.from_dict(kwargs)
        self._type = type_
        
    def get_type(self):
        return self._type

    def from_dict(self, data):
        for (k, v) in data.items():
            self[k] = v
        
    def from_bson(self, data):
        data = bson.BSON.decode(data)
        self.from_dict(data)

    def to_bson(self):
        return bson.BSON.encode(self)
        
    def str(self):
        string = ""
        for (k, v) in self.items():
            string += str(k) + ": " + str(v) + "\n"
        return string
        
    def __str__(self):
        return IPC.IPCMessage.__str__(self)
