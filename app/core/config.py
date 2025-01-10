import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env') # Path to .env file
load_dotenv(dotenv_path=dotenv_path, verbose=True) # Load the .env file
# verbose = True: Print out all of errors and informations the loaded .env file

class Settings():
    algorithm: str = os.getenv("algorithm")
    
    access_secret_key: str = os.getenv("access_token_secret_key")
    refresh_secret_key: str = os.getenv("refresh_token_secret_key")

def get_settings():
    return Settings()
