"""
verifier.py — Domain health and email MX record verification.

Two lightweight checks:
  1. verify_domain()       — Does the website respond with a 2xx/3xx?
  2. verify_email_domain() — Does the email's domain have MX records?
"""

import re
import httpx
import dns.resolver
import dns.exception


def verify_domain(raw_url: str, timeout: float = 6.0) -> dict:
    """
    Check if a website domain is live by making a real HTTP request.

    Args:
        raw_url: Full URL or bare domain (e.g. 'https://acme.com' or 'acme.com').
        timeout: Request timeout in seconds.

    Returns:
        dict with keys: domain_live, status_code, redirect_url, error
    """
    if not raw_url or raw_url.strip() in ("N/A", ""):
        return {"domain_live": False, "status_code": None, "redirect_url": None, "error": "No URL provided"}

    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    match = re.match(r"(https?://[^/]+)", url)
    clean_url = match.group(1) if match else url

    for scheme_url in (clean_url, clean_url.replace("https://", "http://")):
        try:
            with httpx.Client(
                timeout=timeout, follow_redirects=True, verify=False,
                headers={"User-Agent": "LeadOptimizer/1.0"},
            ) as client:
                resp = client.get(scheme_url)
                return {
                    "domain_live":  resp.status_code < 400,
                    "status_code":  resp.status_code,
                    "redirect_url": str(resp.url) if str(resp.url) != scheme_url else None,
                    "error":        None,
                }
        except (httpx.TimeoutException, httpx.RequestError):
            continue

    return {"domain_live": False, "status_code": None, "redirect_url": None, "error": "Unreachable"}


def verify_email_domain(email: str, timeout: float = 5.0) -> dict:
    """
    Check whether the domain part of an email has valid MX records.

    Args:
        email:   Email address to check.
        timeout: DNS resolution timeout in seconds.

    Returns:
        dict with keys: mx_valid, mx_hosts, error
    """
    if not email or "@" not in email:
        return {"mx_valid": False, "mx_hosts": [], "error": "Invalid email format"}

    domain = email.strip().split("@")[-1].lower()
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout
    resolver.timeout  = timeout

    try:
        answers  = resolver.resolve(domain, "MX")
        mx_hosts = sorted([str(r.exchange).rstrip(".") for r in answers])
        return {"mx_valid": True, "mx_hosts": mx_hosts, "error": None}
    except dns.resolver.NXDOMAIN:
        return {"mx_valid": False, "mx_hosts": [], "error": "Domain does not exist"}
    except dns.resolver.NoAnswer:
        return {"mx_valid": False, "mx_hosts": [], "error": "No MX records found"}
    except dns.exception.Timeout:
        return {"mx_valid": False, "mx_hosts": [], "error": "DNS timeout"}
    except Exception as exc:
        return {"mx_valid": False, "mx_hosts": [], "error": str(exc)}
