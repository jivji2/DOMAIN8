#!/usr/bin/env python3
import sys
import asyncio
import aiohttp
import argparse
from urllib.parse import urlparse
from tqdm.asyncio import tqdm


GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def banner():
    print(f"""{GREEN}
    ██████╗  ██████╗ ███╗   ███╗ █████╗ ██╗███╗   ██╗ █████╗
    ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██║████╗  ██║██╔══██╗
    ██║  ██║██║   ██║██╔████╔██║███████║██║██╔██╗ ██║╚█████╔╝
    ██║  ██║██║   ██║██║╚██╔╝██║██╔══██║██║██║╚██╗██║██╔══██╗
    ██████╔╝╚██████╔╝██║ ╚═╝ ██║██║  ██║██║██║ ╚████║╚█████╔╝
    ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚════╝ v1.0

          {RESET}Domain Enumeration Tool{GREEN} | {RESET}github.com/j4ke-exe
""")


def usage_and_error(message=None):
    banner()
    print(f"""
Usage:
    python domain8.py --w <wordlist.txt> --d <domain> [--x .php,.html] [--t 10]
    python domain8.py --w <wordlist.txt> --s <domain> [--ip <ip>] [--t 10]

Examples:
    python domain8.py --w paths.txt --d example.com
    python domain8.py --w sublist.txt --s test.thm --ip 10.10.10.10

Flags:
    --d         Directory scan with full URL (http:// or https://)
    --s         Subdomain scan using base domain (e.g., test.thm)
    --ip        Use this IP instead of resolving subdomains
    --w         Path to wordlist
    --sc        Status codes to display (e.g., 200,301,403,404, default=200)
    --x         File extensions for directory scan (e.g., .php,.html)
    --t         Throttle (max concurrent requests, default=20)
    --h         Show this help message
""")
    if message:
        print(f"{RED}Error: {message}{RESET}")


async def fetch(session, url, semaphore, headers=None, retries=2, display_host=None):
    async with semaphore:
        attempts = 0
        while attempts <= retries:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5), ssl=False, headers=headers) as resp:
                    await resp.text()
                    if display_host:
                        return resp.status, f"{url} ({display_host})"
                    return resp.status, url
            except:
                await asyncio.sleep(0.5)
                attempts += 1
        return None, url


async def scan_directories(wordlist, domain, extensions, codes, throttle):
    try:
        with open(wordlist, "r") as f:
            lines = f.readlines()
    except:
        print(f"{RED}Wordlist file not found!{RESET}")
        return

    entries = []
    for line in lines:
        line = line.strip()
        if line:
            entries.append(line)

    parsed = urlparse(domain)
    if parsed.scheme:
        scheme = parsed.scheme
        netloc = parsed.netloc
    else:
        scheme = "http"
        netloc = parsed.path

    base_url = f"{scheme}://{netloc}"

    urls = []
    for entry in entries:
        entry = entry.strip("/")
        urls.append(f"{base_url}/{entry}/")

    for entry in entries:
        for ext in extensions:
            ext = ext.strip().lstrip(".")
            urls.append(f"{base_url}/{entry.strip('/')}.{ext}")

    banner()
    semaphore = asyncio.Semaphore(throttle)

    connector = aiohttp.TCPConnector(limit_per_host=throttle, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for url in urls:
            task = fetch(session, url, semaphore)
            tasks.append(task)

        futures = asyncio.as_completed(tasks)
        async for result in tqdm(futures, total=len(tasks), desc="Directory scan", leave=False):
            status, link = await result
            if status is None:
                continue
            if codes:
                if status not in codes:
                    continue
            elif status not in (200, 301, 302, 403):
                continue

            if status == 200:
                color = GREEN
                icon = "✔"
            elif 300 <= status < 400:
                color = CYAN
                icon = "↪"
            else:
                color = RED
                icon = "✖"

            tqdm.write(f"{color}[{RESET}{icon}{color}]{RESET} {color}{status}{RESET} ➜ {YELLOW}{link}{RESET}")


async def scan_subdomains(wordlist, domain, ip, codes, throttle):
    try:
        with open(wordlist, "r") as f:
            lines = f.readlines()
    except:
        print(f"{RED}Wordlist file not found!{RESET}")
        return

    subs = []
    for line in lines:
        line = line.strip()
        if line:
            subs.append(line)

    urls = []
    for sub in subs:
        full = f"{sub}.{domain}"
        headers = None
        target = full

        if ip:
            headers = {"Host": full}
            target = ip

        urls.append((f"http://{target}", headers, full))
        urls.append((f"https://{target}", headers, full))

    banner()
    semaphore = asyncio.Semaphore(throttle)

    connector = aiohttp.TCPConnector(limit_per_host=throttle, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for item in urls:
            url = item[0]
            head = item[1]
            display = item[2]
            task = fetch(session, url, semaphore, headers=head, display_host=display)
            tasks.append(task)

        futures = asyncio.as_completed(tasks)
        async for result in tqdm(futures, total=len(tasks), desc="Subdomain scan", leave=False):
            status, shown = await result
            if status is None:
                continue
            allowed = codes if codes else {200, 301, 302, 401, 403}
            if status not in allowed:
                continue

            if status == 200:
                color = GREEN
                icon = "✔"
            elif status in (301, 302):
                color = CYAN
                icon = "↪"
            else:
                color = RED
                icon = "✖"

            tqdm.write(f"{color}[{RESET}{icon}{color}]{RESET} {color}{status}{RESET} ➜ {YELLOW}{shown}{RESET}")


def parse_args():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--d")
    parser.add_argument("--s")
    parser.add_argument("--ip")
    parser.add_argument("--w")
    parser.add_argument("--sc")
    parser.add_argument("--x")
    parser.add_argument("--t", type=int, default=20)
    parser.add_argument("--h", action="store_true")
    return parser.parse_args()


async def main():
    args = parse_args()

    if args.h:
        usage_and_error()
        sys.exit(0)

    if not args.w:
        usage_and_error("--w <wordlist> is required")
        sys.exit(1)

    ext = []
    if args.x:
        pieces = args.x.split(",")
        for x in pieces:
            ext.append(x.strip())

    codes = None
    if args.sc:
        raw = args.sc.split(",")
        codes = set()
        for s in raw:
            if s.isdigit():
                codes.add(int(s))

    if args.d:
        await scan_directories(args.w, args.d, ext, codes, args.t)
    elif args.s:
        await scan_subdomains(args.w, args.s, args.ip, codes, args.t)
    else:
        usage_and_error("Either --d or --s must be specified")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Scan interrupted by user.{RESET}")