<div align="center">

```text
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ████████╗ ██████╗  ██████╗ ██╗     ███████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝   ██║   ██║   ██║██║   ██║██║     ███████╗
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗   ██║   ██║   ██║██║   ██║██║     ╚════██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗███████║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
```

# cybertools-vessel

**Global CLI for CyberTools API · v1.1.0**

[![PyPI](https://img.shields.io/badge/pypi-v1.1.0-e63030?style=flat-square&logo=pypi&logoColor=white)](https://pypi.org/project/cybertools-vessel/)
[![Python](https://img.shields.io/badge/python-%3E%3D3.10-3776AB?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/cybertools-vessel/)
[![License](https://img.shields.io/badge/license-MIT-e63030?style=flat-square)](LICENSE)
[![AUR](https://img.shields.io/badge/AUR-cybertools--vessel-1793D1?style=flat-square&logo=archlinux&logoColor=white)](https://aur.archlinux.org/packages/cybertools-vessel)

**One install. Almost Every recon tool you need. No dependency jungle.**

A Python-based global CLI for recon, payloads, scanning helpers, API testing, hashes, encoding, and bug bounty workflow stuff.

Basically: less tab-hopping, more doing.

</div>

---

## Install

### Using pip

```bash
pip install cybertools-vessel
```

### Using pipx

Recommended if you want it installed globally without messing with your Python environment.

```bash
pipx install cybertools-vessel
```

If you do not have `pipx` yet:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Then restart your terminal and run:

```bash
pipx install cybertools-vessel
```

That is it. No dramatic setup ritual required.

---

## Usage

### Interactive TUI

```bash
cybtl
```

Launches the full menu interface.

Good for when you want the tool to feel like a tiny command-line control room instead of remembering every command like a sleep-deprived wizard.

---

## Direct commands

```bash
cybtl recon      example.com
cybtl scan       https://example.com
cybtl analyze    https://example.com
cybtl expand     example.com
cybtl endpoints  https://example.com
cybtl params     https://example.com
cybtl workflow   example.com
cybtl payloads   sqli
cybtl hash       sha256 "hello world"
cybtl encode     base64 "hello"
cybtl ip         8.8.8.8
cybtl password   "MyP@ssw0rd!"
```

---

## Workflow modes

```bash
cybtl express    example.com          # fast recon + analyze
cybtl bugbounty  example.com          # recon + scan + recommended payloads
cybtl subdomains example.com          # subdomain enum + recon on each
cybtl apiscan    https://api.site.com # endpoint + param scan
```

These are for when you want a quick flow instead of manually typing five commands and pretending that was the plan all along.

---

## Flags

```bash
cybtl recon example.com --json
cybtl workflow example.com --save out.json
```

Use `--json` when you want raw output.

Use `--save` when you want receipts.

---

## Config

Settings are stored here:

```bash
~/.config/cybtl/config.json
```

Show current config:

```bash
cybtl config
```

Change API URL:

```bash
cybtl set api_url https://your.server
```

Change timeout:

```bash
cybtl set timeout 120
```

### Default config

| Key        | Default                       |
| ---------- | ----------------------------- |
| `api_url`  | `https://www.cyber-tools.dev` |
| `timeout`  | `60`                          |
| `save_dir` | `~/cybtl-reports`             |

---

## Commands reference

| Command      | Args              | Description                                             |
| ------------ | ----------------- | ------------------------------------------------------- |
| `recon`      | `<domain>`        | IP, DNS, SSL, headers, tech stack                       |
| `analyze`    | `<url>`           | Redirect chain, CORS, HSTS, CSP checks                  |
| `scan`       | `<url>`           | Common path probing like admin, `.env`, `.git`, swagger |
| `expand`     | `<domain>`        | Passive subdomain enumeration                           |
| `endpoints`  | `<url>`           | Endpoint scan, tagged by type                           |
| `params`     | `<url>`           | Common injectable parameter checks                      |
| `workflow`   | `<target>`        | Full recon workflow                                     |
| `express`    | `<target>`        | Fast recon + analyze                                    |
| `bugbounty`  | `<target>`        | Recon + scan + payload suggestions                      |
| `subdomains` | `<domain>`        | Subdomain enum + recon on each                          |
| `apiscan`    | `<url>`           | API endpoint and parameter scan                         |
| `payloads`   | `<type>`          | Payloads for xss, sqli, lfi, ssrf, idor, open redirect  |
| `hash`       | `<algo> <text>`   | md5, sha1, sha256, sha384, sha512, blake2b              |
| `encode`     | `<method> <text>` | base64, hex, url                                        |
| `ip`         | `<address\|me>`   | IP geolocation                                          |
| `password`   | `<pw>`            | Password strength and feedback                          |
| `last`       | —                 | Show last cached scan                                   |
| `cache`      | —                 | Show cache status                                       |
| `config`     | —                 | Show config                                             |
| `set`        | `<key> <value>`   | Set config value                                        |

---

## Self-hosted

Point `cybtl` at your own CyberTools API instance:

```bash
cybtl set api_url http://localhost:8000
```

Or use a custom API URL for one run:

```bash
CYBERTOOLS_URL=http://localhost:8000 cybtl recon example.com
```

Useful if you are running your own backend locally and want to test without touching production.

Tiny chaos, but controlled.

---

## Links

| Name        | Link                                                                                                         |
| ----------- | ------------------------------------------------------------------------------------------------------------ |
| Website     | [https://www.cyber-tools.dev](https://www.cyber-tools.dev)                                                   |
| Docs        | [https://www.cyber-tools.dev/docs](https://www.cyber-tools.dev/docs)                                         |
| PyPI        | [https://pypi.org/project/cybertools-vessel/](https://pypi.org/project/cybertools-vessel/)                   |
| API repo    | [https://github.com/vessel-69/cybertools-api](https://github.com/vessel-69/cybertools-api)                   |
| AUR package | [https://aur.archlinux.org/packages/cybertools-vessel](https://aur.archlinux.org/packages/cybertools-vessel) |

---

## Notes

This tool is built for legal testing, learning, bug bounty workflows, and your own authorized targets.

Do not run it on random websites like a goblin with Wi-Fi.

---

## License

MIT © vessel-69
