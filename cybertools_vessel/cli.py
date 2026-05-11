"""
cybtl — CyberTools Vessel v1.1.0
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

Keyboard shortcuts (interactive mode):
  Ctrl+Q / 0      Exit to shell
  ?               Show command help overlay
"""

import sys
import os
import json
import time
import signal
import datetime

from . import __version__, __url__
from . import config as cfg
from . import api

# --- Terminal capability detection ---


def _get_term_width():
    try:
        return os.get_terminal_size().columns
    except Exception:
        return 80


# --- ANSI colours ---

R = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITAL = "\033[3m"
UND = "\033[4m"
BLINK = "\033[5m"
REV = "\033[7m"
CYAN = "\033[96m"
BCYAN = "\033[1;96m"
GRN = "\033[92m"
YEL = "\033[93m"
RED = "\033[91m"
BRED = "\033[1;91m"
MAG = "\033[95m"
BLU = "\033[94m"
ORG = "\033[38;5;208m"
WHT = "\033[97m"
DGRY = "\033[38;5;153m"  # pastel sky-blue — vivid on transparent bg
GRY = "\033[38;5;195m"  # alice-blue — near-white, always readable

# Background colours
BG_RED = "\033[41m"
BG_BLK = "\033[40m"
BG_DGRY = "\033[48;5;235m"


def c(text, col):
    return f"{col}{text}{R}"


def ok(t):
    return c(t, GRN)


def bad(t):
    return c(t, RED)


def warn(t):
    return c(t, YEL)


def miss(t):
    return c(t, ORG)


def dim(t):
    return c(t, DIM)


def bold(t):
    return c(t, BOLD)


def cyan(t):
    return c(t, CYAN)


def bcyan(t):
    return c(t, BCYAN)


def mag(t):
    return c(t, MAG)


def gry(t):
    return c(t, GRY)


def dgry(t):
    return c(t, DGRY)


# --- Session state ---

_session_start = datetime.datetime.now()
_session_cmds = 0
_session_last_cmd = None


def _session_info() -> str:
    elapsed = datetime.datetime.now() - _session_start
    secs = int(elapsed.total_seconds())
    mins, s = divmod(secs, 60)
    t_str = f"{mins}m{s:02d}s" if mins else f"{s}s"
    return t_str


# --- Ctrl+Q setup ---

_ctrl_q_exit = False


def _setup_ctrl_q():
    """Bind Ctrl+Q to exit: disable IXON flow-control, then map via readline."""

    try:
        import termios

        fd = sys.stdin.fileno()
        attrs = termios.tcgetattr(fd)
        attrs[0] &= ~termios.IXON
        termios.tcsetattr(fd, termios.TCSADRAIN, attrs)
    except Exception:
        pass

    # Bind Ctrl+Q to type "0" + newline (our "Exit" menu choice)
    try:
        import readline

        readline.parse_and_bind(r'Control-q: "0\n"')
    except Exception:
        pass


def _restore_ixon():
    """Restore XON/XOFF on exit (good practice)."""
    try:
        import termios

        fd = sys.stdin.fileno()
        attrs = termios.tcgetattr(fd)
        attrs[0] |= termios.IXON
        termios.tcsetattr(fd, termios.TCSADRAIN, attrs)
    except Exception:
        pass


# --- ASCII art header ---

BANNER_FULL = f"""{BOLD}{RED}
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ████████╗ ██████╗  ██████╗ ██╗     ███████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝   ██║   ██║   ██║██║   ██║██║     ███████╗
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗   ██║   ██║   ██║██║   ██║██║     ╚════██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗███████║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝{R}"""

BANNER_COMPACT = f"  {BOLD}{RED}[ CYBERTOOLS VESSEL ]{R}"

DIVIDER = c("─" * 58, GRY)
DIVIDER_THIN = c("·" * 58, GRY)


def _banner_line(full: bool = True):
    if full:
        print(BANNER_FULL)
    else:
        print(BANNER_COMPACT)
    ver_str = f"v{__version__}"
    url_str = __url__
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    dot = c("·", CYAN)
    print(f"  {dot}  {c('CyberTools Vessel', WHT)}  {c(ver_str, GRN)}")
    print(f"  {dot}  {c(url_str, CYAN)}")
    print(f"  {dot}  {c(now_str, YEL)}")


