---
name: bcrypt-passlib-compat
description: bcrypt v4+ is incompatible with passlib's bcrypt backend due to missing __about__ module
---

Using `passlib[bcrypt]` with bcrypt v4+ raises `AttributeError: module 'bcrypt' has no attribute '__about__'` and `ValueError: password cannot be longer than 72 bytes`.

**Why:** passlib's bcrypt backend probes `bcrypt.__about__.__version__` which was removed in bcrypt v4.0. Replit's environment has bcrypt v5.x installed.

**How to apply:** Use `bcrypt` directly instead of passlib CryptContext for password hashing:

```python
import bcrypt

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
```
