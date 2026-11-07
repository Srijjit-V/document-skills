# Click cram sheet: building CLIs
Source: pallets/click@2247b35 (8.6.0.dev) · 2026-11-03 · Gotchas run on released Click 8.5.0, not the checkout; other lines checked against source
> **If you only read one thing:** a decorated function is now a `Command`. Calling `hello("x")` parses `"x"` as argv and exits; keep logic in a plain function and call that.
Legend: ★ most used · ⚠ gotcha, run · ⚠? from the docs, not run

## Start
`pip install click`
```python
import click

@click.command()
@click.option("-n",
              default=1)
@click.argument("name")
def hello(n, name):
    """Greet NAME."""
    for _ in range(n):
        click.echo(name)
```
- Run as a script: `if __name__ == "__main__": hello()`
- The docstring becomes `--help` text.

## Options ★
- `default=1` → also sets type int
- `required=True` → error if missing
- `is_flag=True` → `True` when passed
- `"--x/--no-x"` → on/off pair
- `multiple=True` → repeatable, tuple
- `count=True` → `-vvv` gives 3
- `envvar="TOKEN"` → read env var
- `prompt=True` → ask if missing
- `hide_input=True` → for passwords
- `show_default=True` → in help

## Names
- `"--dry-run"` → param `dry_run`
- `"-n", "--name", "who"` → param `who`
- function `sync_cmd` → command `sync`; suffixes `_command`, `_cmd`, `_group`, `_grp` drop

## Types
- `click.Choice(["a", "b"])` → one of list
- `click.IntRange(0, 9)` → bounded int
- `click.Path(exists=True)` → checked path str
- `click.File("r")` → open file; `-` is stdin
- `type=(str, int)` → tuple, nargs=2

## Arguments
- Required by default.
- `help=` needs 8.5+; before that, describe it in the docstring.
- `nargs=-1` → tuple of any length; once per command.
- `cmd -- -odd.txt`: after `--`, all are arguments.

## Groups and context
```python
@click.group()
@click.option("--debug",
              is_flag=True)
@click.pass_context
def cli(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj["dbg"] = debug

@cli.command()
@click.pass_obj
def sync(obj):
    click.echo(obj["dbg"])
```
- `cli.add_command(cmd)` registers a command from another module.
- `invoke_without_command=True` runs the group with no subcommand; check `ctx.invoked_subcommand`.

## Ship it
```toml
[project.scripts]
hello = "pkg.cli:hello"
```
- `pip install -e .`, then run `hello`.
- Zsh completion: `_HELLO_COMPLETE=zsh_source hello` prints a script; `eval` it in `.zshrc`.

## Errors and exit codes
- `raise click.ClickException(msg)` → exit 1
- `click.UsageError`, `click.BadParameter` → exit 2
- `click.Abort` → prints `Aborted!`, exit 1
- `click.confirm("Go?", abort=True)` raises `Abort` on no.
- `--help` exits 0.
- `hello(["Ann"], standalone_mode=False)` returns the value and lets errors raise instead of exiting.

## Test
```python
from click.testing import (
    CliRunner)

r = CliRunner().invoke(
    hello, ["Ann"])
assert r.exit_code == 0
assert r.output == "Ann\n"
```
`r.output` mixes stdout and stderr (8.2+); use `r.stdout` for one stream. Exceptions are caught: check `r.exception`.

## Gotchas
- ⚠ `-dbg` works as one option if you declare it. If you declare only `-d`, `-b`, `-g`, then `-dbg` splits into all three.
- ⚠ `multiple=True, default="ab"` fails with "Value must be an iterable" and exit 2. Use `default=["a","b"]`.
- ⚠ `--x/--no-x` with `envvar="X"` reads only `X`; `NO_X` is ignored.
- ⚠ `auto_envvar_prefix="APP"` names include the subcommand: `APP_RUN_HOST`, not `APP_HOST`.
- ⚠ A group run with no args shows help and exits 2.
- ⚠? `print()` can raise `UnicodeError` on a broken terminal; `click.echo` avoids it (docs/quickstart.md).
- ⚠? `CliRunner` swaps global stdio, so it is not thread-safe (docs/testing.md).

## Output
- `click.echo(msg, err=True)` → stderr
- `click.secho("ok", fg="green")` → styled; plain when piped
- `click.prompt("Port", type=int)` asks and converts
- A line with only `\b` stops help rewrapping the next paragraph.
- `@click.version_option()` adds `--version` from package metadata.
- `context_settings={"help_option_names": ["-h", "--help"]}` adds `-h`.

<!-- Cut to fit (1 page):
- Callbacks, is_eager, custom ParamType: validation beyond built-in types is less common; docs/advanced.md, docs/parameter-types.md
- Chained groups (chain=True) and lazy subcommand loading: advanced; docs/commands.md, docs/complex.md
- default_map and ctx.get_parameter_source(): config-file layering, rare; docs/commands-and-groups.md
- Feature-switch groups (several flag_value options on one param) and default/flag_value tables: rare, long; docs/options.md
- progressbar, edit, launch, pager, get_app_dir, open_file: terminal utilities outside core CLI building; docs/utils.md
- deprecated=, hidden=, renaming commands: rare; docs/commands-and-groups.md
- CliRunner isolated_filesystem() and input=: secondary test helpers; docs/testing.md
- Bash/fish completion lines: same pattern as zsh; docs/shell-completion.md
-->
