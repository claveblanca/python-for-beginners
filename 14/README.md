## Usage

Install dependencies first:

```bash
pip install -r requirements.txt
```

Run the script:

```bash
# limit to the first 5 articles only
python financial_news.py --limit 5 -o output.txt

python news_sentiment.py -i output.txt -o results.json
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
## Technologies Used

- **requests** — HTTP client for web scraping
- **curl_cffi** — Chrome TLS impersonation to bypass 403 blocks (optional)
- **BeautifulSoup** (bs4) — HTML parsing and content extraction
- **Hugging Face Transformers** — sentiment analysis pipeline (`cardiffnlp/twitter-roberta-base-sentiment-latest`)
- **PyTorch** — deep learning backend for the Transformers models
- **Investing.com** — financial news data source