# --- hotkey bar ---


def _print_footer():
    parts = [
        f"{c('Ctrl+Q', YEL)} {c('Quit', WHT)}",
        f"{c('0',     YEL)} {c('Exit', WHT)}",
        f"{c('?',     YEL)} {c('Help', WHT)}",
        f"{c('↑↓',    YEL)} {c('History', WHT)}",
    ]
    bar = f"  {c('│', GRY)}  ".join(parts)
    # session badge
    sess = f"{c('Session:', WHT)} {c(_session_info(), GRN)}  {c('Cmds:', WHT)} {c(str(_session_cmds), GRN)}"
    w = _get_term_width()
    sep = c("─" * w, GRY)
    print(sep)
    print(f"  {bar}    {sess}")
    print(sep)


# --- Config box ---


def print_config_box():
    conf = cfg.load()
    api_url = conf.get("api_url", "?")
    timeout = conf.get("timeout", 60)
    dot = c("·", YEL)
    print(DIVIDER)
    print(f"  {dot}  {c('API', WHT)}  {c(api_url, CYAN)}")
    print(f"  {dot}  {c('Timeout', WHT)}  {c(str(timeout)+'s', GRN)}")
    print(f"  {dot}  {c(str(cfg.CONFIG_FILE), GRY)}")
    print(DIVIDER)


# --- Menu definition ---

MENU_SECTIONS = [
    (
        "RECON",
        CYAN,
        [
            ("1", "◎", "Recon", "<domain>", "Full DNS, SSL & header recon"),
            (
                "2",
                "⟳",
                "Analyze URL",
                "<url>",
                "Redirect chain + misconfiguration hints",
            ),
            ("3", "◈", "BB Scan", "<url>", "Bug-bounty path probing"),
            (
                "4",
                "⊞",
                "Expand Subdomains",
                "<domain>",
                "Passive sub-enum via crt.sh & SAN",
            ),
            ("5", "⊡", "Endpoints", "<url>", "60+ endpoint discovery"),
            ("6", "⊟", "Params", "<url>", "Injectable parameter detection"),
        ],
    ),
    (
        "WORKFLOWS",
        YEL,
        [
            (
                "7",
                "⚡",
                "Full Workflow",
                "<target>",
                "5-stage automated recon pipeline",
            ),
            ("8", "▶", "Express Workflow", "<target>", "Fast: recon + analyze"),
            ("9", "◉", "Bug Bounty", "<target>", "Recon + scan + payload hints"),
            ("10", "⊹", "Subdomains", "<domain>", "Subdomain-focused workflow"),
            ("11", "⊠", "API Scan", "<url>", "API endpoint + param workflow"),
        ],
    ),
    (
        "UTILITIES",
        MAG,
        [
            (
                "12",
                "◇",
                "Payloads",
                "<xss|sqli|lfi|ssrf|idor>",
                "Payload lists by vuln type",
            ),
            ("13", "⌗", "Hash", "<algo> <text>", "Hash any string"),
            ("14", "⊛", "Encode", "<base64|hex|url> <text>", "Encode / decode text"),
            ("15", "⊙", "IP Info", "<address|me>", "IP geolocation & ASN lookup"),
            (
                "16",
                "🔑",
                "Password Analyze",
                "<password>",
                "Strength, entropy & feedback",
            ),
        ],
    ),
    (
        "SYSTEM",
        GRN,
        [
            ("17", "⊚", "Last Scan", "", "Recall last API result"),
            ("18", "▤", "Cache Status", "", "View API cache stats"),
            ("19", "⚙", "Show Config", "", "Display current config"),
            ("20", "✎", "Set Config", "<key> <value>", "Update a config value"),
            ("0", "✗", "Exit", "", "Quit to shell  [Ctrl+Q]"),
        ],
    ),
]

# Column widths
_NUM_W = 3
_ICON_W = 2
_LABEL_W = 22
_ARG_W = 28


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def _render_item(num, icon, label, arg, col):
    """Returns (plain_len, ansi_text) for one menu item."""
    arg_s = f" {arg}" if arg else ""
    plain = f"  {num+'.':>{_NUM_W}}  {icon} {label}{arg_s}"
    ansi = f"  {c(num+'.', col):>{_NUM_W}}  {c(icon, col)} {bold(label)}{dgry(arg_s)}"
    return len(plain), ansi


