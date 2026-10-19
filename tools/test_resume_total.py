"""Unit checks for MainDownloadManager._full_total_from_response.
usage: <pipx-venv>/bin/python tools/test_resume_total.py <clone>"""
import sys, pathlib, tempfile, types
sys.path.insert(0, sys.argv[1]); sys.argv = ["ofscraper"]
import ofscraper.main.open.load
import ofscraper.commands.scraper.actions.utils.globals as g
import logging; g.log = logging.getLogger("t")
from ofscraper.commands.scraper.actions.download.managers.main_download import MainDownloadManager
m = MainDownloadManager()
d = tempfile.mkdtemp(); part = pathlib.Path(d, "x.part")
th = types.SimpleNamespace(tempfilepath=str(part))
def resp(status, cl, cr=None):
    h = {"content-length": str(cl)}
    if cr: h["content-range"] = cr
    return types.SimpleNamespace(status=status, headers=h)
part.write_bytes(b"a"*1000)
assert m._full_total_from_response(resp(206, 1000, "bytes 1000-1999/2000"), 1000, th) == (2000, 1000) and part.exists()
assert m._full_total_from_response(resp(206, 1000, "bytes 1000-1999/*"), 1000, th) == (2000, 1000)
assert m._full_total_from_response(resp(200, 2000), 1000, th) == (2000, 0) and not part.exists()
part.write_bytes(b"a"*1000)
try: m._full_total_from_response(resp(206, 500, "bytes 1500-1999/2000"), 1000, th); raise SystemExit("no raise")
except Exception as e: assert "resumed at byte" in str(e) and not part.exists()
assert m._full_total_from_response(resp(200, 2000), 0, th) == (2000, 0)
print("RESUME_TESTS_OK")
