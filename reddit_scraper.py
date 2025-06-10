import praw
import pandas as pd
from tqdm import tqdm
from newspaper import Article
import time

# Initialize Reddit API
reddit = praw.Reddit(
    """Enter your client_id and client_secret """
    
    client_id='CLIENT_ID',         
    client_secret='CLIENT_SECRET', 
    user_agent='FakeNewsDetector/1.0'  

def extract_article_content(url):
    """Extract main text content from a news article URL"""
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        print(f"Error extracting content from {url}: {str(e)}")
        return None

def get_reddit_news_data(num_posts=1000):
    """
    Collect news data from multiple subreddits and
    Returns a DataFrame with columns: title, content, url
    """
    subreddits = ['news', 'worldnews', 'politics', 'india']
    posts_data = []
    
    print(f"Collecting {num_posts} news posts from Reddit ...")
    
    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)
        
    
        for post in tqdm(subreddit.hot(limit=num_posts//len(subreddits)+20), 
                        desc=f"Scraping r/{subreddit_name}"):
            try:
                
                if post.stickied or post.is_self:
                    continue
                
                # Get article content
                article_content = extract_article_content(post.url)
                if not article_content or len(article_content) < 100:  
                    continue
                
                posts_data.append({
                    'title': post.title,
                    'content': article_content,
                    'url': post.url,
                    'subreddit': subreddit_name
                })
                
                # Add delay 
                time.sleep(1)
                
                
                if len(posts_data) >= num_posts:
                    break
                    
            except Exception as e:
                print(f"Error processing post: {e}")
                continue
    
    # Convert to DataFrame and save
    df = pd.DataFrame(posts_data)[:num_posts]  
    return df[['title', 'content', 'url']]    



# Collect the data
news_data = get_reddit_news_data(1000)

# Save to CSV
news_data.to_csv('reddit_news.csv', index=False)
print("Data collection complete. Saved to 'reddit_news.csv'")

# Display sample
print("\nSample data:")
print(news_data.head(3))