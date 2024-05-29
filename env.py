import os

def openai_api_key():
    os.environ["OPENAI_API_KEY"] = "your openai api key"
    print("Environment variable set successfully.")