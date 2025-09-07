"""Network utilities for eyelet."""

import random
import socket


def is_port_available(host: str, port: int) -> bool:
    """Check if a port is available for binding.
    
    Args:
        host: Host to check (usually 'localhost' or '127.0.0.1')
        port: Port number to check
        
    Returns:
        True if port is available, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except (OSError, socket.error):
        return False


def find_available_port(host: str, preferred_port: int = 443) -> int:
    """Find an available port, starting with preferred port.
    
    Args:
        host: Host to bind to
        preferred_port: Preferred port to try first (default: 443)
        
    Returns:
        Available port number
    """
    # First try the preferred port
    if is_port_available(host, preferred_port):
        return preferred_port
    
    # Fall back to random port in range 2048-65535
    max_attempts = 100
    for _ in range(max_attempts):
        port = random.randint(2048, 65535)
        if is_port_available(host, port):
            return port
    
    # If all random attempts fail, let the OS choose
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, 0))  # 0 means let OS choose
        return sock.getsockname()[1]


def get_sslip_url(host: str, port: int, scheme: str = "https") -> str:
    """Generate sslip.io URL for local service.
    
    Args:
        host: Host address (e.g., '127.0.0.1', 'localhost')
        port: Port number
        scheme: URL scheme ('http' or 'https')
        
    Returns:
        sslip.io URL
    """
    if host in ('localhost', '127.0.0.1'):
        # Convert to sslip.io format
        sslip_host = "127-0-0-1.sslip.io"
    else:
        # Convert IP dots to dashes for other IPs
        sslip_host = host.replace('.', '-') + ".sslip.io"
    
    # Don't include port 443 for HTTPS or port 80 for HTTP
    if (scheme == "https" and port == 443) or (scheme == "http" and port == 80):
        return f"{scheme}://{sslip_host}"
    else:
        return f"{scheme}://{sslip_host}:{port}"