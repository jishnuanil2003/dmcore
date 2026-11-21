#!/usr/bin/env python3
"""
scripts/smtp_diag.py
Diagnostic tool for testing SMTP connectivity to Gmail (ports 587 and 465).
Redacts all passwords and AUTH data from debug output and stdout/stderr.
"""

import os
import sys
import re
import socket
import ssl
import smtplib
from pathlib import Path

# Locate project base and settings
current_dir = Path(__file__).resolve().parent
candidates = [
    current_dir.parent,          # e.g. D:\dmcore\dmcore or D:\dmcore
    current_dir.parent / "dmcore", # e.g. D:\dmcore\dmcore
]

project_dir = None
for c in candidates:
    if (c / "manage.py").exists() and (c / "dmcore" / "settings.py").exists():
        project_dir = c
        break

if not project_dir:
    # fallback
    project_dir = Path(r"D:\dmcore\dmcore")

if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmcore.settings')

import django
django.setup()
from django.conf import settings


def redact_line(line: str, secret: str = "") -> str:
    """Redacts AUTH commands and any occurrence of password/secret."""
    if not line:
        return line
    res = line
    if secret and secret in res:
        res = res.replace(secret, "[REDACTED_PASSWORD]")
    # Redact AUTH command and subsequent parameters / base64
    res = re.sub(r"(AUTH\s+\S+)(\s+.*)?", r"\1 [REDACTED_AUTH_DATA]", res, flags=re.IGNORECASE)
    # Redact send: of base64 looking tokens after auth
    if "send:" in res and any(tok in res for tok in ["AUTH", "auth"]):
        res = "send: 'AUTH [REDACTED]'\n"
    return res


class RedactingDebugPrinter:
    def __init__(self, secret: str = ""):
        self.secret = secret

    def print_debug(self, *args):
        msg = " ".join(str(a) for a in args)
        redacted = redact_line(msg, self.secret)
        # Extra check: if anything looks like a base64 payload during auth
        if self.secret and self.secret in redacted:
            redacted = redacted.replace(self.secret, "[REDACTED_PASSWORD]")
        print(f"  [DEBUG] {redacted}", file=sys.stderr)


def test_dns(host: str):
    print("=" * 60)
    print(f"DNS RESOLUTION: {host}")
    print("=" * 60)
    try:
        addr_info = socket.getaddrinfo(host, None)
        ips = sorted(list(set(item[4][0] for item in addr_info)))
        print(f"DNS Resolution: OK")
        print(f"Resolved IPs: {ips}")
        return True, ips
    except Exception as e:
        print(f"DNS Resolution FAILED: {type(e).__name__}: {e}")
        return False, []


def test_smtp_587(host: str, user: str, password: str, timeout: int = 20):
    print("\n" + "=" * 60)
    print(f"TEST 1: SMTP port 587 + STARTTLS + login (timeout={timeout}s)")
    print("=" * 60)

    debug_printer = RedactingDebugPrinter(password)
    smtp = smtplib.SMTP(timeout=timeout)
    smtp._print_debug = debug_printer.print_debug
    smtp.set_debuglevel(1)

    # 1. TCP Connect
    try:
        code, msg = smtp.connect(host, 587)
        print(f"1. TCP Connect: OK (code={code}, msg={msg.decode('utf-8', 'ignore') if isinstance(msg, bytes) else msg})")
    except Exception as e:
        print(f"1. TCP Connect: FAILED ({type(e).__name__}: {e})")
        return False, f"TCP Connect Failed: {type(e).__name__}: {e}"

    # 2. EHLO before TLS
    try:
        smtp.ehlo()
    except Exception as e:
        print(f"2. Pre-TLS EHLO: FAILED ({type(e).__name__}: {e})")

    # 3. STARTTLS
    try:
        context = ssl.create_default_context()
        smtp.starttls(context=context)
        print("2. TLS (STARTTLS): OK")
    except Exception as e:
        print(f"2. TLS (STARTTLS): FAILED ({type(e).__name__}: {e})")
        try:
            smtp.close()
        except Exception:
            pass
        return False, f"TLS Failed: {type(e).__name__}: {e}"

    # 4. EHLO after TLS & capabilities
    try:
        code, resp = smtp.ehlo()
        print(f"3. EHLO after TLS: OK")
        print(f"   EHLO Capabilities: {list(smtp.esmtp_features.keys())}")
    except Exception as e:
        print(f"3. EHLO after TLS: FAILED ({type(e).__name__}: {e})")

    # 5. AUTH / login
    try:
        code, resp = smtp.login(user, password)
        resp_str = resp.decode('utf-8', 'ignore') if isinstance(resp, bytes) else str(resp)
        print(f"4. AUTH Result: OK (code={code}, message={resp_str})")
        smtp.quit()
        return True, "AUTH OK"
    except Exception as e:
        print(f"4. AUTH Result: FAILED")
        print(f"   Exact Exception: {type(e).__name__}: {e}")
        try:
            smtp.close()
        except Exception:
            pass
        return False, f"AUTH FAILED: {type(e).__name__}: {e}"


