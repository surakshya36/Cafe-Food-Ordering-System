import requests
from django.conf import settings

def verify_khalti_payment(token, amount):
    url = "https://khalti.com/api/v2/payment/verify/"
    key = settings.KHALTI_SANDBOX_SECRET_KEY  # Always use sandbox key

    payload = {
        "token": token,
        "amount": amount
    }

    headers = {
        "Authorization": f"Key {key}"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
