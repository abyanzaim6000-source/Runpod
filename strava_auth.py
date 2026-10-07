import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8282/callback"
SCOPE = "activity:write,read"

auth_code_holder = {}

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if "code" in params:
            auth_code_holder["code"] = params["code"][0]
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorized! You can close this tab and return to the terminal.</h1>")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"<h1>Something went wrong. No code received.</h1>")

    def log_message(self, format, *args):
        pass  # suppress default server logging

def get_authorization_code():
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&approval_prompt=force"
        f"&scope={SCOPE}"
    )
    print("Opening browser for Strava authorization...")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8282), CallbackHandler)
    server.handle_request()  # handles exactly one request, then stops

    return auth_code_holder.get("code")

def exchange_code_for_token(code):
    response = requests.post(
        url="https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
        },
    )
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    code = get_authorization_code()
    if not code:
        print("Authorization failed — no code received.")
    else:
        token_data = exchange_code_for_token(code)
        print("SUCCESS. Token data received:")
        print(f"  Access Token: {token_data['access_token'][:8]}... (truncated)")
        print(f"  Refresh Token: {token_data['refresh_token'][:8]}... (truncated)")
        print(f"  Expires At: {token_data['expires_at']}")
        print(f"  Scope granted: {SCOPE}")

        # Save tokens to .env for reuse (append-safe overwrite of these two keys)
        with open(".env", "a") as f:
            f.write(f"\nSTRAVA_ACCESS_TOKEN={token_data['access_token']}")
            f.write(f"\nSTRAVA_REFRESH_TOKEN={token_data['refresh_token']}")
        print("Tokens appended to .env")