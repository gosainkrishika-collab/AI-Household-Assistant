import hashlib
import hmac
import os

from fastapi import Header, HTTPException

import database


# ---------------- Passwords ----------------
# We never store the real password — only a salted hash of it.
def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000)
    return salt.hex() + "$" + digest.hex()


def check_password(password, stored):
    salt_hex, digest_hex = stored.split("$")
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 200_000)
    return hmac.compare_digest(digest.hex(), digest_hex)


# ---------------- "Who is making this request?" ----------------
# The frontend sends:  Authorization: Bearer <token>
# Any route that lists `Depends(get_token)` / `Depends(get_current_user)`
# is automatically protected.
def get_token(authorization: str = Header(default="")):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Please log in")
    return authorization[len("Bearer "):]


def get_current_user(authorization: str = Header(default="")):
    token = get_token(authorization)
    user = database.get_user_by_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Session expired, please log in again")
    return user