def test_smtp_465(host: str, user: str, password: str, timeout: int = 20):
    print("\n" + "=" * 60)
    print(f"TEST 2: SMTP_SSL port 465 + login (timeout={timeout}s)")
    print("=" * 60)

    debug_printer = RedactingDebugPrinter(password)
    context = ssl.create_default_context()

    try:
        smtp = smtplib.SMTP_SSL(host=host, port=465, timeout=timeout, context=context)
        smtp._print_debug = debug_printer.print_debug
        smtp.set_debuglevel(1)
        print("1. TCP Connect & TLS Handshake (port 465): OK")
    except Exception as e:
        print(f"1. TCP Connect / TLS Handshake: FAILED ({type(e).__name__}: {e})")
        return False, f"Connect/TLS Failed: {type(e).__name__}: {e}"

    # 2. EHLO & capabilities
    try:
        code, resp = smtp.ehlo()
        print(f"2. EHLO: OK")
        print(f"   EHLO Capabilities: {list(smtp.esmtp_features.keys())}")
    except Exception as e:
        print(f"2. EHLO: FAILED ({type(e).__name__}: {e})")

    # 3. AUTH / login
    try:
        code, resp = smtp.login(user, password)
        resp_str = resp.decode('utf-8', 'ignore') if isinstance(resp, bytes) else str(resp)
        print(f"3. AUTH Result: OK (code={code}, message={resp_str})")
        smtp.quit()
        return True, "AUTH OK"
    except Exception as e:
        print(f"3. AUTH Result: FAILED")
        print(f"   Exact Exception: {type(e).__name__}: {e}")
        try:
            smtp.close()
        except Exception:
            pass
        return False, f"AUTH FAILED: {type(e).__name__}: {e}"


def main():
    host = settings.EMAIL_HOST or "smtp.gmail.com"
    user = settings.EMAIL_HOST_USER or ""
    raw_pw = settings.EMAIL_HOST_PASSWORD or ""
    # strip spaces from the password as instructed
    pw = raw_pw.replace(" ", "")

    print(f"Config from settings:")
    print(f"  EMAIL_HOST: {repr(host)}")
    print(f"  EMAIL_HOST_USER: {repr(user)}")
    print(f"  EMAIL_HOST_PASSWORD len: {len(pw)} (is_set: {bool(pw)})")

    # DNS check
    dns_ok, ips = test_dns(host)

    # Test 587
    res_587, msg_587 = test_smtp_587(host, user, pw, timeout=20)

    # Test 465
    res_465, msg_465 = test_smtp_465(host, user, pw, timeout=20)

    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print(f"DNS Resolution: {'SUCCESS' if dns_ok else 'FAILURE'}")
    print(f"Port 587 (STARTTLS): {'SUCCESS' if res_587 else 'FAILURE'} -> {msg_587}")
    print(f"Port 465 (SSL):      {'SUCCESS' if res_465 else 'FAILURE'} -> {msg_465}")

    if res_587 and res_465:
        print("Conclusion: Both 587 and 465 succeed with the given credentials.")
    elif res_465 and not res_587:
        print("Conclusion: (B) Port 587 is interfered with / failing, but Port 465 works.")
    elif not res_587 and not res_465:
        if "AuthenticationError" in msg_587 or "AuthenticationError" in msg_465 or "ServerDisconnected" in msg_587:
            print("Conclusion: (C) Both fail at AUTH (Google account / App Password / Workspace admin policy or network/antivirus block).")
        else:
            print("Conclusion: Failed during connect/TLS (network or config error).")


if __name__ == "__main__":
    main()
