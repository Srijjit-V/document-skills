# itsdangerous: start here

itsdangerous signs data with HMAC so it is safe to hand to an untrusted party (a browser cookie, an emailed link, a URL) and later prove it came back unchanged. It signs; it does not encrypt. Anyone holding a token can base64-decode and read the payload.

Requires Python 3.10+, no runtime dependencies. This page covers version 2.3.0.dev (`pyproject.toml`).

## Sign and verify a token

```python
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

s = URLSafeTimedSerializer("long-random-secret", salt="password-reset")
token = s.dumps({"user_id": 42})        # str, safe for URLs

try:
    data = s.loads(token, max_age=3600)  # {'user_id': 42}
except SignatureExpired:
    ...  # valid signature, older than 1 hour
except BadSignature:
    ...  # tampered, wrong key, or wrong salt
```

`loads` only returns data whose signature checks out. Check `SignatureExpired` before `BadSignature`, because it is a subclass.

## Pick a class

All are importable from the top-level `itsdangerous` package (`src/itsdangerous/__init__.py`).

| Class | Input | Output | Expires | Use for |
|---|---|---|---|---|
| `URLSafeTimedSerializer` | any JSON value | URL-safe `str` | yes, with `max_age` | reset links, email confirmation, most cases |
| `URLSafeSerializer` | any JSON value | URL-safe `str` | no | long-lived tokens in URLs or cookies |
| `Serializer` / `TimedSerializer` | any JSON value | raw JSON + signature `str` | Timed only | non-URL storage, custom serializers |
| `Signer` / `TimestampSigner` | `str` or `bytes` | `bytes` | Timestamp only | signing a value you already have as bytes |

Serializers wrap a signer: `dumps` serializes, then signs; `loads` verifies, then deserializes. The URL-safe variants use compact JSON, zlib-compress when that makes the token shorter (the payload then starts with `.`), and base64-encode (`url_safe.py:55`).

## Secret key and salt

The **secret key** is what makes signatures unforgeable. Use a long random value and load it from the environment, never from source control:

```bash
python3 -c 'import os; print(os.urandom(16).hex())'
```

Changing the key invalidates every token. To rotate without a cutoff, pass a list ordered oldest to newest: the last key signs, and verification tries all of them, newest first (`signer.py:236`).

The **salt** separates contexts. It need not be secret, only different per purpose. Without distinct salts, a token signed for "activate account" also verifies as "upgrade account" if both sign the same user id. Defaults differ by class: serializers use `b"itsdangerous"`, signers use `b"itsdangerous.Signer"`, so a token from one does not verify with the other.

## Errors

Every library error derives from `BadData` (`exc.py`).

| Exception | Raised when | Useful attributes |
|---|---|---|
| `BadSignature` | signature missing or wrong | `payload`: the unverified bytes |
| `BadTimeSignature` | timed signature invalid or timestamp malformed | `payload`, `date_signed` |
| `SignatureExpired` | age > `max_age`, or timestamp is in the future | `payload`, `date_signed` (aware UTC) |
| `BadPayload` | signature valid but deserializing failed | `original_error` |

`BadPayload` is not a subclass of `BadSignature`. Catch `BadData` if you want both.

To inspect a token that failed verification, for debugging only, use `loads_unsafe(token)`; it returns `(signature_ok, payload)` and never raises. Do not use it with a pickle-based serializer, because loading unverified pickle runs attacker code.

## Change signing parameters without breaking old tokens

The default HMAC digest is SHA-1, which is safe inside HMAC. To move to SHA-512 and still accept existing SHA-1 tokens, add a fallback signer:

```python
import hashlib
from itsdangerous import URLSafeSerializer

s = URLSafeSerializer(
    "secret",
    signer_kwargs={"digest_method": hashlib.sha512},
    fallback_signers=[{"digest_method": hashlib.sha1}],
)
```

New tokens use SHA-512 and are longer, which matters in cookies. `fallback_signers` items can be a dict of signer kwargs, a `Signer` subclass, or a `(SignerClass, kwargs)` tuple (`serializer.py:297`). For a timed serializer, an expired token stops the search; fallbacks are not tried (`timed.py:213`).

## Gotchas

- `max_age` is silently ignored by `Serializer` and `URLSafeSerializer`: their `loads` accepts and discards extra keyword arguments (`serializer.py:328`). Expiry needs a `Timed` class.
- A timed `loads` without `max_age` never expires the token.
- `Signer.unsign` returns `bytes` even when you signed a `str`.
- `sep` cannot be a base64 character (letters, digits, `-_=`); the constructor raises `ValueError`.
- Values that JSON cannot encode (sets, datetimes) raise `TypeError` from `dumps`. Pass `serializer_kwargs={"default": ...}` or a custom serializer object with `dumps`/`loads`.
- FIPS builds without SHA-1 fail at first sign, not at import. Set `digest_method` explicitly there.

## Work on the code

| Path | Contents |
|---|---|
| `src/itsdangerous/signer.py` | `Signer`, `HMACAlgorithm`, key derivation |
| `src/itsdangerous/timed.py` | `TimestampSigner`, `TimedSerializer`, expiry checks |
| `src/itsdangerous/serializer.py` | `Serializer`, fallback signers, `loads_unsafe` |
| `src/itsdangerous/url_safe.py` | URL-safe mixin: compact JSON, zlib, base64 |
| `src/itsdangerous/exc.py` | exception hierarchy |
| `tests/test_itsdangerous/` | one test file per module |
| `docs/` | Sphinx source for the published docs |

Run the tests. Verified with Python 3.11 and pip (297 passed):

```bash
python3 -m venv .venv
.venv/bin/pip install -e . pytest freezegun
.venv/bin/pytest -q
```

CI uses uv and tox. These commands come from `pyproject.toml` and `.github/workflows/tests.yaml` and were not run here:

```bash
uv run --locked tox run -e py3.11   # [unverified]
uv run --locked tox run -e typing   # mypy + pyright [unverified]
uv run --locked tox run -e style    # pre-commit: ruff, formatting [unverified]
```

pytest runs with warnings as errors (`filterwarnings = ["error"]`), so a new deprecation warning fails the suite. Record user-visible changes in `CHANGES.rst` under the unreleased version.
