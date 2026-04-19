
"""
cybtl — CyberTools Vessel v2.0
Global CLI for CyberTools API

Usage:
  cybtl                           Interactive menu
  cybtl recon <domain>
  cybtl analyze <url>
  cybtl scan <url>
  cybtl expand <domain>
  cybtl endpoints <url>
  cybtl params <url>
  cybtl workflow <target>
  cybtl express <target>
  cybtl bugbounty <target>
  cybtl subdomains <domain>
  cybtl apiscan <url>
  cybtl payloads <type>
  cybtl hash <algo> <text>
  cybtl encode <method> <text>
  cybtl ip <address>
  cybtl password <pw>
  cybtl last
  cybtl cache
  cybtl config
  cybtl set <key> <value>

Flags:
  --json          Raw JSON output
  --save <file>   Save JSON to file
"""

import sys
import os
import json
import time
import shutil

from . import __version__, __url__
from . import config as cfg
from . import api


# ── ANSI colours ──────────────────────────────────────────────────────────────
R    = "\033[0m"
BOLD = "\033[1m"
DIM  = "\033[2m"
CYAN = "\033[96m"
BCYAN= "\033[1;96m"
GRN  = "\033[92m"
YEL  = "\033[93m"
RED  = "\033[91m"
MAG  = "\033[95m"
ORG  = "\033[38;5;208m"   # orange — missing headers
WHT  = "\033[97m"

def c(text, col): return f"{col}{text}{R}"
def ok(t):        return c(t, GRN)
def bad(t):       return c(t, RED)
def warn(t):      return c(t, YEL)
def miss(t):      return c(t, ORG)
def dim(t):       return c(t, DIM)
def bold(t):      return c(t, BOLD)
def cyan(t):      return c(t, CYAN)
def bcyan(t):     return c(t, BCYAN)
def mag(t):       return c(t, MAG)


# ── ASCII art header ───────

BANNER = f"""{BCYAN}
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ████████╗ ██████╗  ██████╗ ██╗     ███████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝   ██║   ██║   ██║██║   ██║██║     ███████╗
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗   ██║   ██║   ██║██║   ██║██║     ╚════██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗███████║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝{R}
{DIM}  CyberTools Vessel · Global CLI · v{__version__}{R}
{DIM}  {__url__}{R}
"""

DIVIDER = c("─" * 58, DIM)

MENU_ITEMS = [
    ("0", RED,  "✗",  "Exit"),
    ("1", CYAN, "◎",  "Recon                <domain>"),
    ("2", CYAN, "⟳",  "Analyze URL          <url>"),
    ("3", CYAN, "◈",  "BB Scan              <url>"),
    ("4", CYAN, "⊞",  "Expand Subdomains    <domain>"),
    ("5", CYAN, "⊡",  "Endpoints            <url>"),
    ("6", CYAN, "⊟",  "Params               <url>"),
    ("7", YEL,  "⚡", "Full Workflow        <target>"),
    ("8", YEL,  "🚀", "Express Workflow     <target>"),
    ("9", YEL,  "◉",  "Bug Bounty Workflow  <target>"),
    ("10", YEL, "⊹",  "Subdomains Workflow  <domain>"),
    ("11", YEL, "⊠",  "API Scan Workflow    <url>"),
    ("12", MAG, "◇",  "Payloads             <xss|sqli|lfi|ssrf|idor|open_redirect>"),
    ("13", MAG, "⌗",  "Hash                 <algo> <text>"),
    ("14", MAG, "⊛",  "Encode               <base64|hex|url> <text>"),
    ("15", MAG, "⊙",  "IP Info              <address|me>"),
    ("16", MAG, "🔑", "Password Analyze     <password>"),
    ("17", DIM, "⊚",  "Last Scan"),
    ("18", DIM, "🗃",  "Cache Status"),
    ("19", GRN, "⚙",  "Show Config"),
    ("20", GRN, "✎",  "Set Config           <key> <value>"),
]


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    print(BANNER)


