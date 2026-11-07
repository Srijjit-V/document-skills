# Click cram sheet
Source: click 8.6.0.dev repo, behavior run on 8.5.0 · 2026-11-02
> **If you only read one thing:** a function argument must match the option name (`--dry-run` → `dry_run`), and options of a group go before the subcommand: `cli --env x sub`, not `cli sub --env x`.
Legend: ★ most used · ⚠ gotcha · → returns

## Start ★
```python
import click

@click.command()
@click.option("-n",default=1)
@click.argument("name")
def hello(n, name):
    """Greet NAME."""
    for _ in range(n):
        click.echo(name)

if __name__ == "__main__":
    hello()
```
`pip install click`
`python hello.py -n 2 Ann`

## Option and argument kwargs
- `default=3` → also infers int
- `required=True` → error if absent
- `is_flag=True` → bool, no value
- `--a/--no-a` → on/off pair
- `count=True` → `-vvv` gives 3
- `multiple=True` → repeat, tuple
- `nargs=-1` → argument eats rest
- `envvar="X"` → read env var
- `prompt=True` → ask if absent
- `show_default=True` → in --help
- `callback=f` → `f(ctx, param, v)`

## Types
- `click.Choice(["a","b"], case_sensitive=False)`
- `click.IntRange(1, 5)`
- `click.Path(exists=True, path_type=Path)`
- `click.File("r")`: `-` means stdin
- `type=bool` takes yes/no/1/0/true/false

## Groups and context
```python
@click.group()
@click.option("--env")
@click.pass_context
def cli(ctx, env):
    ctx.ensure_object(dict)
    ctx.obj["env"] = env

@cli.command()
@click.pass_obj
def sync(obj): ...
```
`invoke_without_command=True` runs the group body with no subcommand (`ctx.invoked_subcommand` is `None`). `chain=True` runs `a b` in order. `ctx.invoke(other)` calls a command with its defaults.

## Output and errors
- `click.echo(s, err=True)` → stderr
- `click.confirm(m, abort=True)` → n exits 1
- `UsageError(m)` → exit 2, usage line
- `ClickException(m)` → exit 1, `Error: m`
- `ctx.exit(3)` → exit with code
- `hidden=True` → not in --help
- `deprecated=True` → warns on use

## Test it
```python
from click.testing import CliRunner
r = CliRunner().invoke(hello, ["-n", "2", "Ann"])
assert r.exit_code == 0
r.output   # stdout + stderr
r.stdout, r.stderr, r.exception
# input="y\n" feeds prompts; env={"K": "v"}
```

## Ship it
- pyproject `[project.scripts]`, `hello = "hello:cli"`, then `pip install -e .` gives a `hello` command [docs only]
- `@click.version_option("1.2.3")` adds `--version`
- `context_settings={"help_option_names": ["-h", "--help"]}` adds `-h`
- `\b` alone on a line keeps the next lines unwrapped in help

## Gotchas
- ⚠ `cli sub --env x` fails with `No such option`: the group parses its own options first. Put them before `sub`.
- ⚠ `def init_db` becomes `init-db`; `init_db` on the command line is `No such command`.
- ⚠ Param name differs from function arg (`--dry-run`, `def f(dryrun)`) → `TypeError: unexpected keyword argument 'dry_run'`. Rename the arg.
- ⚠ `multiple=True` and `nargs=-1` give `()` when unset, never `None`. A `nargs=2` option gives `None`.
- ⚠ `-x` as a value is read as an option. Use `cmd -- -x`.
- ⚠ Env vars only work with `envvar=` or `auto_envvar_prefix="APP"` passed to `main()`; there is no default lookup.
- ⚠ A plain exception exits 1 with a traceback; only `ClickException` prints `Error:`. In tests see `r.exception`.
- ⚠ `version_option()` with no string raises `RuntimeError` when it cannot detect the version (it did in a plain script test). Pass the string.
- ⚠ In tests, `isolated_filesystem()` is deprecated; use pytest `tmp_path`.
- ⚠ `hello.main()` ends in `SystemExit`; `standalone_mode=False` returns the value.

<!-- Cut to fit (1 page):
- Shell completion, click.style/secho, progressbar, prompt(), launch: less frequent than the core build loop; in docs
- Lazy groups, custom Option/Command classes, result_callback: advanced
- Choice(case_sensitive=False) returning the declared case: minor
- version_option/custom_version_option details: kept one line
-->