def print_menu():
    def build_lines(sections):
        lines = []
        for title, col, items in sections:
            lines.append(("HDR", title, col))
            for entry in items:
                lines.append(("ITEM",) + entry + (col,))
            lines.append(("GAP",))
        return lines

    left = build_lines(MENU_SECTIONS[:2])
    right = build_lines(MENU_SECTIONS[2:])
    maxl = max(len(left), len(right))
    left += [("GAP",)] * (maxl - len(left))
    right += [("GAP",)] * (maxl - len(right))

    COL_W = 46

    print()
    for l, r in zip(left, right):
        # Left cell
        if l[0] == "HDR":
            lhs_plain_len = len(f"  ┄ {l[1]}")
            lhs_ansi = f"  {dgry('┄')} {c(l[1], l[2]+BOLD)}"
        elif l[0] == "ITEM":
            _, num, icon, label, arg, _desc, col = l
            lhs_plain_len, lhs_ansi = _render_item(num, icon, label, arg, col)
        else:
            lhs_plain_len, lhs_ansi = 0, ""

        # Right cell
        if r[0] == "HDR":
            rhs_ansi = f"  {dgry('┄')} {c(r[1], r[2]+BOLD)}"
        elif r[0] == "ITEM":
            _, num, icon, label, arg, _desc, col = r
            _, rhs_ansi = _render_item(num, icon, label, arg, col)
        else:
            rhs_ansi = ""

        pad = max(0, COL_W - lhs_plain_len)
        print(f"{lhs_ansi}{' ' * pad}{rhs_ansi}")
    print()


def _print_help_overlay():
    """Show a compact help overlay listing all commands."""
    print(f"\n  {BOLD}{CYAN}QUICK REFERENCE{R}")
    print(DIVIDER)
    for _, col, items in MENU_SECTIONS:
        for num, icon, label, arg, desc in items:
            num_s = c(f"{num}.", col)
            icon_s = c(icon, col)
            arg_s = dgry(f" {arg}") if arg else ""
            print(f"  {num_s:>4}  {icon_s}  {bold(label)}{arg_s}")
            print(f"        {dgry('└ '+desc)}")
    print(
        f"\n  {dgry('Hotkeys:')}  {c('Ctrl+Q', YEL)} exit  {c('?', YEL)} this help  {c('↑↓', YEL)} history\n"
    )


def prompt_input(label: str) -> str:
    try:
        return input(f"  {cyan('▸')} {bold(label)}: ").strip()
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
        print(f"\n  {ok('✓')} Saved → {cyan(save_path)}\n")
        return
    if "error" in data:
        print(f"\n  {bad('✗')} {data['error']}\n")
        return
    _render(data)


def _render(data: dict):
    print()
    _print_section("RESULT", data)


def _print_section(title: str, data: dict, indent: int = 2):
    pad = " " * indent
    print(f"{pad}{cyan('◉')} {bold(title)}")
    for k, v in data.items():
        if isinstance(v, dict):
            print(f"{pad}  {dgry(k+':')}")
            _print_section(k.upper(), v, indent + 4)
        elif isinstance(v, list):
            if not v:
                continue
            print(f"{pad}  {dgry(k+':')} {_format_list(v, indent + 4)}")
        else:
            color = GRN if k in ("ip", "domain", "valid") else WHT
            print(f"{pad}  {dgry(k+':')} {c(str(v), color)}")


def _format_list(items: list, indent: int) -> str:
    if not items:
        return dgry("[]")
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
                    col = (
                        GRN
                        if v == 200
                        else YEL if isinstance(v, int) and v < 400 else RED
                    )
                    parts.append(c(str(v), col))
                elif k == "risk":
                    col = RED if v == "high" else YEL if v == "medium" else GRN
                    parts.append(c(f"[{v}]", col))
                elif k in ("payload", "subdomain", "path", "name"):
                    parts.append(c(str(v), CYAN))
                else:
                    parts.append(dgry(f"{k}={v}"))
            lines.append(f"\n{pad}  " + "  ".join(parts))
        else:
            lines.append(f"\n{pad}  {c('›', CYAN)} {item}")
    return "".join(lines)


