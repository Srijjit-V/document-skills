# HTTPie cram sheet
Source: httpie/cli@3.2.4 (commit 5b604c3) · 2026-11-02
> **If you only read one thing:** in scripts and CI always pass --ignore-stdin. Otherwise piped stdin becomes the request body and key=value items fail with "cannot be mixed".
Legend: ★ most used · ⚠ gotcha

## Request items
| Item | Sends |
|---|---|
| `name=Ada` ★ | JSON string (form with `-f`) |
| `age:=36` ★ | raw JSON: number, bool, list |
| `X-Token:abc` ★ | header; `Accept:` removes it |
| `q==1` | query param `?q=1` |
| `cv@./cv.pdf` | multipart file upload |
| `body:=@data.json` | JSON field from file |
| `'user[roles][]=admin'` | nested JSON |

## Daily commands
| Command | Does |
|---|---|
| `http :3000/api` ★ | GET localhost:3000 |
| `http POST api.io/u name=Ada` | JSON POST |
| `http -v URL` ★ | show request + response |
| `http --offline URL a=1` | print request, don't send |
| `http -f POST URL a=1` | form-encoded |
| `http -d URL` | download to file |
| `https example.org` | default scheme https |

## Output (-p / --print)
| Letter | Prints |
|---|---|
| `H` / `B` | request headers / body |
| `h` / `b` | response headers / body |
| `m` | response metadata (timing) |

Default on a terminal: `hb`. Piped: `b`. `--offline`: `HB`.

## Auth, redirects, sessions
- `-a user:pass` basic; `-a user` prompts for password
- `-A bearer -a TOKEN` → `Authorization: Bearer TOKEN`
- `-F` follow redirects (off by default, max 30)
- `--session=dev` saves headers, auth, cookies per host

## Exit codes
| Code | Meaning |
|---|---|
| 0 | OK, also 4xx/5xx without `--check-status` |
| 1 | error / bad args |
| 2 | timeout |
| 3/4/5 | HTTP 3xx/4xx/5xx with `--check-status` |
| 6 / 7 | too many redirects / plugin error |
| 130 | Ctrl-C |

## Dev loop
```
python3 -m venv venv && . venv/bin/activate
pip install -e '.[test]'
python -m pytest tests/test_cli.py
make codestyle   # flake8
```
- one test: `pytest tests/test_x.py::TestY::test_z`
- most tests hit a local httpbin (pytest-httpbin)

## Where code lives
- flags: `httpie/cli/definition.py`
- defaults, method guess: `cli/argparser.py`
- main loop, exit codes: `core.py`
- sending: `client.py` · output: `output/`
- flow: `raw_main` → `program` → `collect_messages` → `write_message`

## Config and plugins
- dir: `$HTTPIE_CONFIG_DIR`, else `~/.httpie` if present, else `~/.config/httpie` (Windows: `%APPDATA%\httpie`)
- `config.json` `{"default_options": ["--style=fruity"]}` prepends flags to every call
- sessions: `sessions/HOST/NAME.json` in that dir
- `httpie cli plugins install httpie-foo` / `list` / `uninstall`
- plugin classes: `httpie/plugins/base.py` (Auth, Transport, Converter, Formatter)

## Gotchas
- ⚠ Method is guessed: data items or stdin → POST, else GET.
- ⚠ 4xx/5xx exit 0 by default, because only `--check-status` maps status to exit code.
- ⚠ `--download` implies `--follow`, so it saves the final redirect target.
- ⚠ Sessions never store headers starting `Content-` or `If-`; they're per request.
- ⚠ Don't edit `extras/man/*.1`: CI regenerates them on push to master.
- ⚠ Bug report? Paste `http --debug <command>` output.

<!-- Cut to fit:
- Full request-item list (header-from-file `:@`, `==@`, empty header `Header;`): rare; in docs/README.md
- Formatting flags (--pretty, --style, --format-options, --unsorted): cosmetic; in http --help
- SSL/proxy/timeout flags (--verify, --cert, --proxy, --timeout): situational; in http --help
- Contributing rules (tests + docs required, CHANGELOG entry): in docs.md
-->
