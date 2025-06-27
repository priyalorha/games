
from cryptography.hazmat.primitives.asymmetric import ed25519
from urllib.parse import urlparse, urlencode
import urllib
import json
import requests

from coinswitch.keys import API_KEY, SECRET_KEY

params = {}

endpoint = "/trade/api/v2/validate/keys"
method = "GET"
payload = {}

secret_key = SECRET_KEY
api_key = API_KEY

unquote_endpoint = endpoint
if method == "GET" and len(params) != 0:
    endpoint += ('&', '?')[urlparse(endpoint).query == ''] + urlencode(params)
    unquote_endpoint = urllib.parse.unquote_plus(endpoint)

signature_msg = method + unquote_endpoint + json.dumps(payload, separators=(',', ':'), sort_keys=True)

request_string = bytes(signature_msg, 'utf-8')
secret_key_bytes = bytes.fromhex(secret_key)
secret_key = ed25519.Ed25519PrivateKey.from_private_bytes(secret_key_bytes)
signature_bytes = secret_key.sign(request_string)
signature = signature_bytes.hex()

url = "https://coinswitch.co" + endpoint

headers = {
  'Content-Type': 'application/json',
  'X-AUTH-SIGNATURE': signature,
  'X-AUTH-APIKEY': api_key
}

response = requests.request("GET", url, headers=headers, json=payload)

print(response.status_code)
print(response.text)