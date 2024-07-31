import aiohttp
import redis
import requests

from stream_fusion.settings import settings

class RealDebridService:
    BASE_URL = "https://api.real-debrid.com/oauth/v2"
    CLIENT_ID = "X245A4XAIBGVM"  # Client ID for open source apps

    async def get_device_code(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/device/code", params={"client_id": self.CLIENT_ID, "new_credentials": "yes"}) as response:
                return await response.json()

    async def get_credentials(self, device_code):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}/device/credentials", params={"client_id": self.CLIENT_ID, "code": device_code}) as response:
                if response.status == 200:
                    return await response.json()
                return {"error": "Authorization pending"}

    async def get_token(self, client_id, client_secret, device_code):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.BASE_URL}/token", data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": device_code,
                "grant_type": "http://oauth.net/grant_type/device/1.0"
            }) as response:
                return await response.json()
            
class RDTokenManager:
    BASE_URL = "https://api.real-debrid.com/oauth/v2"

    def __init__(self, config):
        self.redis = redis.Redis(host=settings.redis_host, port=settings.redis_port)
        self.config = config
        self.rd_config = self.config.get('debridKey', {})
        if not self.rd_config:
            raise Exception("Real Debrid configuration not found")
        
        self.client_id = self.rd_config.get('client_id')
        self.client_secret = self.rd_config.get('client_secret')
        self.refresh_token = self.rd_config.get('refresh_token')
        self.apikey = self.config.get('apiKey')
        
        if not all([self.client_id, self.client_secret, self.refresh_token, self.apikey]):
            raise Exception("Missing required Real Debrid configuration")

    def get_access_token(self):
        token = self.redis.get(f"rd_access_token:{self.apikey}")
        if token:
            return token.decode('utf-8')
        return self.new_access_token()

    def new_access_token(self):
        response = requests.post(f"{self.BASE_URL}/token", data={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": self.refresh_token,
            "grant_type": "http://oauth.net/grant_type/device/1.0"
        })
        
        response.raise_for_status()
        
        data = response.json()
        self.redis.setex(f"rd_access_token:{self.apikey}", int(data['expires_in']), data['access_token'])
                
        return data['access_token']