def print_config_box():
    conf = cfg.load()
    api_url = conf.get("api_url", "?")
    timeout = conf.get("timeout", 60)
    print(DIVIDER)
    print(f"  {dim('API URL  ')} {cyan(api_url)}")
    print(f"  {dim('Timeout  ')} {cyan(str(timeout)+'s')}")
    print(f"  {dim('Config   ')} {dim(str(cfg.CONFIG_FILE))}")
    print(DIVIDER)


def print_menu():
    print(f"\n  {bold('Available Options:')}\n")
    left  = MENU_ITEMS[:11]
    right = MENU_ITEMS[11:]
    max_left = max(len(n) for n, *_ in left)
    for i, (left_item, right_item) in enumerate(zip(left, right + [None] * max(0, len(left)-len(right)))):
        n, col, icon, label = left_item
        lhs = f"  {c(n+'.', col):>6}  {c(icon, col)} {label}"
        if right_item:
            rn, rc, ri, rl = right_item
            rhs = f"  {c(rn+'.', rc):>7}  {c(ri, rc)} {rl}"
        else:
            rhs = ""
        print(f"{lhs:<52}{rhs}")
    print()


def prompt_input(label: str) -> str:
    try:
        return input(f"  {cyan('▸')} {label}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print()
        return ""


def print_result(data: dict, raw: bool = False, save_path: str = None):
    if raw:
        print(json.dumps(data, indent=2))
        return
    if save_path:
        with open(save_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n  {ok('✓')} Saved to {cyan(save_path)}\n")
        return

    if "error" in data:
        print(f"\n  {bad('✗')} {data['error']}\n")
        return

    _render(data)


def _render(data: dict):
    """Pretty-print API response recursively."""
    print()
    _print_section("RESULT", data)


def _print_section(title: str, data: dict, indent: int = 2):
    pad = " " * indent
    print(f"{pad}{cyan('◉')} {bold(title)}")
    for k, v in data.items():
        if isinstance(v, dict):
            print(f"{pad}  {dim(k+':')}")
            _print_section(k.upper(), v, indent + 4)
        elif isinstance(v, list):
            if not v:
                continue
            print(f"{pad}  {dim(k+':')} {_format_list(v, indent + 4)}")
        else:
            color = GRN if k in ("ip", "domain", "valid") else WHT
            print(f"{pad}  {dim(k+':')} {c(str(v), color)}")


def _format_list(items: list, indent: int) -> str:
    if not items:
        return dim("[]")
    if all(isinstance(i, str) for i in items):
        if len(items) <= 3:
            return ", ".join(items)

        pad = "\n" + " " * indent + "  "
        joined = pad.join(f"{c('›', CYAN)} {i}" for i in items)
        return f"\n{' '*indent}  {joined}"
    
    pad = " " * indent
    lines = []
    for item in items:
        if isinstance(item, dict):
            parts = []
            for k, v in item.items():
                if k == "status":
                    col = GRN if v == 200 else YEL if isinstance(v, int) and v < 400 else RED
                    parts.append(c(str(v), col))
                elif k == "risk":
                    col = RED if v == "high" else YEL if v == "medium" else GRN
                    parts.append(c(f"[{v}]", col))
                elif k in ("payload", "subdomain", "path", "name"):
                    parts.append(c(str(v), CYAN))
                else:
                    parts.append(dim(f"{k}={v}"))
            lines.append(f"\n{pad}  " + "  ".join(parts))
        else:
            lines.append(f"\n{pad}  {c('›', CYAN)} {item}")
    return "".join(lines)


def _print_smart(data: dict):
    """Print smart_summary and next_steps from any result."""
    summary = data.get("smart_summary", [])
    steps   = data.get("next_steps", [])

    if summary:
        print(f"\n  {bold(cyan('SMART SUMMARY'))}")
        print(DIVIDER)
        for line in summary:
            print(f"  {cyan('›')} {line}")

    if steps:
        print(f"\n  {bold(cyan('NEXT STEPS'))}")
        print(DIVIDER)
        for i, step in enumerate(steps, 1):
            num = c(f"{i}.", YEL)
            print(f"  {num} {step}")
    print()


# ── Command handlers ───────────

def cmd_recon(args, raw=False, save=None):
    domain = args[0] if args else prompt_input("Domain")
    if not domain: return
    print(f"\n  {dim('Resolving IP, DNS, SSL...')}")
    d = api.recon(domain)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_recon(d)

def _print_recon(d: dict):
    if "error" in d: print(f"\n  {bad('✗')} {d['error']}"); return
    print(f"\n  {bold(cyan('HOST INFO'))}")
    print(DIVIDER)
    print(f"  {dim('Domain   ')} {cyan(d.get('domain',''))}")
    print(f"  {dim('IP       ')} {ok(d.get('ip','—'))}")
    print(f"  {dim('Protocol ')} {d.get('protocol','').upper()}")
    sc = d.get('status_code')
    scol = GRN if sc and sc < 400 else RED
    print(f"  {dim('Status   ')} {c(str(sc or '—'), scol)}")

    ssl_d = d.get('ssl', {})
    if ssl_d:
        print(f"\n  {bold(cyan('SSL'))}")
        print(DIVIDER)
        print(f"  {dim('Valid    ')} {ok('Yes') if ssl_d.get('valid') else bad('No')}")
        print(f"  {dim('Expires  ')} {ssl_d.get('expires','—')}")
        days = ssl_d.get('days_remaining')
        print(f"  {dim('Days     ')} {(ok if days and days>30 else bad)(str(days or '—'))}")
        print(f"  {dim('Issuer   ')} {ssl_d.get('issuer','—')}")

    dns_d = d.get('dns', {})
    if dns_d:
        print(f"\n  {bold(cyan('DNS RECORDS'))}")
        print(DIVIDER)
        for rtype, records in dns_d.items():
            print(f"  {dim(rtype+' '):<16} {', '.join(str(r) for r in records[:3])}")

    missing = d.get('missing_security_headers', [])
    if missing:
        print(f"\n  {bold(ORG+'MISSING SECURITY HEADERS'+R)}")
        print(DIVIDER)
        for h in missing:
            print(f"  {miss('⊘')} {miss(h)}")
    else:
        print(f"\n  {ok('✓')} All major security headers present.")

    tech = d.get('tech_hints', [])
    if tech:
        print(f"\n  {bold(cyan('TECH STACK'))}")
        print(DIVIDER)
        for t in tech:
            print(f"  {warn('●')} {t}")

    _print_smart(d)


def cmd_analyze(args, raw=False, save=None):
    url = args[0] if args else prompt_input("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    print(f"\n  {dim('Following redirects...')}")
    d = api.analyze(url)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_analyze(d)

def _print_analyze(d: dict):
    if "error" in d: print(f"\n  {bad('✗')} {d['error']}"); return
    print(f"\n  {bold(cyan('REDIRECT CHAIN'))}")
    print(DIVIDER)
    for hop in d.get("redirect_chain", []):
        sc = hop["status"]
        col = GRN if sc < 300 else YEL if sc < 400 else RED
        print(f"  {c(str(sc), col)} {dim('→')} {hop['url']}")
    misconf = d.get("misconfig_hints", [])
    if misconf:
        print(f"\n  {bold(RED+'MISCONFIGURATIONS'+R)}")
        print(DIVIDER)
        for h in misconf:
            print(f"  {bad('✗')} {h}")
    else:
        print(f"\n  {ok('✓')} No obvious misconfigurations found.")
    _print_smart(d)


def cmd_scan(args, raw=False, save=None):
    url = args[0] if args else prompt_input("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    print(f"\n  {dim('Probing paths concurrently (~3-5s)...')}")
    d = api.bb_scan(url)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_scan(d)

def _print_scan(d: dict):
    if "error" in d: print(f"\n  {bad('✗')} {d['error']}"); return
    found = d.get("interesting_paths", [])
    print(f"\n  {bold(cyan(f'INTERESTING PATHS ({len(found)})'))} ")
    print(DIVIDER)
    for p in found:
        sc = p["status"]
        col = GRN if sc == 200 else YEL if str(sc).startswith("3") else RED
        print(f"  {c(str(sc), col):>6}  {p['path']}")
    if not found:
        print(f"  {dim('No interesting paths found.')}")
    hints = d.get("bug_bounty_hints", [])
    if hints:
        print(f"\n  {bold(cyan('BUG BOUNTY HINTS'))}")
        print(DIVIDER)
        for h in hints:
            col = RED if "CRITICAL" in h or "HIGH" in h else YEL if "INFO" in h else CYAN
            print(f"  {c('›', col)} {h}")
    _print_smart(d)


def cmd_expand(args, raw=False, save=None):
    domain = args[0] if args else prompt_input("Domain")
    if not domain: return
    print(f"\n  {dim('Querying crt.sh, hackertarget, SSL SAN...')}")
    d = api.expand(domain)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_expand(d)

def _print_expand(d: dict):
    if "error" in d: print(f"\n  {bad('✗')} {d['error']}"); return
    subs = d.get("subdomains", [])
    live = [s for s in subs if s.get("live")]
    dead = [s for s in subs if not s.get("live")]
    print(f"\n  {bold(cyan(f'LIVE SUBDOMAINS ({len(live)})'))} {dim('via '+ ', '.join(d.get('sources',[])))}")
    print(DIVIDER)
    for s in live:
        print(f"  {ok('●')} {cyan(s['subdomain'])} {dim(s.get('ip',''))}")
    if dead:
        print(f"\n  {dim(f'Non-resolving: {len(dead)}')}")
        for s in dead[:6]:
            print(f"  {bad('○')} {dim(s['subdomain'])}")
    _print_smart(d)


def cmd_endpoints(args, raw=False, save=None):
    url = args[0] if args else prompt_input("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    print(f"\n  {dim('Probing 60+ paths...')}")
    d = api.endpoints(url)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_endpoints(d)

def _print_endpoints(d: dict):
    if "error" in d: print(f"\n  {bad('✗')} {d['error']}"); return
    eps = d.get("endpoints", [])
    type_col = {"sensitive": RED, "admin": RED, "api": GRN, "auth": YEL, "monitoring": YEL, "other": DIM}
    print(f"\n  {bold(cyan(f'FOUND ENDPOINTS ({len(eps)})'))} {dim('of '+ str(d.get('paths_probed',0)) +' probed')}")
    print(DIVIDER)
    for ep in eps:
        col = type_col.get(ep.get("type","other"), DIM)
        sc  = ep["status"]
        scol = GRN if sc == 200 else YEL if sc < 400 else RED
        print(f"  {c('['+ep.get('type','?')+']', col):<22} {ep['path']:<35} {c(str(sc), scol)}")
    _print_smart(d)


def cmd_params(args, raw=False, save=None):
    url = args[0] if args else prompt_input("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    print(f"\n  {dim('Probing 26 common parameters...')}")
    d = api.params(url)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_params(d)

def _print_params(d: dict):
    if "error" in d: print(f"\n  {bad('✗')} {d['error']}"); return
    interesting = d.get("interesting", [])
    high_risk   = d.get("high_risk", [])
    print(f"\n  {bold(cyan(f'INTERESTING PARAMETERS ({len(interesting)})'))} {dim('tested: '+str(d.get('params_tested',0)))}")
    print(DIVIDER)
    for p in interesting:
        rc = RED if p["risk"] == "high" else YEL if p["risk"] == "medium" else GRN
        print(f"  {c('['+p['risk']+']', rc):<18} {cyan('?'+p['name']+'=FUZZ')}")
        print(f"  {dim('   ↳ '+p['test'])}")
    if not interesting:
        print(f"  {dim('No clearly injectable params found.')}")
    _print_smart(d)


def cmd_workflow(args, raw=False, save=None, mode="full"):
    target = args[0] if args else prompt_input("Target")
    if not target: return
    funcs = {
        "full":       api.workflow,
        "express":    api.workflow_express,
        "bugbounty":  api.workflow_bugbounty,
        "subdomains": api.workflow_subdomains,
        "api":        api.workflow_api,
    }
    fn = funcs.get(mode, api.workflow)
    print(f"\n  {dim('Running pipeline...')}")
    d = fn(target) if mode != "api" else fn(target if target.startswith("http") else "https://"+target)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_workflow(d)

def _print_workflow(d: dict):
    if "error" in d: print(f"\n  {bad('✗')} {d['error']}"); return
    elapsed = d.get("elapsed_seconds", "?")
    print(f"\n  {bold(cyan('WORKFLOW COMPLETE'))} {dim(f'({elapsed}s)')}")
    print(DIVIDER)
    recon = d.get("recon", {})
    if recon.get("ip"):
        print(f"  {dim('IP       ')} {ok(recon['ip'])}")
        print(f"  {dim('Status   ')} {recon.get('status_code','—')}")
    paths = d.get("bb_scan", {}).get("interesting_paths", [])
    if paths:
        print(f"\n  {bold(cyan(f'PATHS ({len(paths)})'))} ")
        print(DIVIDER)
        for p in paths[:8]:
            sc = p["status"]
            col = GRN if sc == 200 else YEL if str(sc).startswith("3") else RED
            print(f"  {c(str(sc), col):>6}  {p['path']}")
    eps = d.get("endpoints", {}).get("endpoints", [])
    if eps:
        print(f"\n  {bold(cyan(f'ENDPOINTS ({len(eps)})'))} ")
        print(DIVIDER)
        for ep in eps[:6]:
            print(f"  {cyan('['+ep.get('type','?')+']'):<20} {ep['path']} → {ep['status']}")
    iparams = d.get("params", {}).get("interesting", [])
    if iparams:
        print(f"\n  {bold(RED+f'INJECTABLE PARAMS ({len(iparams)})'+R)}")
        print(DIVIDER)
        for p in iparams[:5]:
            rc = RED if p["risk"]=="high" else YEL
            print(f"  {c('!', rc)} {cyan('?'+p['name']+'=')} {dim(p['test'])}")
    _print_smart(d)


def cmd_payloads(args, raw=False, save=None):
    ptype = args[0] if args else prompt_input("Type (xss/sqli/lfi/ssrf/idor/open_redirect)")
    if not ptype: return
    d = api.payloads(ptype)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_payloads(d)

def _print_payloads(d: dict):
    if "error" in d: print(f"\n  {bad('✗')} {d['error']}"); return
    print(f"\n  {bold(cyan(d.get('type','').upper()+' PAYLOADS'))} {dim('('+str(d.get('count',0))+' total)')}")
    print(DIVIDER)
    print(f"  {dim(d.get('description',''))}\n")
    for p in d.get("payloads", []):
        ctx   = p.get("context", "")
        label = p.get("label", "")
        ctxl  = warn(f"[{ctx}]") if ctx else ""
        print(f"  {cyan(p['payload'])}  {dim(label)} {ctxl}")
    tips = d.get("usage_tips", [])
    if tips:
        print(f"\n  {bold(YEL+'USAGE TIPS'+R)}")
        for i, tip in enumerate(tips, 1):
            print(f"  {warn(str(i)+'.')} {tip}")
    print()


def cmd_hash(args, raw=False, save=None):
    if len(args) >= 2:
        algo, text = args[0], args[1]
    else:
        algo = prompt_input("Algorithm (sha256/md5/...)")
        text = prompt_input("Text")
    if not algo or not text: return
    d = api.hash_text(algo, text)
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d: print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(f"\n  {dim('Hash')} ({d.get('algorithm','')})\n  {cyan(d.get('hash',''))}\n")


def cmd_encode(args, raw=False, save=None):
    if len(args) >= 2:
        method, text = args[0], " ".join(args[1:])
    else:
        method = prompt_input("Method (base64/hex/url)")
        text   = prompt_input("Text")
    if not method or not text: return
    d = api.encode(method, text)
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d: print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(f"\n  {cyan(d.get('encoded',''))}\n")


def cmd_ip(args, raw=False, save=None):
    addr = args[0] if args else prompt_input("IP address (or 'me')")
    if not addr: return
    d = api.ip_info(addr)
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d: print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(f"\n  {bold(cyan('IP INFO'))}")
            print(DIVIDER)
            for k, v in d.items():
                print(f"  {dim(k+':')} {cyan(str(v))}")
            print()


def cmd_password(args, raw=False, save=None):
    pw = " ".join(args) if args else prompt_input("Password (for strength analysis)")
    if not pw: return
    d = api.password_analyze(pw)
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d: print(f"\n  {bad('✗')} {d['error']}")
        else:
            strength = d.get("strength","")
            scol = GRN if "Strong" in strength else YEL if "Moderate" in strength else RED
            print(f"\n  {bold('Strength:')} {c(strength, scol)}")
            print(f"  {dim('Score   ')} {d.get('score')}/{d.get('max_score')}")
            print(f"  {dim('Entropy ')} {d.get('entropy_estimate_bits')} bits")
            for fb in d.get("feedback", []):
                print(f"  {warn('⚠')} {fb}")
            print()


def cmd_last(raw=False, save=None):
    d = api.last_scan()
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d: print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(f"\n  {bold(cyan('LAST SCAN'))}")
            print(DIVIDER)
            print(f"  {dim('Target    ')} {cyan(d.get('key',''))}")
            print(f"  {dim('Timestamp ')} {d.get('timestamp','')}")
            summary = (d.get("data") or {}).get("smart_summary", [])
            for s in summary[:8]:
                print(f"  {cyan('›')} {s}")
            print()


def cmd_cache(raw=False, save=None):
    d = api.cache_status()
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d: print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(f"\n  {bold(cyan('CACHE STATUS'))}")
            print(DIVIDER)
            print(f"  {dim('Active   ')} {ok(str(d.get('active_entries',0)))}")
            print(f"  {dim('Expired  ')} {warn(str(d.get('expired_entries',0)))}")
            print(f"  {dim('Total    ')} {d.get('total_entries',0)}")
            print()


def cmd_config_show():
    print(f"\n  {bold(cyan('CURRENT CONFIG'))}")
    print(DIVIDER)
    print(cfg.show())
    print(f"\n  {dim('File: '+ str(cfg.CONFIG_FILE))}\n")


def cmd_config_set(args):
    if len(args) >= 2:
        key, val = args[0], " ".join(args[1:])
    else:
        key = prompt_input("Key (api_url / timeout / save_dir)")
        val = prompt_input("Value")
    if not key or not val: return
    cfg.set_key(key, val)
    print(f"\n  {ok('✓')} {key} = {cyan(val)}\n")


# ── Output helpers ──────────

def _handle_output(data: dict, raw: bool, save_path: str):
    if raw:
        print(json.dumps(data, indent=2))
    elif save_path:
        with open(save_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n  {ok('✓')} Saved to {cyan(save_path)}\n")


# ── Interactive menu ─────

MENU_DISPATCH = {
    "1":  lambda a,r,s: cmd_recon(a,r,s),
    "2":  lambda a,r,s: cmd_analyze(a,r,s),
    "3":  lambda a,r,s: cmd_scan(a,r,s),
    "4":  lambda a,r,s: cmd_expand(a,r,s),
    "5":  lambda a,r,s: cmd_endpoints(a,r,s),
    "6":  lambda a,r,s: cmd_params(a,r,s),
    "7":  lambda a,r,s: cmd_workflow(a,r,s,mode="full"),
    "8":  lambda a,r,s: cmd_workflow(a,r,s,mode="express"),
    "9":  lambda a,r,s: cmd_workflow(a,r,s,mode="bugbounty"),
    "10": lambda a,r,s: cmd_workflow(a,r,s,mode="subdomains"),
    "11": lambda a,r,s: cmd_workflow(a,r,s,mode="api"),
    "12": lambda a,r,s: cmd_payloads(a,r,s),
    "13": lambda a,r,s: cmd_hash(a,r,s),
    "14": lambda a,r,s: cmd_encode(a,r,s),
    "15": lambda a,r,s: cmd_ip(a,r,s),
    "16": lambda a,r,s: cmd_password(a,r,s),
    "17": lambda a,r,s: cmd_last(r,s),
    "18": lambda a,r,s: cmd_cache(r,s),
    "19": lambda a,r,s: cmd_config_show(),
    "20": lambda a,r,s: cmd_config_set(a),
}

CMD_NAME_DISPATCH = {
    "recon":      ("1", []),
    "analyze":    ("2", []),
    "scan":       ("3", []),
    "expand":     ("4", []),
    "endpoints":  ("5", []),
    "params":     ("6", []),
    "workflow":   ("7", []),
    "express":    ("8", []),
    "bugbounty":  ("9", []),
    "subdomains": ("10", []),
    "apiscan":    ("11", []),
    "payloads":   ("12", []),
    "hash":       ("13", []),
    "encode":     ("14", []),
    "ip":         ("15", []),
    "password":   ("16", []),
    "last":       ("17", []),
    "cache":      ("18", []),
    "config":     ("19", []),
    "set":        ("20", []),
}


def interactive_loop():
    """Main interactive TUI loop."""
    clear_screen()
    print_banner()
    print_config_box()

    while True:
        print_menu()
        try:
            choice = input(f"  {c('▸', CYAN)} Please enter your choice (0-20): ").strip()
        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {dim('Goodbye. Stay stealthy.')}\n")
            break

        if choice == "0":
            print(f"\n  {dim('Goodbye. Stay stealthy.')}\n")
            break

        if choice not in MENU_DISPATCH:
            print(f"\n  {bad('Invalid choice.')} Enter a number 0-20.\n")
            continue

        try:
            MENU_DISPATCH[choice]([], False, None)
        except Exception as e:
            print(f"\n  {bad('Error:')} {e}\n")

        input(f"  {dim('Press Enter to continue...')}")
        clear_screen()
        print_banner()
        print_config_box()


# ── Entry point ──────

USAGE = f"""
{bcyan('⌖ cybtl')} {dim('— CyberTools Vessel v'+__version__)}

{warn('Direct usage:')}
  cybtl recon     <domain>         Full host recon
  cybtl analyze   <url>            URL redirect + header analysis
  cybtl scan      <url>            Bug bounty path scan
  cybtl expand    <domain>         Passive subdomain enumeration
  cybtl endpoints <url>            60+ endpoint probe
  cybtl params    <url>            Injectable param detection
  cybtl workflow  <target>         Full 5-stage pipeline
  cybtl express   <target>         Fast: recon + analyze
  cybtl bugbounty <target>         Recon + scan + payloads
  cybtl subdomains <domain>        Subdomain workflow
  cybtl apiscan   <url>            API endpoint + param workflow
  cybtl payloads  <type>           xss|sqli|lfi|ssrf|idor|open_redirect
  cybtl hash      <algo> <text>    Hash a string
  cybtl encode    <method> <text>  base64|hex|url
  cybtl ip        <address|me>     IP geolocation
  cybtl password  <pw>             Password strength
  cybtl last                       Last scan result
  cybtl cache                      Cache status
  cybtl config                     Show config
  cybtl set       <key> <value>    Set config value

{warn('Flags:')}
  --json          Raw JSON output
  --save <file>   Save JSON to file

{warn('Interactive mode:')}
  cybtl           Launch full TUI menu

{warn('API URL:')} {dim(cfg.get('api_url','https://www.cyber-tools.dev'))}
"""


def main():
    args = sys.argv[1:]

    if not args:
        interactive_loop()
        return

    if args[0] in ("-h", "--help", "help"):
        print(USAGE)
        return

    # Parse flags
    raw  = "--json" in args
    args = [a for a in args if a != "--json"]

    save = None
    if "--save" in args:
        idx  = args.index("--save")
        save = args[idx + 1] if idx + 1 < len(args) else None
        args = [a for i, a in enumerate(args) if i != idx and i != idx + 1]

    cmd  = args[0].lower()
    rest = args[1:]

    if cmd not in CMD_NAME_DISPATCH:
        print(f"\n  {bad('Unknown command:')} {cmd}")
        print(USAGE)
        sys.exit(1)

    menu_key, _ = CMD_NAME_DISPATCH[cmd]
    try:
        MENU_DISPATCH[menu_key](rest, raw, save)
    except Exception as e:
        print(f"\n  {bad('Error:')} {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
