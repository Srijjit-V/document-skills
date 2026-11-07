# ItsDangerous Cheat Sheet

Signs data so it can safely make a round trip through untrusted hands. **Signed ≠ encrypted: payloads are readable.** Python 3.10+, no dependencies.

## Pick a class

| Need | Class |
|---|---|
| Sign raw bytes/str | `Signer` |
| + timestamp / expiry | `TimestampSigner` |
| Sign objects (JSON) | `Serializer` |
| + expiry | `TimedSerializer` |
| URL/cookie-safe, compressed | `URLSafeSerializer` |
| URL-safe + expiry (most common) | `URLSafeTimedSerializer` |

## Core usage

```python
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
s = URLSafeTimedSerializer(SECRET_KEY, salt="password-reset")
token = s.dumps({"user_id": 42})                 # str
try:
    data = s.loads(token, max_age=3600)          # seconds
    data, ts = s.loads(token, max_age=3600, return_timestamp=True)  # ts: aware UTC datetime
except SignatureExpired as e:  ...               # e.date_signed
except BadSignature as e:      ...               # e.payload = unverified bytes
```

```python
from itsdangerous import Signer, TimestampSigner
Signer(KEY).sign("v")                 # b'v.SIG'
Signer(KEY).unsign(b"v.SIG")          # b'v'  | BadSignature
Signer(KEY).validate(b"v.SIG")        # True/False
TimestampSigner(KEY).unsign(v, max_age=60, return_timestamp=True)
```

## Constructor knobs

| Arg | Default | Meaning |
|---|---|---|
| `secret_key` | — | str/bytes or list (oldest→newest); last signs, all verify |
| `salt` | `b"itsdangerous"` (Serializer) / `b"itsdangerous.Signer"` (Signer) | unique per purpose |
| `serializer` | `json` (URL-safe: compact JSON) | any obj with `dumps`/`loads` |
| `signer_kwargs` | `{}` | `sep`, `digest_method`, `key_derivation`, `algorithm` |
| `fallback_signers` | `[]` | extra signers tried by `loads` only |
| `digest_method` | `hashlib.sha1` (HMAC) | e.g. `hashlib.sha256` |
| `key_derivation` | `"django-concat"` | `concat`, `hmac`, `none` |
| `sep` | `b"."` | must not be in `A-Za-z0-9-_=` |

## Serializer methods

`dumps(obj, salt=None)` · `loads(s, salt=None)` · `dump(obj, f)` · `load(f)` · `loads_unsafe(s) → (ok, payload)` (debug only) · `load_payload(bytes)` · `make_signer(salt)`
**Timed:** `loads(s, max_age=None, return_timestamp=False, salt=None)` — pass `salt=` by keyword.

## Exceptions

```
BadData (.message)
├─ BadPayload (.original_error)          deserialization failed
└─ BadSignature (.payload)               tampered / wrong key / wrong salt
   ├─ BadHeader                          legacy
   └─ BadTimeSignature (.date_signed)    timed sig bad / bad timestamp
      └─ SignatureExpired                age > max_age (or in future)
```
Catch `SignatureExpired` before `BadSignature`.

## Token formats

`Signer`: `value.SIG` · `TimestampSigner`: `value.TS.SIG` · `URLSafe*`: `B64(json)[.TS].SIG`; leading `.` = zlib-compressed.

## Recipes

```python
URLSafeSerializer(["old-key", "new-key"])                        # key rotation
URLSafeSerializer(KEY, signer_kwargs={"digest_method": hashlib.sha256},
                  fallback_signers=[{"digest_method": hashlib.sha1}])  # digest upgrade
python3 -c 'import os; print(os.urandom(16).hex())'              # generate a key
```

## Gotchas

- No `max_age` → never expires. Tokens are replayable until expiry; enforce one-time use server-side.
- Different salt per purpose, or tokens cross contexts.
- Never use `pickle` as serializer.
- `SignatureExpired` skips fallback signers.
- No `__version__`: use `importlib.metadata.version("itsdangerous")`.

## Dev commands

`uv sync` · `uv run pytest` · `uv run tox run -e typing` (mypy+pyright) · `-e style` (pre-commit/ruff) · `-e docs` · changelog → `CHANGES.rst` "Unreleased"
