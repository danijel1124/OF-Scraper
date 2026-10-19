"""
End-to-end check of the 403 -> url refresh -> resume path.

Runs the normal ofscraper CLI, but the first download request of the given
media is sent to an invalid signed url (the link from user_data.db with a
corrupted Signature, which CloudFront answers with the same 403 AccessDenied
as a url bound to an old IP). Expected: one 403, url refresh, then resume of the
existing .part with a 206.

usage: PYTHONPATH=<clone> <pipx-venv>/bin/python tools/stale_url_e2e.py \
           <user_data.db> <media_id> -- <ofscraper args...>
"""
import sqlite3
import sys
import urllib.parse

db, media_id = sys.argv[1], int(sys.argv[2])
sys.argv = ["ofscraper"] + sys.argv[sys.argv.index("--") + 1 :]

(link,) = sqlite3.connect(db).execute(
    "select link from medias where media_id=?", (media_id,)
).fetchone()
parts = urllib.parse.urlsplit(link)
query = urllib.parse.parse_qs(parts.query)
query["Signature"] = ["A" + query["Signature"][0][1:]]
stale_link = parts._replace(query=urllib.parse.urlencode(query, doseq=True)).geturl()

import ofscraper.main.open.load as load
from ofscraper.commands.scraper.actions.download.managers.main_download import (
    MainDownloadManager,
)

orig = MainDownloadManager._send_req_inner
injected = False


async def patched(self, c, ele, *args, **kwargs):
    global injected
    if not injected and int(ele.id) == media_id:
        injected = True
        ele.url = stale_link
    return await orig(self, c, ele, *args, **kwargs)


MainDownloadManager._send_req_inner = patched
load.main()
