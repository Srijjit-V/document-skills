# Scrapy 2.19 Cheat Sheet

Python 3.11+ · `pip install scrapy` · Docs: docs.scrapy.org

## Project & CLI
```bash
scrapy startproject myproj && cd myproj
scrapy genspider [-t basic|crawl|csvfeed|xmlfeed] name example.com
scrapy crawl name -O out.json        # -o appends; out.csv:csv sets format
scrapy crawl name -a cat=books -s LOG_LEVEL=INFO
scrapy runspider spider.py -O out.jsonl
scrapy shell "https://example.com"   # fetch(), view(response)
scrapy fetch | view | parse <url>    # parse --spider=NAME -c cb <url>
scrapy list | check NAME | settings --get NAME | version -v | bench
scrapy genrequest 'curl ...'         # curl → Request code
scrapy crawl big -s JOBDIR=crawls/1  # pause (Ctrl-C) / resume
```

## Spider
```python
import scrapy
class Q(scrapy.Spider):
    name = "q"
    allowed_domains = ["example.com"]
    start_urls = ["https://example.com/"]
    custom_settings = {"DOWNLOAD_DELAY": 1}
    async def start(self):               # optional; default uses start_urls
        yield scrapy.Request(self.start_urls[0])
    def parse(self, response):           # may be async def
        for q in response.css("div.quote"):
            yield {"text": q.css("span::text").get()}
        yield from response.follow_all(css="a.next", callback=self.parse)
```
Generic: `CrawlSpider` + `Rule(LinkExtractor(allow=r"/p/"), callback="parse_item", follow=True)`, `SitemapSpider`, `XMLFeedSpider`, `CSVFeedSpider`.

## Selectors
| | |
|---|---|
| `response.css("h1::text").get()` | first match or `None` |
| `.getall()` | list of matches |
| `response.css("a::attr(href)")` | attribute |
| `response.xpath("//h1/text()")` | XPath |
| `.re(r"\d+")` / `.re_first(...)` | regex |
| `response.json()` | parse JSON body |
| `response.urljoin(href)` | absolute URL |

## Requests
`Request(url, callback, errback, method, headers, cookies, meta, cb_kwargs, dont_filter, priority)` · `FormRequest.from_response(resp, formdata={})` · `JsonRequest(url, data={})` · `response.follow(link, cb)`
Meta: `dont_redirect`, `dont_retry`, `handle_httpstatus_list`, `proxy`, `download_timeout`, `max_retry_times`, `cookiejar`

## Items & Pipelines
```python
class P(scrapy.Item): name = scrapy.Field()
class Clean:
    def process_item(self, item):          # raise DropItem to discard
        return item
ITEM_PIPELINES = {"myproj.pipelines.Clean": 300}   # lower runs first
```
Items: dict, dataclass, attrs, `scrapy.Item` (via `ItemAdapter`). Media: `FilesPipeline`, `ImagesPipeline`.

## Key settings (default)
| Setting | Default | Setting | Default |
|---|---|---|---|
| CONCURRENT_REQUESTS | 16 | ROBOTSTXT_OBEY | False* |
| …_PER_DOMAIN | 8* | RETRY_TIMES | 2 |
| DOWNLOAD_DELAY | 0* | DOWNLOAD_TIMEOUT | 180 |
| AUTOTHROTTLE_ENABLED | False | HTTPCACHE_ENABLED | False |
| DEPTH_LIMIT | 0 | LOG_LEVEL | DEBUG |
| CLOSESPIDER_ITEMCOUNT | 0 | TWISTED_REACTOR_ENABLED | True |

\*New projects set ROBOTSTXT_OBEY=True, PER_DOMAIN=1, DOWNLOAD_DELAY=1.
Precedence: `-s` › spider `custom_settings` › `settings.py` › add-ons › defaults. Disable a built-in component: set it to `None`.
`FEEDS = {"out/%(name)s.jsonl": {"format": "jsonlines", "overwrite": True}}`

## From a script
```python
from scrapy.crawler import AsyncCrawlerProcess
from scrapy.utils.project import get_project_settings
p = AsyncCrawlerProcess(get_project_settings()); p.crawl("q"); p.start()
```

## Data flow
Spider `start()` → spider mw → **Engine** → **Scheduler** (dupefilter) → downloader mw → **Downloader**/handlers → response → downloader mw → spider mw → callback → items → **Pipelines** / requests → Scheduler

## Contributing (repo)
```bash
pip install -e . tox pre-commit && pre-commit install
tox -e py -- tests/test_crawl.py   # pytest args after --
pre-commit run --all-files; tox -e mypy; tox -e pylint; tox -e docs
```
Tests: mock server, `example.com` only, parametrize, `build_from_crawler()`. Don't edit `docs/news.rst`. Never rebase a reviewed PR.
