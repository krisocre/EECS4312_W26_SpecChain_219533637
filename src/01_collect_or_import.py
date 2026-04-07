"""imports or reads your raw dataset; if you scraped, include scraper here"""

import json
from google_play_scraper import Sort, reviews

APP_ID = 'com.getsomeheadspace.android'

def gather_reviews():
    print(f"Starting review collection for {APP_ID}...")
    
    # We attempt to pull 5,000 reviews
    result, _ = reviews(
        APP_ID,
        lang='en', 
        country='us', 
        sort=Sort.NEWEST, 
        count=5000
    )

    with open('data/reviews_raw.jsonl', 'w', encoding='utf-8') as f:
        for entry in result:
            # Store the full raw dictionary per line
            f.write(json.dumps(entry, default=str) + '\n')
            
    print(f"Collected {len(result)} reviews and saved to data/reviews_raw.jsonl")

if __name__ == "__main__":
    gather_reviews()