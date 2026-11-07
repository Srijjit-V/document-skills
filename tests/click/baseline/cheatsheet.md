# Click Cheat Sheet (Click 8.5+)

`pip install click` · `import click`

## Minimal command

```python
import click

@click.command()
@click.argument("name")
@click.option("--count", "-c", default=1, show_default=True, help="Repeats.")
def hello(name, count):
    """Greet NAME."""              # docstring = --help text
    for _ in range(count):
        click.echo(f"Hello {name}")

if __name__ == "__main__":
    hello()
```

## Groups and subcommands

```python
@click.group()
@click.option("-v", "--verbose", count=True)
@click.pass_context
def cli(ctx, verbose):
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose

@cli.command()                     # name: "sync" (from function)
@click.pass_obj                    # receives ctx.obj
def sync(obj): ...

cli.add_command(other, name="other")
```

| Group option | Effect |
|---|---|
| `invoke_without_command=True` | Run group callback with no subcommand; check `ctx.invoked_subcommand` |
| `chain=True` | `cli a b c` runs several subcommands |
| `@cli.result_callback()` | Post-process subcommand return values |
| `@click.command("my-name")` | Override the command name |

Function names: `_` becomes `-` (`def dry_run` → `dry-run`).

## Arguments (positional)

| Pattern | Code |
|---|---|
| Required | `@click.argument("src")` |
| Optional | `@click.argument("dst", required=False)` |
| Variadic | `@click.argument("files", nargs=-1)` → tuple |
| Fixed count | `@click.argument("point", nargs=2, type=float)` |
| From env | `@click.argument("src", envvar="SRC")` |

Arguments take `help=` since 8.5; otherwise describe them in the docstring.

## Options

| Want | Code |
|---|---|
| Value with default | `@click.option("--n", default=1)` (type inferred) |
| Required | `required=True` |
| Boolean flag | `@click.option("--force", is_flag=True)` |
| On/off pair | `@click.option("--color/--no-color", default=True)` |
| Repeatable | `multiple=True` → tuple |
| Counter (`-vvv`) | `count=True` |
| Feature switch | two options, same dest, `flag_value="upper"` / `"lower"` |
| Tuple value | `nargs=2` or `type=(str, int)` |
| Env var | `envvar="APP_TOKEN"` (or `auto_envvar_prefix="APP"` in `cli(...)`) |
| Ask if missing | `prompt=True` / `prompt="Your name"` |
| Password | `prompt=True, hide_input=True, confirmation_prompt=True` or `@click.password_option()` |
| Show default in help | `show_default=True` |
| Hide from help | `hidden=True` |
| Custom Python name | `@click.option("--from", "from_")` |
| Deprecate | `deprecated=True` or `deprecated="use --x"` |

Built-ins: `@click.version_option()` (auto-detects package version), `@click.confirmation_option(prompt="Sure?")`, `@click.help_option("-h", "--help")`.
Also `context_settings={"help_option_names": ["-h", "--help"]}`.

## Types

| Type | Notes |
|---|---|
| `str`, `int`, `float`, `bool` | Plain Python types work |
| `click.Choice(["a","b"], case_sensitive=False)` | Also accepts an `Enum` class |
| `click.IntRange(0, 10, clamp=True)` / `FloatRange` | Bounds check |
| `click.Path(exists=True, dir_okay=False, path_type=pathlib.Path)` | Validates, doesn't open |
| `click.File("rb")` / `click.File("w", lazy=True)` | Opens; `-` = stdin/stdout |
| `click.DateTime(["%Y-%m-%d"])` | → `datetime` |
| `click.UUID` | → `uuid.UUID` |

Custom: subclass `click.ParamType`, set `name`, implement `convert(value, param, ctx)`, call `self.fail(msg, param, ctx)` on bad input.

## Validation callback

```python
def check(ctx, param, value):
    if value % 2:
        raise click.BadParameter("even only")
    return value

@click.option("--n", type=int, callback=check)
```

`is_eager=True` + `expose_value=False` processes an option first and keeps it out of the function args (how `--version` works).

## Output and input

| Task | Code |
|---|---|
| Print | `click.echo(msg)` · stderr: `err=True` |
| Color | `click.secho("ok", fg="green", bold=True)` / `click.style(...)` |
| Ask | `click.prompt("Port", type=int, default=8080)` |
| Yes/no | `click.confirm("Continue?", abort=True)` |
| Pager | `click.echo_via_pager(text)` |
| Editor | `click.edit("initial text")` |
| Progress | `with click.progressbar(items, label="Work") as bar:` |
| Open file/URL | `click.launch(path_or_url)` |
| Config dir | `click.get_app_dir("myapp")` |

## Errors and exit codes

| Raise | Result |
|---|---|
| `click.ClickException(msg)` | `Error: msg`, exit 1 |
| `click.UsageError(msg)` | usage + error, exit 2 |
| `click.BadParameter(msg)` | names the bad param, exit 2 |
| `click.Abort()` | `Aborted!`, exit 1 |
| `ctx.exit(code)` | exit with `code` |

## Testing

```python
from click.testing import CliRunner

def test_sync(tmp_path):
    runner = CliRunner()
    r = runner.invoke(cli, ["sync", str(tmp_path)],
                      env={"APP_TOKEN": "t"}, input="y\n")
    assert r.exit_code == 0, r.output
    assert "done" in r.stdout     # also r.stderr, r.output
```

`r.exception` holds an uncaught exception. Use `tmp_path`; `isolated_filesystem()` is deprecated in 8.5.

## Packaging and completion

```toml
[project.scripts]
mytool = "mytool.cli:cli"
```

Shell completion (bash, zsh, fish, powershell):
`_MYTOOL_COMPLETE=zsh_source mytool > ~/.mytool-complete.zsh`, then source it from your shell rc.

## Gotchas

- Decorated parameter names must match function args (`--dry-run` → `dry_run`).
- Only one `nargs=-1` argument per command; it yields `()` when nothing is passed.
- `default` on a `multiple=True` option must be a list/tuple.
- `ctx.obj` is `None` until you set it: call `ctx.ensure_object(dict)`.
- Use `click.echo`, not `print()`: it respects `CliRunner` capture and strips color when piped.