def _print_smart(data: dict):
    summary = data.get("smart_summary", [])
    steps = data.get("next_steps", [])
    if summary:
        print(f"\n  {bold(cyan('SMART SUMMARY'))}")
        print(DIVIDER_THIN)
        for line in summary:
            print(f"  {cyan('›')} {line}")
    if steps:
        print(f"\n  {bold(cyan('NEXT STEPS'))}")
        print(DIVIDER_THIN)
        for i, step in enumerate(steps, 1):
            print(f"  {c(str(i)+'.', YEL)} {step}")
    print()


# --- Command handlers ---


def cmd_recon(args, raw=False, save=None):
    domain = args[0] if args else prompt_input("Domain")
    if not domain:
        return
    print(f"\n  {dgry('Resolving IP, DNS, SSL...')}")
    d = api.recon(domain)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_recon(d)


def _print_recon(d: dict):
    if "error" in d:
        print(f"\n  {bad('✗')} {d['error']}")
        return
    print(f"\n  {bold(cyan('HOST INFO'))}")
    print(DIVIDER)
    print(f"  {dgry('Domain   ')} {cyan(d.get('domain',''))}")
    print(f"  {dgry('IP       ')} {ok(d.get('ip','—'))}")
    print(f"  {dgry('Protocol ')} {d.get('protocol','').upper()}")
    sc = d.get("status_code")
    scol = GRN if sc and sc < 400 else RED
    print(f"  {dgry('Status   ')} {c(str(sc or '—'), scol)}")
    ssl_d = d.get("ssl", {})
    if ssl_d:
        print(f"\n  {bold(cyan('SSL'))}")
        print(DIVIDER)
        print(f"  {dgry('Valid    ')} {ok('Yes') if ssl_d.get('valid') else bad('No')}")
        print(f"  {dgry('Expires  ')} {ssl_d.get('expires','—')}")
        days = ssl_d.get("days_remaining")
        print(
            f"  {dgry('Days     ')} {(ok if days and days>30 else bad)(str(days or '—'))}"
        )
        print(f"  {dgry('Issuer   ')} {ssl_d.get('issuer','—')}")
    dns_d = d.get("dns", {})
    if dns_d:
        print(f"\n  {bold(cyan('DNS RECORDS'))}")
        print(DIVIDER)
        for rtype, records in dns_d.items():
            print(f"  {dgry(rtype+' '):<16} {', '.join(str(r) for r in records[:3])}")
    missing = d.get("missing_security_headers", [])
    if missing:
        print(f"\n  {bold(ORG+'MISSING SECURITY HEADERS'+R)}")
        print(DIVIDER)
        for h in missing:
            print(f"  {miss('⊘')} {miss(h)}")
    else:
        print(f"\n  {ok('✓')} All major security headers present.")
    tech = d.get("tech_hints", [])
    if tech:
        print(f"\n  {bold(cyan('TECH STACK'))}")
        print(DIVIDER)
        for t in tech:
            print(f"  {warn('●')} {t}")
    _print_smart(d)


