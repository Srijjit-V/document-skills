# HTTPie cheat sheet
Source: httpie/cli@3.2.4 (5b604c3) · 2026-11-02
> **If you only read one thing:** in scripts and CI add `--ignore-stdin` (`-I`); otherwise HTTPie reads the body from stdin and `key=value` items exit 1.
Legend: ★ most used · ⚠ gotcha

## Start
```
pip install httpie
http pie.dev/get
http pie.dev/post a=1
http :8000/api
https example.org
```
`:8000` means localhost:8000. `https` defaults to `https://`.
`--offline` ★ prints the request and sends nothing.

## Request items
| Item | Sends |
|---|---|
| `X-Token:abc` | header |
| `X-Empty;` | empty header |
| `q==1` | query param |
| `name=Ada` ★ | JSON string |
| `age:=36` ★ | raw JSON value |
| `data=@f.txt` | field from file |
| `doc@f.txt` | file upload (multipart) |

Data present and no method → POST.

## Nested JSON
```
http pie.dev/post \
  'user[name]=Ada' 'tags[]=a'
```
→ `{"user": {"name": "Ada"}, "tags": ["a"]}`

## Body type and method
| Flag | Effect |
|---|---|
| (default) | JSON body |
| `-f`, `--form` | urlencoded form |
| `--multipart` | force multipart |
| `--raw TEXT` | body as given |
| `PUT url a=1` | explicit method |

## What gets printed
| Flag | Prints |
|---|---|
| `-v` ★ | request + response |
| `-h` | response headers only |
| `-b` | response body only |
| `-p HBhb` | pick: H/B request, h/b response |
| `-q` | nothing |

Piped output prints the body only.

## Auth, sessions, TLS
| Flag | Use |
|---|---|
| `-a user:pw` | Basic auth |
| `-A bearer -a TOKEN` | Bearer token |
| `--session=dev` | save cookies/headers/auth |
| `--verify=no` | skip TLS check |

`--session-read-only=dev` loads a session without writing it.

## Downloads and scripts
| Flag | Effect |
|---|---|
| `-d` / `-d -c` | download / resume |
| `-F` | follow redirects |
| `--timeout 5` | seconds |
| `--debug` | env + request kwargs |
| `-o out.json` | save output to file |
| `-S` | stream line by line |

`--check-status` ★ makes 3xx/4xx/5xx exit 3/4/5. Other exits: 2 timeout, 6 too many redirects, 7 plugin error.

## Develop
```
make all
make test
make codestyle
pytest tests/f.py::test_x
```
`all` creates `./venv`, installs, tests. `codestyle` runs flake8, a CI gate.

`HTTPIE_CONFIG_DIR=/tmp/x` isolates config.

## Plugins
`httpie cli plugins` then `install X`, `list`, `upgrade X`, or `uninstall X`. Install runs pip into the plugins dir.

## Gotchas
- ⚠ `-h` is `--headers`, not help: use `--help`.
- ⚠ `age=36` sends `"36"`, a string. Use `:=`.
- ⚠ 404 and 500 still exit 0 without `--check-status`.
- ⚠ `default_options` in `config.json` apply to every call, tests too.
- ⚠ `--session` rewrites the file each run, because new headers and auth get saved.
- ⚠ Man pages are generated: edit `cli/definition.py`, then `make man`.

<!-- Cut to fit (1 page):
- --format-options / --style / --pretty: cosmetic, rarely wrong.
- --path-as-is, --compress, --max-redirects, --ssl, --cert: rare.
- Exit code 130 (Ctrl-C): obvious.
- httpie cli sessions upgrade / check-updates / export-args: rare maintenance.
- Request flow and file:line map: belongs in docs.md, not a quick reference.
-->
