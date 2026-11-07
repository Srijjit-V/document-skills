# csvtrim

A small Python script that strips leading and trailing whitespace from every cell of a CSV file and drops rows that are completely empty.

It uses only the standard library and needs Python 3 (f-strings are used, so 3.6 or later).

## Usage

```
python3 csvtrim.py INPUT [-o OUTPUT] [--delimiter CHAR] [--keep-empty]
```

| Option | Meaning |
| --- | --- |
| `INPUT` | CSV file to read (UTF-8). |
| `-o`, `--output` | Write to this file instead of standard output. An existing file is overwritten. |
| `--delimiter` | Field delimiter for both input and output. Default `,`. |
| `--keep-empty` | Keep rows that are completely empty (cells are still trimmed). |

The count of dropped rows is printed to standard error, so it does not mix with CSV on standard output.

## Example

`sample.csv`:

```
name , city ,age
  Ana ,Lisbon , 31

 Ben,  Oslo,27
,,
```

```
$ python3 csvtrim.py sample.csv
csvtrim: dropped 2 empty rows
name,city,age
Ana,Lisbon,31
Ben,Oslo,27
```

## Behavior to know about

- A row counts as empty when every cell is blank after trimming. A blank line and a row like `,,` are both dropped.
- Output always uses `\n` line endings and the csv module's default quoting, so quoting may differ from the input.
- If the input file does not exist, it prints `csvtrim: no such file: <path>` to standard error and exits with status 2.
- Do not set `-o` to the same path as the input: the output file is opened after the input is read, but it is overwritten without asking.

## Tests

```
python3 -m unittest
```

The tests cover the `trim()` function in `test_csvtrim.py`. The command-line handling is not tested.
