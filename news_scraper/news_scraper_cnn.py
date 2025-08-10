import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm

def scrape_cnn_news(max_articles=100, delay=2):
    base_url = "https://edition.cnn.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
   
    article_links = set()
    sections = ["world", "business", "politics", "technology"]  
    
    with tqdm(total=max_articles, desc="Collecting links") as pbar:
        for section in sections:
            section_url = f"{base_url}/{section}"
            try:
                response = requests.get(section_url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                
                for link in soup.select('a[href*="/202"]'):  
                    href = link['href']
                    if href.startswith('/') and not any(x in href for x in ['/video/', '/gallery/']):
                        full_url = f"{base_url}{href}" if not href.startswith('http') else href
                        article_links.add(full_url)
                        pbar.update(1)
                        if len(article_links) >= max_articles:
                            break
                time.sleep(delay)
                
            except Exception as e:
                print(f"Error fetching {section_url}: {e}")
                continue

    
    articles_data = []
    with tqdm(total=len(article_links), desc="Scraping articles") as pbar:
        for link in list(article_links)[:max_articles]:
            for attempt in range(3):  
                try:
                    response = requests.get(link, headers=headers, timeout=10)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No Title"
                    
                    paragraphs = soup.select('p.paragraph')
                    text = ' '.join([p.get_text(strip=True) for p in paragraphs])
                    
                    articles_data.append({
                        'title': title,
                        'text': text,
                        'url': link,
                        'timestamp': pd.Timestamp.now()
                    })
                    break 
                except Exception as e:
                    if attempt == 2:
                        print(f"Failed to scrape {link}: {e}")
                    time.sleep(delay * 2)
            pbar.update(1)
            time.sleep(delay)

    return pd.DataFrame(articles_data)

df = scrape_cnn_news(max_articles=100)
df.to_csv("cnn_news.csv", index=False, encoding='utf-8')
print(f"Successfully scraped {len(df)} articles.")