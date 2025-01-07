import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env') # Path to .env file
load_dotenv(dotenv_path=dotenv_path, verbose=True) # Load the .env file
# verbose = True: Print out all of errors and informations the loaded .env file

class Settings():
    algorithm: str = os.getenv("algorithm")
    
    user_access_secret_key: str = os.getenv("user_access_token_secret_key")
    user_refresh_secret_key: str = os.getenv("user_refresh_token_secret_key")
    admin_access_secret_key: str = os.getenv("admin_access_token_secret_key")
    admin_refresh_secret_key: str = os.getenv("admin_refresh_token_secret_key")

def get_settings():
    return Settings()
