import os
import requests
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

GDELT_URL = "https://api.gdeltproject.org/api/v2/doc/doc"

def fetch_gdelt(query="financial markets OR stocks OR bank", maxrecords=20):
    params = {
        "query": query,
        "mode": "artlist",
        "format": "json",
        "maxrecords": maxrecords,
        "timespan": "24h",
        "sort": "HybridRel",
    }
    r = requests.get(GDELT_URL, params=params, timeout=15)
    r.raise_for_status()
    payload = r.json()
    rows = []
    for a in payload.get("articles", []):
        rows.append({
            "source": "GDELT",
            "entity": query,
            "title": a.get("title",""),
            "text": a.get("title",""),
            "url": a.get("url",""),
            "published_at": a.get("seendate",""),
        })
    return rows

def fetch_newsapi(query="financial markets OR stocks", api_key=None, page_size=20):
    api_key = api_key or os.getenv("NEWSAPI_KEY")
    if not api_key:
        return []
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size,
        "apiKey": api_key,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    payload = r.json()
    rows = []
    for a in payload.get("articles", []):
        text = " ".join(filter(None, [a.get("title"), a.get("description"), a.get("content")]))
        rows.append({
            "source": "NewsAPI",
            "entity": query,
            "title": a.get("title",""),
            "text": text,
            "url": a.get("url",""),
            "published_at": a.get("publishedAt",""),
        })
    return rows

def load_social_demo(path="data/social_posts.csv"):
    df = pd.read_csv(path)
    return df.to_dict("records")

def collect_all(query="financial markets OR stocks", use_live=True):
    records = []
    if use_live:
        try:
            records.extend(fetch_gdelt(query=query))
        except Exception as e:
            print(f"GDELT unavailable: {e}")
        try:
            records.extend(fetch_newsapi(query=query))
        except Exception as e:
            print(f"NewsAPI unavailable or key missing: {e}")
    records.extend(load_social_demo())
    return records