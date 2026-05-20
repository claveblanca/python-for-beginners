## Usage

Install dependencies first:

```bash
pip install -r requirements.txt
# optional: better TLS impersonation to avoid 403s
pip install curl-cffi
```

Run the script:

```bash
# fetch latest-news listing (single page, prints to stdout)
python financial_news.py

# fetch stock-market news via sitemap (default category)
python financial_news.py --category stock-market-news

# use HTML pagination instead of sitemap
python financial_news.py --category stock-market-news --use-listing-pages

# provide a custom sitemap URL
python financial_news.py --sitemap-url https://www.investing.com/news_stock_market_sitemap.xml

# limit to the first 5 articles only
python financial_news.py --limit 5

# add a 1.5 s delay between article fetches (be polite)
python financial_news.py --delay 1.5

# output one JSON object per line (pipe-friendly)
python financial_news.py --limit 5 --json

# combine options: 10 stock-market articles as JSON with a 2 s delay
python financial_news.py --category stock-market-news --limit 10 --delay 2 --json
```

## sources of news

```
📰 Top Global Financial News Platforms
Bloomberg
Real-time market data, breaking news, and deep analysis
Excellent for macroeconomics, equities, and global markets
Reuters
Highly reliable, fast, and unbiased reporting
Great for global financial updates and earnings news
CNBC
Live market coverage, interviews, and stock insights
Strong focus on U.S. markets and business news
Financial Times
In-depth analysis, global finance, and policy insights
Premium content, widely respected among professionals
📊 Investment & Market Analysis Sources
The Wall Street Journal
High-quality reporting on markets, companies, and economy
Strong editorial perspective
MarketWatch
Easy-to-digest market news and personal finance tips
Good for retail investors
Seeking Alpha
Opinion-driven articles and stock analysis
Useful for idea generation (but requires critical thinking)
Yahoo Finance
Free data, charts, earnings, and news aggregation
Great all-in-one dashboard
📈 Professional & Data-Driven Platforms
Morningstar
Fundamental analysis, ratings, and long-term investing insights
Strong on mutual funds and ETFs
Investing.com
Real-time data, economic calendar, and global market coverage
Popular for tracking multiple asset classes
```