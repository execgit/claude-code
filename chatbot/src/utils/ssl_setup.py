import os
from pathlib import Path
from config.settings import settings

def setup_ssl_certificates():
    """
    Set up SSL certificates for self-hosted LLM servers.
    Sets REQUESTS_CA_BUNDLE environment variable if CA certificate path is provided.
    """
    if not settings.ca_cert_path:
        return
        
    ca_cert_path = Path(settings.ca_cert_path)
    
    if not ca_cert_path.exists():
        print(f"⚠️  CA certificate file not found: {ca_cert_path}")
        return
        
    # Set REQUESTS_CA_BUNDLE environment variable
    os.environ["REQUESTS_CA_BUNDLE"] = str(ca_cert_path.absolute())
    print(f"✅ SSL certificate configured: {ca_cert_path}")
    
    # Also set CURL_CA_BUNDLE for completeness
    os.environ["CURL_CA_BUNDLE"] = str(ca_cert_path.absolute())
    
def get_ssl_verify_setting():
    """
    Get the SSL verify setting for requests.
    Returns the CA bundle path if set, otherwise True for default verification.
    """
    if settings.ca_cert_path:
        ca_cert_path = Path(settings.ca_cert_path)
        if ca_cert_path.exists():
            return str(ca_cert_path.absolute())
    return True