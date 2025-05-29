![version](https://img.shields.io/badge/version-1.0-green.svg)
![python](https://img.shields.io/badge/python-3.8+-blue.svg)

`DOMAIN8` is a fast domain enumeration tool written in Python using `aiohttp` and `asyncio`.

---

## Features

- Asynchronous directory and subdomain scanning
- Host header spoofing for IP-based vhosts
- Extension-based fuzzing (`.php`, `.html`, etc.)
- Status code filtering
- Throttled concurrent connections

---

## Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/j4ke-exe/domain8.git
cd domain8
pip install -r requirements.txt
```

---

## Usage

```bash
python domain8.py --w <wordlist.txt> --d <domain> [--x .php,.html] [--t 10]
python domain8.py --w <wordlist.txt> --s <domain> [--ip <ip>] [--t 10]
```

---

## Examples

```bash
# Basic directory scan
python domain8.py --w paths.txt --d https://example.com

# Directory scan with file extensions and status code filtering
python domain8.py --w paths.txt --d http://example.com --x .php,.html --sc 200,403

# Subdomain enumeration
python domain8.py --w subdomains.txt --s example.com

# Subdomain scan via IP with host header spoofing
python domain8.py --w subdomains.txt --s example.com --ip 10.10.10.10

# Throttle concurrency to XX requests at a time
python domain8.py --w paths.txt --d https://example.com --t 10
```

---

## Options

| Flag       | Description                                              |
|------------|----------------------------------------------------------|
| `--w`      | Wordlist file (**required**)                         	|
| `--d`      | Directory scan 										 	|
| `--s`      | Subdomain scan 											|
| `--ip`     | Optional IP address for host header spoofing             |
| `--sc`     | Filter status codes (e.g., `200,301,403`, default: 200)	|
| `--x`      | File extensions (e.g., `.php,.html`) 					|
| `--t`      | Max concurrent requests (default: 20)                    |
| `--h`      | Show help message                                        |

---

## Legal Disclaimer

> This tool is intended for educational purposes and authorized penetration testing.  
> Unauthorized use of this tool against systems without explicit permission is **strictly prohibited** and **illegal**.

By using this tool, you agree to:

- Operate only within the bounds of **legal and ethical hacking practices**.
- Use `domain8` **only** on systems you own or are authorized to test.
- Assume **full responsibility** for any consequences resulting from its use.

**The author assumes no liability for any misuse or resulting damage.**

---

## License

This project is open-source and licensed under the [MIT License](LICENSE).
