import requests
from django.conf import settings

def verify_email_with_zerobounce(email):
    api_key = settings.ZEROBOUNCE_API_KEY
    url = f"https://api.zerobounce.net/v2/validate?api_key={api_key}&email={email}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        # Example response: { "status": "valid", "sub_status": "", ... }
        return data
    except Exception as e:
        return {"status": "error", "error": str(e)}
