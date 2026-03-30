import redis
from dotenv import load_dotenv
import os
load_dotenv()
from exceptions import RedisError

class RedisConfig:
    
    def __init__(self):
        self.redis= redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            username=os.getenv("REDIS_USERNAME"),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=True
        )
        
    def get_redis(self):
        return self.redis
    
    def set_value(self,key:str,value:str,ex:int=None):
        try:
            self.redis.set(name=key,value=value,ex=ex)
            print(f"Value set in Redis: {key}={value}")
        except Exception as e:
            raise RedisError("Failed to set value in Redis: " + str(e)) from e
        
    def get_value(self,key:str)->str:
        try:
            value=self.redis.get(name=key)
            print(f"Value retrieved from Redis: {key}={value}")
            return value
        except Exception as e:
            print("Error getting value from Redis:", e)
            raise RedisError("Failed to get value from Redis: " + str(e)) from e

    def delete_value(self,key:str):
        try:
            self.redis.delete(key)
            print(f"Value deleted from Redis: {key}")
        except Exception as e:
            print("Error deleting value from Redis:", e)
            raise RedisError("Failed to delete value from Redis: " + str(e)) from e
        
    def does_exist(self,key:str)->bool:
        try:
            exists=self.redis.exists(key)
            print(f"Checked existence in Redis: {key} exists={exists}")
            return exists == 1
        except Exception as e:
            print("Error checking existence in Redis:", e)
            raise RedisError("Failed to check existence in Redis: " + str(e)) from e
        
redisClient=RedisConfig()