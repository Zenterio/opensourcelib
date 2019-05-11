import pickle

from zaf.messages.message import EndpointId, MessageId

MESSAGE = MessageId('message', '')
PICKLED_MESSAGE = pickle.dumps(MESSAGE)
PICKLED_MESSAGES = pickle.dumps([MESSAGE])
ENDPOINT = EndpointId('endpoint', '')
PICKLED_ENDPOINT = pickle.dumps(ENDPOINT)
PICKLED_ENDPOINTS = pickle.dumps([ENDPOINT])
DATA = {'a': 'b', 3: 4, MESSAGE: ENDPOINT}
PICKLED_DATA = pickle.dumps(DATA)
ENTITY = 'entity'
PICKLED_ENTITY = pickle.dumps(ENTITY)
PICKLED_ENTITIES = pickle.dumps([ENTITY])
