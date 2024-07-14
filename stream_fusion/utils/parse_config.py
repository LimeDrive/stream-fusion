import json
import base64
from cryptography.fernet import Fernet
from stream_fusion.settings import settings

def parse_config(encoded_config):
    try:
        # Base64 decoding
        encrypted_data = base64.b64decode(encoded_config)

        # Create Fernet key from the secret key
        fernet_key = Fernet.generate_key()
        f = Fernet(fernet_key)

        # Decrypt the data
        decrypted_data = f.decrypt(encrypted_data).decode('utf-8')

        # JSON parsing
        config = json.loads(decrypted_data)

        # For backward compatibility
        if "languages" not in config:
            config["languages"] = [config["language"]]

        if "anonymizeMagnets" not in config:
            config["anonymizeMagnets"] = False

        return config
    except Exception as e:
        raise ValueError(f"Error during configuration decoding/decryption: {str(e)}")