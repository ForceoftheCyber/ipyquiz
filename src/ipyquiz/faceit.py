import requests
from questions import display_questions, Question

API_BASE_URL = "https://dev.faceittools.com/questions/fetch_questions/"

def display_simple_search(body: str):
    response = requests.get(f"{API_BASE_URL}{body}")

    if response.status_code == 204:
        return []
    elif response.status_code == 200:
        content = response.json()
        
        # Sanity check
        if content["status"] != "success":
            raise RuntimeError("Fetch returned with response code 200, but status in body was not 'success'")
        
        display_questions(questions=content["questions"])        
    else:
        raise requests.exceptions.RequestException(f"Fetch resulted in a HTTP error with status code: {response.status_code}")
