import requests
from constants import SERVER_URL
from profile import Profile
import json

BASE_URL = SERVER_URL #where server is running

def register(username, password):
    response = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
    print(response.json())

def login(username, password):
    response = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    print(response.json())

def get_user(username):
    response = requests.get(f"{BASE_URL}/get-user", json={"username": username})
    print(response.json())
    print(Profile(**json.loads(str(response.json()).replace("\'","\""))).id)

# Example usage:
#register("testuser2", "securepassword123")
#login("testuser", "unsecurepassword")
get_user("testuser2")