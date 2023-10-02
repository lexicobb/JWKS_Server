# Author:      Alexia Cobb (alexiacobb@my.unt.edu)
# EUID:		   asc0223
# Assignment:  JWKS Server
# Class:       CSCE 3550
# Instructor:  Dr. Hochstetler
# Due Date:    1 October 2023

import http.server
import socketserver
import json
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# Generate an RSA private key
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Serialize the private key to PEM format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

# Create a JSON Web Key (JWK) from the private key
jwk_data = {
    "kty": "RSA",
    "kid": "sampleKeyId",
    "use": "sig",
    "n": private_key.public_key().public_numbers().n,
    "e": private_key.public_key().public_numbers().e,
}

# Create a JWT using the private key
jwt_payload = {"sub": "1234567890", "name": "John Doe"}
jwt_token = jwt.encode(jwt_payload, private_pem, algorithm="RS256")

# Custom request handler
class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/.well-known/jwks.json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"keys": [jwk_data]}).encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/auth':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Authentication endpoint')
        else:
            super().do_POST()

# Set up the server
with socketserver.TCPServer(("0.0.0.0", 8080), MyHandler) as httpd:
    print("Server started on port 8080")
    httpd.serve_forever()
