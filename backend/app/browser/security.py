"""URL Validation and SSRF Protection for Replicate.AI."""
import ipaddress
import socket
from urllib.parse import urlparse
from typing import Tuple, Optional


DISALLOWED_SCHEMES = {"file", "javascript", "data", "ftp", "gopher", "dict", "ldap"}
ALLOWED_SCHEMES = {"http", "https"}

# Cloud metadata addresses and special IP addresses
METADATA_IPS = {"169.254.169.254", "metadata.google.internal", "metadata.nic"}


def is_private_or_loopback_ip(ip_str: str) -> bool:
    """Check if an IP address is loopback, private, link-local, or reserved."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_loopback
            or ip.is_private
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        )
    except ValueError:
        return True


def validate_url(url: str, allow_localhost: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate a website URL to prevent SSRF and security vulnerabilities.
    
    Returns:
        (is_valid, sanitized_url, error_message)
    """
    if not url or not isinstance(url, str):
        return False, None, "URL cannot be empty."

    url = url.strip()

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, None, f"Malformed URL: {str(e)}"

    if not parsed.scheme:
        # Default to https:// if scheme is missing
        url = "https://" + url
        try:
            parsed = urlparse(url)
        except Exception as e:
            return False, None, f"Malformed URL: {str(e)}"

    scheme = parsed.scheme.lower()
    if scheme in DISALLOWED_SCHEMES:
        return False, None, f"Disallowed URL scheme: '{scheme}'. Only HTTP and HTTPS are permitted."

    if scheme not in ALLOWED_SCHEMES:
        return False, None, f"Invalid URL scheme: '{scheme}'. Expected 'http' or 'https'."

    hostname = parsed.hostname
    if not hostname:
        return False, None, "URL must include a valid host name."

    hostname_lower = hostname.lower()

    if hostname_lower in METADATA_IPS:
        return False, None, "Access to cloud metadata endpoints is prohibited (SSRF protection)."

    # Check localhost restrictions
    if not allow_localhost:
        if hostname_lower in {"localhost", "127.0.0.1", "0.0.0.0", "::1"} or hostname_lower.endswith(".localhost"):
            return False, None, "Localhost addresses are disallowed in production mode."

    # DNS Resolution check to prevent DNS rebinding or private IP target
    try:
        # Resolve hostname to IP
        resolved_ips = socket.getaddrinfo(hostname, None)
        for res in resolved_ips:
            ip_str = res[4][0]
            if not allow_localhost and is_private_or_loopback_ip(ip_str):
                return False, None, f"Resolved IP {ip_str} belongs to a private/internal network (SSRF protection)."
    except socket.gaierror:
        # If host cannot be resolved, we can still report DNS failure
        return False, None, f"Unable to resolve host: '{hostname}'. Check spelling and internet connection."
    except Exception as e:
        return False, None, f"DNS validation error for '{hostname}': {str(e)}"

    return True, url, None
