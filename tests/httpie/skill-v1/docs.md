# Start here: HTTPie CLI

HTTPie is a command-line HTTP client (`http`, `https`) built on Python `requests`, plus a small manager command (`httpie`) for plugins and sessions. This repo is version 3.2.4 (`httpie/__init__.py`), needs Python 3.7+, and is BSD licensed.

| Path | What lives there |
|---|---|
| `httpie/core.py` | `main()` and `program()`: error handling, exit codes, the request/response loop |
| `httpie/cli/definition.py` | every CLI flag (help text and man pages are generated from it) |
| `httpie/cli/argparser.py` | defaults the parser applies: method guessing, URL shorthand, output options |
| `httpie/cli/constants.py` | item separators (`=`, `:=`, `==`, `@`…) and `--print` letters |
| `httpie/client.py` | builds the `requests` session and sends requests |
| `httpie/output/` | formatting, colors, streaming to the terminal |
| `httpie/sessions.py`, `config.py` | sessions and `config.json` |
| `httpie/plugins/`, `httpie/manager/` | plugin API and the `httpie` command |
| `tests/` | pytest suite, one file per feature (`test_uploads.py`, `test_sessions.py`…) |

## Day 1: run it

```bash
python3 -m venv venv && source venv/bin/activate
pip install -e '.[test]'      # or: make install  (adds the dev/lint extras)
http --version                # 3.2.4
python -m pytest tests/test_cli.py tests/test_offline.py tests/test_exit_status.py
```

The subset above ran in 2 seconds here (56 passed). The full suite is `make test`; `make codestyle` runs flake8, and `make test-cover` adds coverage. Most tests use a local httpbin server from `pytest-httpbin`, so they need no network. Run one test with `python -m pytest tests/test_uploads.py::TestMultipartFormDataFileUpload::test_upload_ok`.

## Use it

Arguments after the URL are request items. The separator decides where each one goes:

| Item | Becomes | Example |
|---|---|---|
| `key=value` | JSON string field (form field with `--form`) | `name=Ada` |
| `key:=json` | raw JSON value | `age:=36`, `tags:='["a"]'` |
| `Header:value` | request header (`Header:` removes it) | `X-Token:abc` |
| `key==value` | query parameter | `q==1` |
| `field@path` | file upload (multipart) | `cv@./cv.pdf` |
| `key=@path`, `key:=@path` | field from file contents | `body:=@data.json` |

```bash
http --offline pie.dev/post name=Ada age:=36 X-Token:abc q==1
```

`--offline` builds and prints the request without sending it. The command above printed `POST /post?q=1` with `Content-Type: application/json` and body `{"name": "Ada", "age": 36}`. Brackets nest JSON: `'user[roles][]=admin'` sends `{"user": {"roles": ["admin"]}}`.

Common flags:

| Flag | Does |
|---|---|
| `-v` | print request and response |
| `-p HBhbm` / `--print` | choose output: request Headers/Body, response headers/body, metadata |
| `-f`, `--form` | send form data instead of JSON |
| `-a user:pass`, `-A bearer` | auth; omit `:pass` to be prompted |
| `-F`, `--follow` | follow redirects (off by default) |
| `--check-status` | exit non-zero on 3xx/4xx/5xx |
| `-d`, `--download` | save body to a file (implies `--follow`) |
| `--session=NAME` | persist headers, auth, cookies between calls |

## How a request flows

`http` → `httpie/__main__.py:main` → `core.main` → `core.raw_main`. `raw_main` loads plugins, prepends `default_options` from `config.json`, parses args with `cli/definition.py:parser`, then calls `core.program`. `program` iterates `client.collect_messages()`, which yields each request and response (redirects included), and passes each to `output/writer.write_message`. Exceptions are turned into exit codes in `raw_main`, not where they're raised.

Exit codes (`httpie/status.py`):

| Code | Meaning |
|---|---|
| 0 | success (also for 4xx/5xx unless `--check-status`) |
| 1 | generic error, bad arguments |
| 2 | timeout |
| 3 / 4 / 5 | HTTP 3xx / 4xx / 5xx, only with `--check-status` or `--download` |
| 6 | too many redirects |
| 7 | plugin error |
| 130 | Ctrl-C |

## Behavior that surprises people

- Piped stdin becomes the body. If stdin is not a terminal (scripts, CI, editors, agents), HTTPie reads it as the body, and `key=value` items then fail with "Request body … and request data … cannot be mixed". Add `--ignore-stdin` in scripts. CI does the same (`.github/workflows/docs-deploy.yml`).
- The method is guessed. No method plus data items or stdin means `POST`; otherwise `GET` (`argparser.py:_guess_method`).
- Output depends on where stdout goes. On a terminal you get response headers and body; redirected to a file or pipe you get only the body; with `--offline` you get the request.
- URL shorthand. `:3000/api` means `http://localhost:3000/api`. Run as `https`, the default scheme is `https://`.
- Config location. `$HTTPIE_CONFIG_DIR`, else `%APPDATA%\httpie` on Windows, else `~/.httpie` if it exists, else `$XDG_CONFIG_HOME/httpie` (default `~/.config/httpie`). Sessions are stored in `sessions/<host>/<name>.json` inside it.
- Sessions drop some headers. Headers starting with `Content-` or `If-` are never saved (`sessions.py:35`).

## Contribute

Add a flag in `httpie/cli/definition.py`, apply its default or validation in `argparser.py`, then add a test next to the feature in `tests/`. Don't hand-edit `extras/man/*.1`: CI regenerates man pages and install docs (`make content`) on every push to `master`. PRs that change behavior need tests and a docs change in `docs/README.md` (the full user manual), and should add a `CHANGELOG.md` entry. For bug reports, include the output of `http --debug <your command>`.

Plugins subclass `AuthPlugin`, `TransportPlugin`, `ConverterPlugin`, or `FormatterPlugin` in `httpie/plugins/base.py`; manage them with `httpie cli plugins install|list|upgrade|uninstall`.
