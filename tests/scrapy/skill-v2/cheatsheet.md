# Scrapy cram sheet
Source: scrapy/scrapy@2.19.0 · 2026-11-02
> **If you only read one thing:** use `-O out.json` (overwrite), not `-o`. In a project, `-o` onto an existing file logs an ERROR and the items are lost.
Legend: ★ most used · ⚠ gotcha

## Get started
```
pip install scrapy
scrapy startproject quotes
cd quotes
scrapy genspider qs site.com
scrapy crawl qs -O out.json
# no project needed:
scrapy runspider s.py \
  -O o.json
```
Needs Python 3.11+.

## Spider skeleton
```
import scrapy

class QS(scrapy.Spider):
  name = "qs"
  allowed_domains = [
    "site.com"]
  start_urls = [
    "https://site.com/"]

  def parse(self, r):
    for q in r.css("p"):
      yield {"t": q.css(
        "b::text").get()}
    yield from r.follow_all(
      css="a.next")
```
`follow_all` defaults to `callback=self.parse`. Custom first requests: `async def start(self)` (2.13+).

## Daily commands
| Command | Does |
|---|---|
| `crawl NAME` ★ | run project spider |
| `shell URL` ★ | try selectors live |
| `list` | spider names |
| `fetch URL` | print body as Scrapy sees it |
| `view URL` | open that body in a browser |
| `parse URL -c parse` | run one callback |
| `genrequest "curl …"` | curl → `Request(...)` |

`crawl`, `list`, `check`, `parse`, `edit` need a project dir.

## Crawl flags
| Flag | Effect |
|---|---|
| `-O f.json` ★ | overwrite feed |
| `-o f.jsonl` | append feed |
| `-a cat=books` | spider attr `self.cat` |
| `-s NAME=VAL` | override a setting |
| `-L INFO` | log level (default DEBUG) |
| `--pdb` | debugger on failure |

## Selectors
```
r = response
r.css("a::text").get()
  # first match or None
r.xpath("//a/@href").getall()
  # list of all hrefs
r.xpath("//h1/text()").get()
r.follow(href, cb)
  # relative URLs OK
```

## Defaults: library → new project
- `ROBOTSTXT_OBEY`: False → True
- `CONCURRENT_REQUESTS_PER_DOMAIN`: 8 → 1
- `DOWNLOAD_DELAY`: 0 → 1 s (±50% jitter)
- `FEED_MODE`: None → `create`

A spider run outside a project gets the library column. Check: `scrapy settings --get NAME`

## Gotchas
- ⚠ Links outside `allowed_domains` drop silently (DEBUG log only), because `OffsiteMiddleware` filters them. Check stat `offsite/filtered`.
- ⚠ A URL seen once is never fetched again: the dupefilter drops it. Use `Request(url, dont_filter=True)`.
- ⚠ Every crawl opens Telnet (:6023) and a RemoteControl HTTP server that runs code. Off: set `TELNETCONSOLE_ENABLED` and `REMOTE_CONTROL_ENABLED` to False.
- ⚠ No-reactor mode (`TWISTED_REACTOR_ENABLED` off) is experimental, uses aiohttp, and can't be set per spider.

## Tune and resume
```
-s JOBDIR=crawls/r1
  # Ctrl-C, rerun to resume
-s HTTPCACHE_ENABLED=1
  # cache: .scrapy/httpcache
-s AUTOTHROTTLE_ENABLED=1
  # delay follows latency
-s CLOSESPIDER_ITEMCOUNT=50
  # stop after 50 items
```

## Hack on Scrapy
```
pip install -e .
pip install tox pre-commit
tox -e py -- tests/test_x.py
pre-commit run --all-files
tox -e mypy && tox -e pylint
```
All defaults: `default_settings.py` in `scrapy/settings/`. Engine: `scrapy/core/engine.py`.

<!-- Cut to fit:
- Run from a script with AsyncCrawlerProcess: rare for day-to-day CLI use; in docs.md "Run it from a script".
- Request flow (engine -> scheduler -> downloader -> spider -> scraper): explanation, not lookup; in docs.md "How a request flows".
- Repository map table: in docs.md.
- Contributor rules from AGENTS.md (underscore-prefix private names, mockserver tests, no rebase after review): in docs.md.
- DOWNLOAD_DELAY_JITTER (+/-50% by default), FEED_EXPORT_ENCODING utf-8 in projects: low impact.
-->
