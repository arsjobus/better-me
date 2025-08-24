import redis

class RedisClient:
    def __init__(self, url, token):
        self.url = url
        self.token = token
        self.client = redis.Redis.from_url(url, password=token)

    def get_all_task_keys(self):
        return self.client.keys('task:*')

    def get_all_data_for_keys(self, keys):
        return self.client.mget(keys)
    
    def set_task(self, key, data):
        return self.client.set(key, data)