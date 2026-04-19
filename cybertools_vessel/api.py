import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from . import config as cfg


def _get(path: str) -> dict:
    base = cfg.get("api_url", "https://www.cyber-tools.dev").rstrip("/")
    url  = base + path
    timeout = int(cfg.get("timeout", 60))
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    req = urllib.request.Request(
        url, headers={"User-Agent": "cybtl/2.0 (cybertools-vessel)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        try:
            return {"error": json.loads(e.read()).get("detail", str(e))}
        except Exception:
            return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


def _post(path: str, body: dict) -> dict:
    base = cfg.get("api_url", "https://www.cyber-tools.dev").rstrip("/")
    url  = base + path
    timeout = int(cfg.get("timeout", 60))
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE
    data = json.dumps(body).encode()
    req  = urllib.request.Request(
        url, data=data,
        headers={"User-Agent": "cybtl/2.0", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        try:
            return {"error": json.loads(e.read()).get("detail", str(e))}
        except Exception:
            return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


# ── Endpoints ─────────────────────────────────────────────────────────────────

def recon(domain: str)     -> dict: return _get(f"/recon?domain={urllib.parse.quote(domain)}")
def analyze(url: str)      -> dict: return _get(f"/analyze-url?url={urllib.parse.quote(url)}")
def bb_scan(url: str)      -> dict: return _get(f"/bb-scan?url={urllib.parse.quote(url)}")
def expand(domain: str)    -> dict: return _get(f"/expand?domain={urllib.parse.quote(domain)}")
def endpoints(url: str)    -> dict: return _get(f"/endpoints?url={urllib.parse.quote(url)}")
def params(url: str)       -> dict: return _get(f"/params?url={urllib.parse.quote(url)}")
def workflow(target: str)  -> dict: return _get(f"/workflow?target={urllib.parse.quote(target)}")
def payloads(ptype: str)   -> dict: return _get(f"/payloads?type={urllib.parse.quote(ptype)}")
def last_scan()            -> dict: return _get("/last-scan")
def cache_status()         -> dict: return _get("/workflows/cache/status")

def workflow_express(t: str)    -> dict: return _get(f"/workflows/express?target={urllib.parse.quote(t)}")
def workflow_bugbounty(t: str)  -> dict: return _get(f"/workflows/bugbounty?target={urllib.parse.quote(t)}")
def workflow_subdomains(d: str) -> dict: return _get(f"/workflows/subdomains?domain={urllib.parse.quote(d)}")
def workflow_api(url: str)      -> dict: return _get(f"/workflows/api?url={urllib.parse.quote(url)}")

def hash_text(algo: str, text: str) -> dict:
    return _get(f"/hash/{urllib.parse.quote(algo)}/{urllib.parse.quote(text)}")

def encode(method: str, text: str) -> dict:
    return _get(f"/encode/{urllib.parse.quote(method)}/{urllib.parse.quote(text)}")

def ip_info(ip: str) -> dict:
    return _get(f"/ip/{urllib.parse.quote(ip)}")

def password_analyze(pw: str) -> dict:
    return _post("/password/analyze", {"password": pw})

def chat(question: str, history: list) -> dict:
    history_with_q = history + [{"role": "user", "content": question}]
    return _post("/api/chat", {"messages": history_with_q})
