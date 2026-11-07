# Click: build a CLI
Source: Click 8.5.0 (installed, checked with CliRunner); repo main is 8.6.0.dev (docs read as text), 2026-11-04
> **If you only read one thing:** decorate a function with `@click.command()`, stack `@click.option`/`@click.argument` above it, and parameter names become function arguments; test with `CliRunner`.
Legend: ★ use daily · ⚠ mistake · → leads to

## Skeleton ★
```python
import click

@click.group()
def cli(): ...

@cli.command()
@click.option("-n", "--name", default="W")
@click.argument("files", nargs=-1)
def hello(name, files):
    click.echo(f"hi {name}")

if __name__ == "__main__":
    cli()
```
Install as a command: `app = "pkg.mod:cli"` under `[project.scripts]` `[docs-only]`

## Options ★
| Declare | Gives |
|---|---|
| `"--a/--no-a"` | bool on/off |
| `is_flag=True` | bool, default False |
| `count=True` (`-vvv`) | int 3 |
| `multiple=True` | tuple |
| `nargs=2, type=int` | tuple of 2 |
| `required=True` | error if absent |
| `show_default=True` | `[default: W]` in help |

## Types
| click.* | Use |
|---|---|
| `type=int` or `default=3` | int, inferred |
| `Choice(["a","b"])` | fixed set |
| `IntRange(1, 5)` | bounded int |
| `Path(exists=True)` | file path, checked |
| `File("r")` | open file; `-` is stdin |

## Value order ★
1. command line
2. `envvar=` (or `auto_envvar_prefix`)
3. `default_map` on the context
4. `default=`

## Groups and context
- `invoke_without_command=True` runs the group alone
- `ctx.obj` + `@click.pass_obj` share state
- `@click.pass_context` gives `ctx`
- `ctx.invoke(other, n=7)` calls a command
- `chain=True` runs `x1 x2` in one call

## Input and output
- `click.echo(msg, err=True)` writes stderr
- `prompt=True` asks if missing
- `hide_input=True, confirmation_prompt=True` for passwords
- `@click.confirmation_option()` adds `--yes`
- `@click.version_option("1.2.3")` adds `--version`

## Errors and exit codes
| Raise | Exit |
|---|---|
| `UsageError("x")` | 2, shows usage |
| `BadParameter("x")` in a callback | 2 |
| `ClickException("x")` | 1, `Error: x` |
| `Abort()` | 1, `Aborted!` |
| `ctx.exit(4)` | 4 |

## Test with CliRunner ★
```python
from click.testing import CliRunner
r = CliRunner().invoke(cli, ["hello"], env={"K": "v"}, input="y\n")
r.exit_code, r.output, r.stderr
```
`isolated_filesystem()` gives a temp dir. `catch_exceptions=False` re-raises.

## Gotchas
- ⚠ Group options go before the subcommand: `app --debug sub` works, `app sub --debug` is "No such option", because each level parses its own options.
- ⚠ A value starting with `-` is read as an option; put `--` first (`app -- -x`) because it looks like an option.
- ⚠ `def do_thing` becomes `do-thing`, and `do_thing` is "No such command", because Click converts underscores to dashes. `init_cmd` becomes `init`, too.
- ⚠ `Choice` with `case_sensitive=False` returns the declared value (`A` gives `a`); the default is case-sensitive and `LO` fails.
- ⚠ An empty env var (`TOK=""`) gives `None`, not `""`, because Click treats it as unset.
- ⚠ `multiple=True` with `default=["a"]` is replaced, not extended, when the user passes `--t b`.
- ⚠ An exception that is not a Click one gives exit 1 and a traceback; `CliRunner` stores it in `r.exception`.
- ⚠ Prompt text and `Aborted!` appear in `r.output`, not on a terminal, so assert on them there.

<!-- Cut to fit: click.style/secho/progressbar/pause (output polish, rare); shell completion (setup, not daily); click.DateTime/UUID/Tuple types (rare); lazy/plugin groups and aliases (advanced); no_args_is_help and help_option_names (minor); 8.6.0.dev-only changes (Parameter.spec, error messages naming the option spec; not runnable on installed 8.5.0) -->
