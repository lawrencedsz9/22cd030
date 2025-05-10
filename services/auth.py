import requests

def get_token():
    url = "http://20.244.56.144/evaluation-service/auth"
    payload = {
        "email": "22j30.lowrence@sjec.ac.in",
        "name": "lowrence dsouza",
        "rollNo": "4s022cd030",
        "accessCode": "KjJAxP",
        "clientID": "af256a6c-1341-42fd-83b4-d7b05f299754",
        "clientSecret": "vubJkmWyWEaJfkfw"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json().get("token")  
    except requests.RequestException as e:
        print(f"Error fetching token: {e}")
        return None