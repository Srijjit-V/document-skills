# Scrapy cram sheet
Source: scrapy@2.19.0 · Python 3.11+ · 2026-11-02
> **If you only read one thing:** non-2xx responses and repeated URLs never reach your callback. Check HTTPERROR_ALLOWED_CODES and dont_filter before debugging selectors.
Legend: ★ most used · ⚠ gotcha

## Daily commands
| Command | Does |
|---|---|
| `scrapy crawl NAME -O out.jsonl` ★ | run spider, overwrite output |
| `scrapy shell URL` ★ | console with `response` loaded |
| `scrapy parse URL --spider NAME -c cb` | run one callback on one URL |
| `scrapy runspider file.py` | run a spider without a project |
| `scrapy genspider NAME DOMAIN` | new spider from template |
| `scrapy fetch --curl 'curl ...'` | fetch a request given as curl |
| `scrapy genrequest 'curl ...'` | print Request code for curl |
| `scrapy settings --get NAME` | print a resolved setting |

## Global flags
| Flag | Does |
|---|---|
| `-s NAME=VALUE` ★ | override a setting (priority 40) |
| `-a NAME=VALUE` | spider argument, becomes attribute |
| `-o F` / `-O F` | append / overwrite feed |
| `-L INFO` | log level (default `DEBUG`) |
| `--pdb` | debugger on logged exceptions |

## Minimal spider
```python
class QSpider(scrapy.Spider):
  name = "q"
  start_urls = [
   "https://quotes.toscrape.com"]

  def parse(self, resp):
    for q in resp.css(".quote"):
      yield {"t": q.css(
        ".text::text").get()}
    yield from resp.follow_all(
      css="li.next a",
      callback=self.parse)
```
- Yield dict → pipelines/feeds; yield `Request` → scheduler
- Custom first requests: `async def start(self)` (2.13+)

## Selectors (on `response`)
- `.css("h1::text").get()` → first str or `None`
- `.css("a::attr(href)").getall()` → list
- `.xpath("//a/@href").get()` → XPath form
- `.follow(href, callback=cb)` → `Request`, relative URL ok

## Settings that matter
Built-in default → `startproject` template value:
- `ROBOTSTXT_OBEY` False → True
- `CONCURRENT_REQUESTS_PER_DOMAIN` 8 → 1
- `DOWNLOAD_DELAY` 0 → 1
- `RETRY_TIMES` 2 (3 attempts), `DOWNLOAD_TIMEOUT` 180 s
- Priority: default 0 < command 10 < addon 15 < project 20 < spider 30 < cmdline 40

## Gotchas
- ⚠ 404/500 dropped by `HttpErrorMiddleware`. Use `meta={"handle_httpstatus_list": [404]}`.
- ⚠ Duplicate URLs silently filtered. `dont_filter=True` to revisit.
- ⚠ `allowed_domains` wants `"example.com"`, not a URL.
- ⚠ `-o x.json` twice = two arrays, invalid JSON. Use `-O` or `.jsonl`.
- ⚠ `runspider` outside a project uses built-in defaults: no robots.txt, 8 req/domain.

## Find it in the repo
- `scrapy/core/engine.py` crawl loop
- `scrapy/core/scheduler.py` queue, dupefilter
- `scrapy/settings/` defaults in `default_settings.py`
- `scrapy/commands/` one file per command
- `tests/mockserver/` server the tests crawl

## Run from a script
```python
from scrapy.crawler import (
  AsyncCrawlerProcess)
p = AsyncCrawlerProcess({
  "FEEDS": {"out.json":
    {"format": "json"}}})
p.crawl(QSpider)
p.start()  # blocks until done
```

## Enable a pipeline
```python
ITEM_PIPELINES = {
  "proj.pipelines.Clean": 300}
```
- Lower number runs first; keep to 0–1000
- Same dict shape for `DOWNLOADER_MIDDLEWARES`, `SPIDER_MIDDLEWARES`

## Contribute
```bash
pre-commit run --all-files
tox -e mypy && tox -e pylint
tox -e py -- tests/test_foo.py
```

<!-- Cut to fit (1 page):
- Request flow through engine/scheduler/middlewares: explanation, not lookup; in docs.md
- scrapy check / contracts, edit, list, view, bench, version, complete: rare
- TWISTED_REACTOR, LOG_LEVEL, CONCURRENT_REQUESTS defaults: rarely changed
- Contributor conventions (_ prefix, example.com in tests, no news.rst edits): in docs.md
-->
