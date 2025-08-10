import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm

def scrape_ndtv_news(max_articles=50, delay=2):
    base_url = "https://www.ndtv.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Step 1: Fetch article links from NDTV homepage
    article_links = set()
    
    print("Fetching NDTV homepage...")
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract links (NDTV uses <a> tags with href containing '/news/')
        for link in tqdm(soup.select('a[href*="/news/"]'), desc="Collecting links"):
            href = link['href']
            if href.startswith('https://www.ndtv.com/') and not any(x in href for x in ['/video/', '/live-news/']):
                article_links.add(href)
                if len(article_links) >= max_articles:
                    break
    except Exception as e:
        print(f"Error fetching {base_url}: {e}")

    # Step 2: Scrape articles
    articles_data = []
    print("Scraping articles...")
    for link in tqdm(list(article_links)[:max_articles], desc="Processing"):
        try:
            response = requests.get(link, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.find('h1', {'itemprop': 'headline'})
            title = title.get_text(strip=True) if title else "No Title"
            
            # Extract text (NDTV uses <p> inside div#ins_storybody)
            body = soup.find('div', {'id': 'ins_storybody'})
            if body:
                paragraphs = body.find_all('p')
                text = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            else:
                text = "No Body Found"
            
            articles_data.append({
                'title': title,
                'text': text,
                'url': link,
                'scraped_at': pd.Timestamp.now()
            })
            time.sleep(delay)
        except Exception as e:
            print(f"Error scraping {link}: {e}")

    return pd.DataFrame(articles_data)

# Run scraper
df = scrape_ndtv_news(max_articles=50)  # Start with 50 to test
df.to_csv("ndtv_news_articles.csv", index=False, encoding='utf-8')
print(f"Saved {len(df)} articles to 'ndtv_news_articles.csv'.")