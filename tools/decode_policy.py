"""
Print expiry and IP binding of OnlyFans CDN signed urls (CloudFront policy).
usage: echo '<url>' | python3 tools/decode_policy.py
   or: sqlite3 <user_data.db> "select link from medias where media_id=..." | python3 tools/decode_policy.py
"""
import base64
import datetime
import json
import sys
import urllib.parse

for url in sys.stdin.read().split():
    query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
    if "Policy" not in query:
        print("no Policy:", url[:80])
        continue
    policy = query["Policy"][0].replace("-", "+").replace("_", "=").replace("~", "/")
    cond = json.loads(base64.b64decode(policy + "=="))["Statement"][0]["Condition"]
    expiry = datetime.datetime.fromtimestamp(cond["DateLessThan"]["AWS:EpochTime"])
    ip = cond.get("IpAddress", {}).get("AWS:SourceIp", "-")
    print(f"expires {expiry}  ip {ip}")
