import requests
import pickle
import redis

from tenacity import retry, stop_after_attempt, wait_fixed
from requests.utils import dict_from_cookiejar, cookiejar_from_dict

from stream_fusion.utils.yggfilx.ygg_auth import ygg_login
from stream_fusion.settings import settings
from stream_fusion.logging_config import logger


class YggSessionManager:
    def __init__(self, redis_url):
        self.redis_url = f"redis://{settings.redis_host}:{settings.redis_port}"
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)
        self.session_expiry = 7200  # 2 hour
        self.session_id = f"ygg_session:{settings.ygg_user}"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.3))
    def check_redis_connection(self):
        try:
            self.redis.ping()
        except redis.ConnectionError as e:
            logger.error(f"Échec de connexion à Redis : {e}")
            raise Exception("Échec de connexion à Redis")

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.3))
    def new_session(self):
        ygg_session = ygg_login()
        session_data = {
            "cookies": pickle.dumps(dict_from_cookiejar(ygg_session.cookies)),
            "headers": pickle.dumps(dict(ygg_session.headers)),
        }
        self.redis.hmset(self.session_id, session_data)
        self.redis.expire(self.session_id, self.session_expiry)
        return ygg_session

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.3))
    def get_session(self):
        session_data = self.redis.hgetall(self.session_id)
        if not session_data:
            return None

        requests_session = requests.Session()
        requests_session.cookies = cookiejar_from_dict(
            pickle.loads(session_data["cookies"])
        )
        requests_session.headers.update(pickle.loads(session_data["headers"]))
        return requests_session

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.3))
    def save_session(self, requests_session):
        session_data = {
            "cookies": pickle.dumps(dict_from_cookiejar(requests_session.cookies)),
            "headers": pickle.dumps(dict(requests_session.headers)),
        }
        self.redis.hmset(self.session_id, session_data)
        self.redis.expire(self.session_id, self.session_expiry)

    def init_session(self):
        self.check_redis_connection()
        session_id, _ = self.new_session()
        return session_id

    def get_or_create_session(self):
        session = self.get_session()
        if session is None:
            session = self.new_session()
        return session
