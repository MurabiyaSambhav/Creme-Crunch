import requests
import os

# Load API key from environment variable (recommended)
API_KEY = os.getenv("ZEROBOUNCE_API_KEY", "94cfc438aed743c5ae079dafbfec2f8f")

def verify_email_with_zerobounce(email, ip_address=""):
    """
    Validate email using ZeroBounce API.
    Returns dict with either 'status' or 'error'.
    """
    url = "https://api.zerobounce.net/v2/validate"
    params = {
        "api_key": API_KEY,
        "email": email,
        "ip_address": ip_address or ""
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}
