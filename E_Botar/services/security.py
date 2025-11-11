from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Tuple
from django.conf import settings


def _get_secret_key_bytes() -> bytes:
    raw = getattr(settings, 'SECRET_KEY', '')
    if not raw:
        raise RuntimeError('SECRET_KEY is not configured')
    # Derive a fixed-length key
    import hashlib
    return hashlib.sha256(raw.encode('utf-8')).digest()


def encrypt_string(plaintext: str) -> str:
    """Lightweight symmetric encryption for sensitive at-rest strings.

    Note: For production-grade crypto, use Fernet/NaCl. Here we use XOR + IV and base64
    for a simple reversible scheme that avoids extra deps.
    """
    if plaintext is None:
        return ''
    key = _get_secret_key_bytes()
    iv = os.urandom(16)
    data = plaintext.encode('utf-8')
    out = bytearray()
    for i, b in enumerate(data):
        out.append(b ^ key[i % len(key)] ^ iv[i % len(iv)])
    return base64.urlsafe_b64encode(iv + bytes(out)).decode('ascii')


def decrypt_string(ciphertext: str) -> str:
    if not ciphertext:
        return ''
    raw = base64.urlsafe_b64decode(ciphertext.encode('ascii'))
    iv, payload = raw[:16], raw[16:]
    key = _get_secret_key_bytes()
    out = bytearray()
    for i, b in enumerate(payload):
        out.append(b ^ key[i % len(key)] ^ iv[i % len(iv)])
    return bytes(out).decode('utf-8')


@dataclass(frozen=True)
class AnonymizedReceipt:
    receipt_code: str
    hash_suffix: str


def generate_anonymous_receipt(receipt_code: str) -> AnonymizedReceipt:
    """Return a display-safe anonymized receipt reference.

    We do not store direct mapping from user->receipt exposed publicly.
    """
    import hashlib
    h = hashlib.sha256(receipt_code.encode('utf-8')).hexdigest()
    # show only last 8 chars as public proof code
    return AnonymizedReceipt(receipt_code=receipt_code, hash_suffix=h[-8:])


def encrypt_vote_data(vote_data: dict) -> str:
    """Encrypt vote data for secure storage"""
    import json
    json_data = json.dumps(vote_data)
    return encrypt_string(json_data)


def decrypt_vote_data(encrypted_data: str) -> dict:
    """Decrypt vote data"""
    import json
    json_data = decrypt_string(encrypted_data)
    return json.loads(json_data)


def generate_vote_receipt_code() -> str:
    """Generate a unique vote receipt code"""
    import uuid
    return str(uuid.uuid4())


def validate_vote_integrity(vote_data: dict) -> bool:
    """Validate vote data integrity"""
    required_fields = ['election_id', 'position_id', 'candidate_id', 'voter_id']
    return all(field in vote_data for field in required_fields)


# --- Security module helpers (used by security_module) ---
def check_security_threats() -> list[dict]:
    """Lightweight placeholder threat checks.
    Returns a list of detected threat summaries. Replace with real logic as needed.
    """
    return []


def generate_security_report(events, attempts) -> dict:
    """Generate a simple security report structure for rendering."""
    try:
        total_events = events.count() if hasattr(events, 'count') else len(events)
        total_attempts = attempts.count() if hasattr(attempts, 'count') else len(attempts)
    except Exception:
        total_events = 0
        total_attempts = 0
    return {
        'summary': {
            'total_events': total_events,
            'total_access_attempts': total_attempts,
        },
        'by_severity': {},
        'top_ip_addresses': [],
    }


def secure_file_upload(file, allowed_extensions=None, max_size=None):
    """Secure file upload validation"""
    if allowed_extensions is None:
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    
    if max_size is None:
        max_size = 5 * 1024 * 1024  # 5MB
    
    # Check file extension
    import os
    file_ext = os.path.splitext(file.name)[1].lower()
    if file_ext not in allowed_extensions:
        raise ValueError(f"File type {file_ext} not allowed")
    
    # Check file size
    if file.size > max_size:
        raise ValueError(f"File size {file.size} exceeds maximum {max_size}")
    
    return True
