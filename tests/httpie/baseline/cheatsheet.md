# HTTPie CLI Cheat Sheet (v3.2.4)

`http [flags] [METHOD] URL [ITEM ...]`. Use `https` for an https:// default. Manager command: `httpie`.

## Basics
| Command | Does |
|---|---|
| `http pie.dev/get` | GET (default when there's no body) |
| `http pie.dev/post a=1` | POST JSON (data present → POST) |
| `http PUT pie.dev/put a=1` | Explicit method |
| `http :3000/x` | → `http://localhost:3000/x` |
| `https example.org` | Default scheme https |
| `http --offline URL a=1` | Prints the request, doesn't send it |

## Request items
| Item | Meaning |
|---|---|
| `H:v` / `H;` / `H:` | Header / empty header / remove default header |
| `H:@f` | Header value read from a file |
| `q==v` / `q==@f` | Query param / query param read from a file |
| `k=v` | String field |
| `k:=json` | Raw JSON (`n:=1 ok:=true l:='[1,2]'`) |
| `k=@f` / `k:=@f.json` | Field read from a file (text / JSON) |
| `f@path[;type=mime]` | File upload (multipart) |
| `a[b][]=x  a[c]:=1` | Nested JSON |
| `@file` (alone) | File contents as the body |
| `\` | Escape a separator: `'a\==b'` |

## Body
| Flag | Effect |
|---|---|
| `-j` (default) | JSON object |
| `-f` | Form (multipart if files are present) |
| `--multipart [--boundary=X]` | Always multipart |
| `--raw 'txt'` | Raw body |
| `cmd \| http POST URL` | Body from stdin |
| `-x` / `-xx` | Deflate-compress (`-xx` forces it) |
| `--chunked` | Chunked transfer encoding |

## Output
| Flag | Prints |
|---|---|
| `-p HBhbm` | Request **H**eaders/**B**ody, response **h**eaders/**b**ody, **m**eta |
| `-h` / `-b` / `-m` | Response headers / body / meta only |
| `-v` / `-vv` | Request + response (+meta) |
| `--all`, `-P WHAT` | Show redirects / control what's printed for them |
| `-q` / `-qq` | Quiet / also hide warnings |
| `-S` | Stream line by line |
| `-o FILE` | Write output to a file |
| `--pretty=all\|colors\|format\|none` | Formatting |
| `-s monokai` | Color style |
| `--unsorted` / `--sorted` | Turn key/header sorting off / on |
| `--format-options=json.indent:2` | Fine-tune formatting |

Defaults: `hb` on a TTY, `b` when redirected, `HB` with `--offline`.

## Download
`http -d URL` · `http -d -o f.zip URL` · `http -dco f.zip URL` (resume). `-d` implies `-F`.

## Auth
| Flag | Use |
|---|---|
| `-a user:pass` | Basic auth (`-a user` prompts for the password) |
| `-A digest -a u:p` | Digest auth |
| `-A bearer -a TOKEN` | Bearer token |
| `--ignore-netrc` | Skip ~/.netrc |

## Sessions
`--session=NAME` (stored per host) · `--session=./s.json` · `--session-read-only=NAME` · `httpie cli sessions upgrade-all`

## Network / TLS
| Flag | Use |
|---|---|
| `-F`, `--max-redirects=30` | Follow redirects |
| `--timeout=5` | Timeout (seconds) |
| `--proxy=https:http://h:p` | Proxy (socks5 supported) |
| `--verify=no\|ca.pem` | TLS verification |
| `--cert c.pem --cert-key k.pem` | Client certificate |
| `--ssl=tls1.2  --ciphers=…` | TLS version / ciphers |
| `--path-as-is` | Keep `/../` in the URL |
| `--default-scheme=https` | Scheme when the URL has none |
| `--no-FLAG` | Unset a default flag |

## Scripting / exit codes
`http -I --check-status --timeout=3 URL` (`-I`/`--ignore-stdin` stops cron jobs from hanging)

`0` ok · `1` error · `2` timeout · `3` 3xx · `4` 4xx · `5` 5xx · `6` too many redirects · `7` plugin error · `130` Ctrl-C

## Config
Directory: `$HTTPIE_CONFIG_DIR` → `%APPDATA%\httpie` (Windows) → `~/.httpie` → `~/.config/httpie`
`config.json`: `{"default_options": ["--style=fruity"], "plugins_dir": "…"}`

## Manager
`httpie cli plugins install|upgrade|uninstall|list` · `httpie cli check-updates` · `httpie cli export-args`

## Dev (repo)
| Command | Does |
|---|---|
| `make all` | Creates the venv, installs, runs tests |
| `source venv/bin/activate` | Use the dev `http` |
| `make test` / `make test-cover` | pytest / with coverage |
| `pytest tests/test_x.py::T::t` | Run a single test |
| `make codestyle` | flake8 |
| `make test-all` | Everything (dist, style) |
| `python extras/profiling/run.py` | Benchmarks |
| `http --debug …` | Info for bug reports |

**Key files:** `core.py` (main loop) · `cli/definition.py` (all flags) · `cli/argparser.py` · `cli/requestitems.py` · `client.py` (sending) · `output/` · `sessions.py` · `plugins/base.py` · `manager/` · `status.py` · `tests/utils/__init__.py::http()`
