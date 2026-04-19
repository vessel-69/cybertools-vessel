<div align="center">

```
 ██████╗██╗   ██╗██████╗ ███████╗██████╗ ████████╗ ██████╗  ██████╗ ██╗     ███████╗
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝   ██║   ██║   ██║██║   ██║██║     ███████╗
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗   ██║   ██║   ██║██║   ██║██║     ╚════██║
╚██████╗   ██║   ██████╔╝███████╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗███████║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝
```

**cybertools-vessel** · Global CLI · v2.0.0

[![PyPI](https://img.shields.io/pypi/v/cybertools-vessel?style=flat-square&color=e63030)](https://pypi.org/project/cybertools-vessel/)
[![Python](https://img.shields.io/pypi/pyversions/cybertools-vessel?style=flat-square)](https://pypi.org/project/cybertools-vessel/)
[![License](https://img.shields.io/badge/license-MIT-e63030?style=flat-square)](LICENSE)

**One install. Every recon tool you need. No dependencies.**

</div>

---

## Install

```bash
pip install cybertools-vessel
```

That's it. No external dependencies — pure Python stdlib.

---

## Usage

### Interactive TUI (recommended)

```bash
cybtl
```

Launches the full menu interface (like the image above).

### Direct commands

```bash
cybtl recon      example.com
cybtl scan       https://example.com
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

### Workflow modes

```bash
cybtl express    example.com   # fast: recon + analyze
cybtl bugbounty  example.com   # recon + scan + recommended payloads
cybtl subdomains example.com   # subdomain enum + recon on each
cybtl apiscan    https://api.example.com  # endpoint + param scan
```

### Flags

```bash
cybtl recon example.com --json              # raw JSON output
cybtl workflow example.com --save out.json  # save to file
```

---

## Config

Settings are stored in `~/.config/cybtl/config.json`.

```bash
cybtl config                           # show current config
cybtl set api_url https://your.server  # use self-hosted instance
cybtl set timeout 120                  # change request timeout
```

**Default config:**

| Key       | Default                              |
|-----------|--------------------------------------|
| `api_url` | `https://www.cyber-tools.dev`        |
| `timeout` | `60`                                 |
| `save_dir`| `~/cybtl-reports`                    |

---

## Commands reference

| Command | Args | Description |
|---------|------|-------------|
| `recon` | `<domain>` | IP, DNS, SSL, headers, tech stack |
| `analyze` | `<url>` | Redirect chain, CORS/HSTS/CSP misconfigs |
| `scan` | `<url>` | 30+ path probe (admin, .env, .git, swagger) |
| `expand` | `<domain>` | Passive subdomain enum |
| `endpoints` | `<url>` | 60+ endpoint scan, tagged by type |
| `params` | `<url>` | 26 common injectable params |
| `workflow` | `<target>` | Full 5-stage pipeline |
| `express` | `<target>` | Fast recon + analyze |
| `bugbounty` | `<target>` | Recon + scan + recommended payloads |
| `subdomains` | `<domain>` | Subdomain enum + recon on each |
| `apiscan` | `<url>` | Endpoint enum + param probing |
| `payloads` | `<type>` | xss / sqli / lfi / ssrf / idor / open_redirect |
| `hash` | `<algo> <text>` | md5, sha1, sha256, sha384, sha512, blake2b |
| `encode` | `<method> <text>` | base64 / hex / url |
| `ip` | `<address\|me>` | IP geolocation |
| `password` | `<pw>` | Strength, entropy, feedback |
| `last` | — | Last cached scan |
| `cache` | — | Cache status |
| `config` | — | Show config |
| `set` | `<key> <value>` | Set config value |

---

## Self-hosted

Point `cybtl` at your own CyberTools API instance:

```bash
cybtl set api_url http://localhost:8000
```

Or per-run:

```bash
CYBERTOOLS_URL=http://localhost:8000 cybtl recon example.com
```

---

## Links

- **API:** https://www.cyber-tools.dev
- **Docs:** https://www.cyber-tools.dev/docs
- **API repo:** https://github.com/vessel-69/cybertools-api
- **AUR package:** https://aur.archlinux.org/packages/cybertools-vessel

---

## License

MIT © vessel-69
