# SSL Certificates Directory

This directory is for storing SSL certificates needed for self-hosted LLM servers with self-signed certificates.

## Usage

1. Place your CA certificate file (e.g., `ca-cert.pem`) in this directory
2. Set the `LLM_CA_CERT_PATH` environment variable to point to the certificate file:
   ```
   LLM_CA_CERT_PATH=/app/certs/ca-cert.pem
   ```
3. The chatbot will automatically set the `REQUESTS_CA_BUNDLE` environment variable to use this certificate

## Docker Usage

The `certs` directory is mounted as a read-only volume in the Docker container at `/app/certs`.

## Example

```bash
# Copy your CA certificate
cp /path/to/your/ca-cert.pem ./certs/

# Set environment variable
export LLM_CA_CERT_PATH=/app/certs/ca-cert.pem

# Or in .env file
echo "LLM_CA_CERT_PATH=/app/certs/ca-cert.pem" >> .env
```