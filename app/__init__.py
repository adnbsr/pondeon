from json import JSONEncoder
from bson.objectid import ObjectId

class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        elif set(['quantize', 'year']).intersection(dir(obj)):
            return str(obj)
        elif hasattr(obj, 'next'):
            return list(obj)
        return JSONEncoder.default(self, obj)
