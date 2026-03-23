import os
from redis import Redis
from rq import Worker, Queue

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
redis_conn = Redis.from_url(redis_url)

queue = Queue('notifications', connection=redis_conn)

if __name__ == '__main__':
    worker = Worker([queue], connection=redis_conn)
    worker.work()