def cmd_analyze(args, raw=False, save=None):
    url = args[0] if args else prompt_input("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    print(f"\n  {dgry('Following redirects...')}")
    d = api.analyze(url)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_analyze(d)


def _print_analyze(d: dict):
    if "error" in d:
        print(f"\n  {bad('✗')} {d['error']}")
        return
    print(f"\n  {bold(cyan('REDIRECT CHAIN'))}")
    print(DIVIDER)
    for hop in d.get("redirect_chain", []):
        sc = hop["status"]
        col = GRN if sc < 300 else YEL if sc < 400 else RED
        print(f"  {c(str(sc), col)} {dgry('→')} {hop['url']}")
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
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    print(f"\n  {dgry('Probing paths concurrently (~3-5s)...')}")
    d = api.bb_scan(url)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_scan(d)


def _print_scan(d: dict):
    if "error" in d:
        print(f"\n  {bad('✗')} {d['error']}")
        return
    found = d.get("interesting_paths", [])
    print(f"\n  {bold(cyan(f'INTERESTING PATHS ({len(found)})'))} ")
    print(DIVIDER)
    for p in found:
        sc = p["status"]
        col = GRN if sc == 200 else YEL if str(sc).startswith("3") else RED
        print(f"  {c(str(sc), col):>6}  {p['path']}")
    if not found:
        print(f"  {dgry('No interesting paths found.')}")
    hints = d.get("bug_bounty_hints", [])
    if hints:
        print(f"\n  {bold(cyan('BUG BOUNTY HINTS'))}")
        print(DIVIDER)
        for h in hints:
            col = (
                RED if "CRITICAL" in h or "HIGH" in h else YEL if "INFO" in h else CYAN
            )
            print(f"  {c('›', col)} {h}")
    _print_smart(d)


def cmd_expand(args, raw=False, save=None):
    domain = args[0] if args else prompt_input("Domain")
    if not domain:
        return
    print(f"\n  {dgry('Querying crt.sh, hackertarget, SSL SAN...')}")
    d = api.expand(domain)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_expand(d)


def _print_expand(d: dict):
    if "error" in d:
        print(f"\n  {bad('✗')} {d['error']}")
        return
    subs = d.get("subdomains", [])
    live = [s for s in subs if s.get("live")]
    dead = [s for s in subs if not s.get("live")]
    print(
        f"\n  {bold(cyan(f'LIVE SUBDOMAINS ({len(live)})'))} {dgry('via '+ ', '.join(d.get('sources',[])))}"
    )
    print(DIVIDER)
    for s in live:
        print(f"  {ok('●')} {cyan(s['subdomain'])} {dgry(s.get('ip',''))}")
    if dead:
        print(f"\n  {dgry(f'Non-resolving: {len(dead)}')}")
        for s in dead[:6]:
            print(f"  {bad('○')} {dgry(s['subdomain'])}")
    _print_smart(d)


def cmd_endpoints(args, raw=False, save=None):
    url = args[0] if args else prompt_input("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    print(f"\n  {dgry('Probing 60+ paths...')}")
    d = api.endpoints(url)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_endpoints(d)


def _print_endpoints(d: dict):
    if "error" in d:
        print(f"\n  {bad('✗')} {d['error']}")
        return
    eps = d.get("endpoints", [])
    type_col = {
        "sensitive": RED,
        "admin": RED,
        "api": GRN,
        "auth": YEL,
        "monitoring": YEL,
        "other": DIM,
    }
    print(
        f"\n  {bold(cyan(f'FOUND ENDPOINTS ({len(eps)})'))} {dgry('of '+ str(d.get('paths_probed',0)) +' probed')}"
    )
    print(DIVIDER)
    for ep in eps:
        col = type_col.get(ep.get("type", "other"), DIM)
        sc = ep["status"]
        scol = GRN if sc == 200 else YEL if sc < 400 else RED
        print(
            f"  {c('['+ep.get('type','?')+']', col):<22} {ep['path']:<35} {c(str(sc), scol)}"
        )
    _print_smart(d)


def cmd_params(args, raw=False, save=None):
    url = args[0] if args else prompt_input("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    print(f"\n  {dgry('Probing 26 common parameters...')}")
    d = api.params(url)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_params(d)


def _print_params(d: dict):
    if "error" in d:
        print(f"\n  {bad('✗')} {d['error']}")
        return
    interesting = d.get("interesting", [])
    print(
        f"\n  {bold(cyan(f'INTERESTING PARAMETERS ({len(interesting)})'))} {dgry('tested: '+str(d.get('params_tested',0)))}"
    )
    print(DIVIDER)
    for p in interesting:
        rc = RED if p["risk"] == "high" else YEL if p["risk"] == "medium" else GRN
        print(f"  {c('['+p['risk']+']', rc):<18} {cyan('?'+p['name']+'=FUZZ')}")
        print(f"  {dgry('   ↳ '+p['test'])}")
    if not interesting:
        print(f"  {dgry('No clearly injectable params found.')}")
    _print_smart(d)


def cmd_workflow(args, raw=False, save=None, mode="full"):
    target = args[0] if args else prompt_input("Target")
    if not target:
        return
    funcs = {
        "full": api.workflow,
        "express": api.workflow_express,
        "bugbounty": api.workflow_bugbounty,
        "subdomains": api.workflow_subdomains,
        "api": api.workflow_api,
    }
    fn = funcs.get(mode, api.workflow)
    print(f"\n  {dgry('Running pipeline...')}")
    d = (
        fn(target)
        if mode != "api"
        else fn(target if target.startswith("http") else "https://" + target)
    )
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_workflow(d)


def _print_workflow(d: dict):
    if "error" in d:
        print(f"\n  {bad('✗')} {d['error']}")
        return
    elapsed = d.get("elapsed_seconds", "?")
    print(f"\n  {bold(cyan('WORKFLOW COMPLETE'))} {dgry(f'({elapsed}s)')}")
    print(DIVIDER)
    recon = d.get("recon", {})
    if recon.get("ip"):
        print(f"  {dgry('IP       ')} {ok(recon['ip'])}")
        print(f"  {dgry('Status   ')} {recon.get('status_code','—')}")
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
            print(
                f"  {cyan('['+ep.get('type','?')+']'):<20} {ep['path']} → {ep['status']}"
            )
    iparams = d.get("params", {}).get("interesting", [])
    if iparams:
        print(f"\n  {bold(RED+f'INJECTABLE PARAMS ({len(iparams)})'+R)}")
        print(DIVIDER)
        for p in iparams[:5]:
            rc = RED if p["risk"] == "high" else YEL
            print(f"  {c('!', rc)} {cyan('?'+p['name']+'=')} {dgry(p['test'])}")
    _print_smart(d)


def cmd_payloads(args, raw=False, save=None):
    ptype = (
        args[0] if args else prompt_input("Type (xss/sqli/lfi/ssrf/idor/open_redirect)")
    )
    if not ptype:
        return
    d = api.payloads(ptype)
    _handle_output(d, raw, save)
    if not raw and not save:
        _print_payloads(d)


def _print_payloads(d: dict):
    if "error" in d:
        print(f"\n  {bad('✗')} {d['error']}")
        return
    print(
        f"\n  {bold(cyan(d.get('type','').upper()+' PAYLOADS'))} {dgry('('+str(d.get('count',0))+' total)')}"
    )
    print(DIVIDER)
    print(f"  {dgry(d.get('description',''))}\n")
    for p in d.get("payloads", []):
        ctx = p.get("context", "")
        label = p.get("label", "")
        ctxl = warn(f"[{ctx}]") if ctx else ""
        print(f"  {cyan(p['payload'])}  {dgry(label)} {ctxl}")
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
    if not algo or not text:
        return
    d = api.hash_text(algo, text)
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d:
            print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(
                f"\n  {dgry('Hash')} ({d.get('algorithm','')})\n  {cyan(d.get('hash',''))}\n"
            )


def cmd_encode(args, raw=False, save=None):
    if len(args) >= 2:
        method, text = args[0], " ".join(args[1:])
    else:
        method = prompt_input("Method (base64/hex/url)")
        text = prompt_input("Text")
    if not method or not text:
        return
    d = api.encode(method, text)
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d:
            print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(f"\n  {cyan(d.get('encoded',''))}\n")


def cmd_ip(args, raw=False, save=None):
    addr = args[0] if args else prompt_input("IP address (or 'me')")
    if not addr:
        return
    d = api.ip_info(addr)
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d:
            print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(f"\n  {bold(cyan('IP INFO'))}")
            print(DIVIDER)
            for k, v in d.items():
                print(f"  {dgry(k+':')} {cyan(str(v))}")
            print()


def cmd_password(args, raw=False, save=None):
    pw = " ".join(args) if args else prompt_input("Password (for strength analysis)")
    if not pw:
        return
    d = api.password_analyze(pw)
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d:
            print(f"\n  {bad('✗')} {d['error']}")
        else:
            strength = d.get("strength", "")
            scol = (
                GRN if "Strong" in strength else YEL if "Moderate" in strength else RED
            )
            print(f"\n  {bold('Strength:')} {c(strength, scol)}")
            print(f"  {dgry('Score   ')} {d.get('score')}/{d.get('max_score')}")
            print(f"  {dgry('Entropy ')} {d.get('entropy_estimate_bits')} bits")
            for fb in d.get("feedback", []):
                print(f"  {warn('⚠')} {fb}")
            print()


def cmd_last(raw=False, save=None):
    d = api.last_scan()
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d:
            print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(f"\n  {bold(cyan('LAST SCAN'))}")
            print(DIVIDER)
            print(f"  {dgry('Target    ')} {cyan(d.get('key',''))}")
            print(f"  {dgry('Timestamp ')} {d.get('timestamp','')}")
            summary = (d.get("data") or {}).get("smart_summary", [])
            for s in summary[:8]:
                print(f"  {cyan('›')} {s}")
            print()


def cmd_cache(raw=False, save=None):
    d = api.cache_status()
    _handle_output(d, raw, save)
    if not raw and not save:
        if "error" in d:
            print(f"\n  {bad('✗')} {d['error']}")
        else:
            print(f"\n  {bold(cyan('CACHE STATUS'))}")
            print(DIVIDER)
            print(f"  {dgry('Active   ')} {ok(str(d.get('active_entries',0)))}")
            print(f"  {dgry('Expired  ')} {warn(str(d.get('expired_entries',0)))}")
            print(f"  {dgry('Total    ')} {d.get('total_entries',0)}")
            print()


def cmd_config_show():
    print(f"\n  {bold(cyan('CURRENT CONFIG'))}")
    print(DIVIDER)
    print(cfg.show())
    print(f"\n  {dgry('File: '+ str(cfg.CONFIG_FILE))}\n")


def cmd_config_set(args):
    if len(args) >= 2:
        key, val = args[0], " ".join(args[1:])
    else:
        key = prompt_input("Key (api_url / timeout / save_dir)")
        val = prompt_input("Value")
    if not key or not val:
        return
    cfg.set_key(key, val)
    print(f"\n  {ok('✓')} {bold(key)} = {cyan(val)}\n")


# --- Output helper ---


def _handle_output(data: dict, raw: bool, save_path: str):
    if raw:
        print(json.dumps(data, indent=2))
    elif save_path:
        with open(save_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\n  {ok('✓')} Saved → {cyan(save_path)}\n")


# --- Dispatch tables ---

MENU_DISPATCH = {
    "1": lambda a, r, s: cmd_recon(a, r, s),
    "2": lambda a, r, s: cmd_analyze(a, r, s),
    "3": lambda a, r, s: cmd_scan(a, r, s),
    "4": lambda a, r, s: cmd_expand(a, r, s),
    "5": lambda a, r, s: cmd_endpoints(a, r, s),
    "6": lambda a, r, s: cmd_params(a, r, s),
    "7": lambda a, r, s: cmd_workflow(a, r, s, mode="full"),
    "8": lambda a, r, s: cmd_workflow(a, r, s, mode="express"),
    "9": lambda a, r, s: cmd_workflow(a, r, s, mode="bugbounty"),
    "10": lambda a, r, s: cmd_workflow(a, r, s, mode="subdomains"),
    "11": lambda a, r, s: cmd_workflow(a, r, s, mode="api"),
    "12": lambda a, r, s: cmd_payloads(a, r, s),
    "13": lambda a, r, s: cmd_hash(a, r, s),
    "14": lambda a, r, s: cmd_encode(a, r, s),
    "15": lambda a, r, s: cmd_ip(a, r, s),
    "16": lambda a, r, s: cmd_password(a, r, s),
    "17": lambda a, r, s: cmd_last(r, s),
    "18": lambda a, r, s: cmd_cache(r, s),
    "19": lambda a, r, s: cmd_config_show(),
    "20": lambda a, r, s: cmd_config_set(a),
}

CMD_NAME_DISPATCH = {
    "recon": "1",
    "analyze": "2",
    "scan": "3",
    "expand": "4",
    "endpoints": "5",
    "params": "6",
    "workflow": "7",
    "express": "8",
    "bugbounty": "9",
    "subdomains": "10",
    "apiscan": "11",
    "payloads": "12",
    "hash": "13",
    "encode": "14",
    "ip": "15",
    "password": "16",
    "last": "17",
    "cache": "18",
    "config": "19",
    "set": "20",
}

# Closest-match suggestions for typos
_CMD_ALIASES = {
    "rec": "recon",
    "anal": "analyze",
    "analyse": "analyze",
    "bb": "scan",
    "sub": "subdomains",
    "ep": "endpoints",
    "ep": "endpoints",
    "pay": "payloads",
    "pw": "password",
    "pass": "password",
    "enc": "encode",
    "wf": "workflow",
    "full": "workflow",
    "exp": "express",
    "api": "apiscan",
    "exit": "0",
    "quit": "0",
    "q": "0",
}


def _suggest_command(typo: str) -> str:
    if typo in _CMD_ALIASES:
        return _CMD_ALIASES[typo]
    # simple prefix match
    for cmd in list(CMD_NAME_DISPATCH.keys()):
        if cmd.startswith(typo[:3]):
            return cmd
    return ""


# --- Interactive loop ---


def interactive_loop():
    global _session_cmds, _session_last_cmd

    _setup_ctrl_q()
    clear_screen()
    _banner_line(full=True)
    print_config_box()

    first = True

    while True:
        if not first:
            print_menu()
        else:
            print_menu()
            first = False

        _print_footer()

        try:
            raw_choice = input(f"\n  {c('▸', RED)} Choice (0-20): ").strip()
        except (KeyboardInterrupt, EOFError):
            _restore_ixon()
            print(f"\n\n  {dgry('Session ended. Stay stealthy.')}\n")
            break

        choice = raw_choice.lower()

        # Exit shortcuts
        if choice in ("0", "exit", "quit", "q", ""):
            _restore_ixon()
            print(f"\n  {dgry('Goodbye. Stay stealthy.')}\n")
            break

        # Help overlay
        if choice in ("?", "help", "h"):
            _print_help_overlay()
            input(f"  {dgry('Press Enter to return...')}")
            clear_screen()
            _banner_line(full=False)
            print_config_box()
            continue

        # Check for named command (e.g. user types "recon" instead of "1")
        if choice in CMD_NAME_DISPATCH:
            choice = CMD_NAME_DISPATCH[choice]

        if choice not in MENU_DISPATCH:
            # Try suggestions
            suggestion = _suggest_command(choice)
            if suggestion and suggestion != "0":
                print(
                    f"\n  {warn('?')} Unknown: {c(repr(raw_choice), YEL)}  →  Did you mean {c(suggestion, CYAN)}?"
                )
            else:
                print(
                    f"\n  {bad('✗')} Invalid choice {c(repr(raw_choice), YEL)} — enter a number {c('0-20', CYAN)} or {c('?', YEL)} for help.\n"
                )
            continue

        _session_cmds += 1
        _session_last_cmd = raw_choice

        try:
            MENU_DISPATCH[choice]([], False, None)
        except Exception as e:
            print(f"\n  {bad('Error:')} {e}\n")

        # Show last command in the continue prompt
        cmd_label = next(
            (
                f"{num}. {icon} {label}"
                for _, _, items in MENU_SECTIONS
                for num, icon, label, *_ in items
                if num == choice
            ),
            choice,
        )
        print(f"\n  {dgry('─'*50)}")
        print(
            f"  {dgry('Ran:')} {c(cmd_label, CYAN)}   {dgry('Session cmds:')} {c(str(_session_cmds), GRN)}"
        )
        input(f"  {dgry('Press Enter to continue...')}")

        clear_screen()
        _banner_line(full=False)
        print_config_box()


# --- Entry point ---

USAGE = f"""
{bcyan('⌖ cybtl')} {dgry('— CyberTools Vessel v'+__version__)}

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
  cybtl           Launch TUI menu  ({c('Ctrl+Q', YEL)} or {c('0', YEL)} to exit)

{warn('API URL:')} {dgry(cfg.get('api_url','https://www.cyber-tools.dev'))}
"""


def main():
    args = sys.argv[1:]

    if not args:
        interactive_loop()
        return

    if args[0] in ("-h", "--help", "help"):
        print(USAGE)
        return

    if args[0] in ("-v", "--version", "version"):
        print(f"cybtl {__version__}")
        return

    raw = "--json" in args
    args = [a for a in args if a != "--json"]

    save = None
    if "--save" in args:
        idx = args.index("--save")
        save = args[idx + 1] if idx + 1 < len(args) else None
        args = [a for i, a in enumerate(args) if i != idx and i != idx + 1]

    cmd = args[0].lower()
    rest = args[1:]

    # alias support for CLI mode too
    if cmd in _CMD_ALIASES:
        cmd = _CMD_ALIASES[cmd]

    if cmd not in CMD_NAME_DISPATCH:
        print(f"\n  {bad('Unknown command:')} {cmd}")
        suggestion = _suggest_command(cmd)
        if suggestion:
            print(f"  {warn('Hint:')} did you mean {cyan(suggestion)}?")
        print(USAGE)
        sys.exit(1)

    menu_key = CMD_NAME_DISPATCH[cmd]
    try:
        MENU_DISPATCH[menu_key](rest, raw, save)
    except Exception as e:
        print(f"\n  {bad('Error:')} {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
