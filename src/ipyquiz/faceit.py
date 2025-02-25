import requests
from ipyquiz.questions import display_questions, display_json, Question
import json

API_BASE_URL = "https://dev.faceittools.com/questions/fetch_questions/"

def display_simple_search(body: str, max_questions: int = 10):
    """
    params:
    - body: search string in question body
    - max_questions: maximum number of questions displayed
    """
    response = requests.get(f"{API_BASE_URL}{body}")

    if response.status_code == 204:
        return []
    elif response.status_code == 200:
        content = response.json()
        
        # Sanity check
        if content["status"] != "success":
            raise RuntimeError("Fetch returned with response code 200, but status in body was not 'success'")
        
        # Also limits questions
        questions = json.loads(content["questions"])[0:max_questions]

        display_questions(questions=questions)       
    else:
        raise requests.exceptions.RequestException(f"Fetch resulted in a HTTP error with status code: {response.status_code}")
    
# # For debugging
# if __name__ == "__main__":
#     display_simple_search("math")
