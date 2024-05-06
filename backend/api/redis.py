from redis import Redis
from rq import Queue

from api.constants import constants

redis_conn = Redis.from_url(constants.redis_uri, socket_timeout=500)
task_queue = Queue(constants.channel_name, connection=redis_conn)
