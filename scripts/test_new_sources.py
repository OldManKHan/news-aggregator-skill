#!/usr/bin/env python3
"""
Test script for candidate RSS/API source URLs.
Tests accessibility, response format, and parseability.
"""

import sys
import os
import json
import time
import requests
import urllib3

# Add scripts dir to path so we can import rss_parser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rss_parser import parse_rss_content

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
              "image/avif,image/webp,*/*;q=0.8",
}
TIMEOUT = 15

# ── Source definitions ──────────────────────────────────────────────
RSS_SOURCES = [
    # International Politics
    ("Reuters World",       "https://feeds.reuters.com/Reuters/worldNews"),
    ("BBC World",           "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("The Guardian World",  "https://www.theguardian.com/world/rss"),
    ("Al Jazeera",          "https://www.aljazeera.com/xml/rss/all.xml"),
    ("DW News",             "https://rss.dw.com/rdf/rss-en-all"),
    ("France24",            "https://www.france24.com/en/rss"),
    ("NHK World",           "https://www3.nhk.or.jp/rss/news/cat0.xml"),
    ("AP News (RSSHub)",    "https://rsshub.app/apnews/topics/world-news"),
    # International Finance
    ("CNBC World",          "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100727362"),
    ("MarketWatch",         "https://feeds.marketwatch.com/marketwatch/topstories/"),
    ("Seeking Alpha",       "https://seekingalpha.com/market_currents.xml"),
    ("Nikkei Asia",         "https://asia.nikkei.com/rss"),
    ("FT Markets",          "https://www.ft.com/markets?format=rss"),
    ("Bloomberg Markets",   "https://feeds.bloomberg.com/markets/news.rss"),
    ("Economist Finance",   "https://www.economist.com/finance-and-economics/rss.xml"),
]

API_SOURCES = [
    ("Eastmoney Flash News", "https://push2ex.eastmoney.com/getAllStockChanges?type=8201&pageindex=0&pagesize=10"),
]


def detect_content_type(response):
    """Return a human-readable content type string."""
    ct = response.headers.get("Content-Type", "")
    if "xml" in ct or "rss" in ct or "atom" in ct:
        return "XML/RSS"
    if "json" in ct:
        return "JSON"
    if "html" in ct:
        return "HTML"
    return ct or "unknown"


def test_rss_source(name, url):
    """Test a single RSS/Atom feed URL."""
    result = {
        "name": name,
        "url": url,
        "status_code": None,
        "content_type": None,
        "items_parsed": 0,
        "sample_title": None,
        "issues": [],
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                            verify=False, allow_redirects=True)
        result["status_code"] = resp.status_code

        # Track redirects
        if resp.history:
            chain = " -> ".join(str(r.status_code) for r in resp.history)
            result["issues"].append(f"Redirected ({chain}) to {resp.url}")

        result["content_type"] = detect_content_type(resp)

        if resp.status_code != 200:
            result["issues"].append(f"Non-200 status: {resp.status_code}")
            return result

        body = resp.text[:500].lower()

        # Paywall / blocking checks
        if "subscribe" in body and "sign in" in body:
            result["issues"].append("Possible paywall detected")
        if resp.status_code == 200 and len(resp.content) < 200:
            result["issues"].append(f"Very short response ({len(resp.content)} bytes)")

        # Check if response looks like HTML instead of XML feed
        if result["content_type"] == "HTML" and "<rss" not in body and "<feed" not in body and "<rdf" not in body:
            result["issues"].append("Response is HTML, not an RSS/Atom feed")

        # Parse with rss_parser
        resp.encoding = resp.apparent_encoding or "utf-8"
        items = parse_rss_content(resp.content, name, limit=3)
        result["items_parsed"] = len(items)

        if items:
            result["sample_title"] = items[0]["title"]
        else:
            result["issues"].append("No items parsed from feed")

    except requests.exceptions.Timeout:
        result["issues"].append("Request timed out (15s)")
    except requests.exceptions.ConnectionError as e:
        result["issues"].append(f"Connection error: {e}")
    except Exception as e:
        result["issues"].append(f"Error: {e}")

    return result


def test_api_source(name, url):
    """Test a JSON API endpoint."""
    result = {
        "name": name,
        "url": url,
        "status_code": None,
        "content_type": None,
        "items_parsed": 0,
        "sample_title": None,
        "issues": [],
    }

    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT,
                            verify=False, allow_redirects=True)
        result["status_code"] = resp.status_code
        result["content_type"] = detect_content_type(resp)

        if resp.history:
            chain = " -> ".join(str(r.status_code) for r in resp.history)
            result["issues"].append(f"Redirected ({chain}) to {resp.url}")

        if resp.status_code != 200:
            result["issues"].append(f"Non-200 status: {resp.status_code}")
            return result

        try:
            data = resp.json()
        except json.JSONDecodeError:
            result["issues"].append("Response is not valid JSON")
            return result

        # Eastmoney specific parsing
        if "eastmoney" in url:
            inner = data.get("data")
            if inner is None:
                result["issues"].append("data is null (market may be closed)")
            else:
                allstock = inner.get("allstock", [])
                result["items_parsed"] = len(allstock)
                if allstock:
                    item = allstock[0]
                    info = item.get("info", "")
                    code = item.get("c", "")
                    result["sample_title"] = f"[{code}] {info}"[:120]
                else:
                    result["issues"].append("No items in data.allstock")
        else:
            # Generic JSON: report top-level keys
            result["issues"].append(f"Top-level keys: {list(data.keys())[:10]}")

    except requests.exceptions.Timeout:
        result["issues"].append("Request timed out (15s)")
    except requests.exceptions.ConnectionError as e:
        result["issues"].append(f"Connection error: {e}")
    except Exception as e:
        result["issues"].append(f"Error: {e}")

    return result


def print_report(results):
    """Print a formatted report of all test results."""
    ok_count = 0
    warn_count = 0
    fail_count = 0

    print("=" * 80)
    print("SOURCE FEED TEST REPORT")
    print("=" * 80)

    for r in results:
        has_items = r["items_parsed"] > 0
        has_issues = len(r["issues"]) > 0
        status_ok = r["status_code"] == 200

        if has_items and status_ok and not has_issues:
            tag = "OK"
            ok_count += 1
        elif has_items and status_ok:
            tag = "WARN"
            warn_count += 1
        else:
            tag = "FAIL"
            fail_count += 1

        print(f"\n[{tag}] {r['name']}")
        print(f"  URL:          {r['url']}")
        print(f"  HTTP Status:  {r['status_code']}")
        print(f"  Content-Type: {r['content_type']}")
        print(f"  Items Parsed: {r['items_parsed']}")
        if r["sample_title"]:
            print(f"  Sample Title: {r['sample_title']}")
        if r["issues"]:
            for issue in r["issues"]:
                print(f"  !! {issue}")

    print("\n" + "=" * 80)
    print(f"SUMMARY: {ok_count} OK / {warn_count} WARN / {fail_count} FAIL "
          f"(total {len(results)})")
    print("=" * 80)


def main():
    results = []

    print("Testing RSS/Atom feeds...")
    for name, url in RSS_SOURCES:
        print(f"  Testing {name}...", flush=True)
        results.append(test_rss_source(name, url))

    print("Testing API sources...")
    for name, url in API_SOURCES:
        print(f"  Testing {name}...", flush=True)
        results.append(test_api_source(name, url))

    print()
    print_report(results)


if __name__ == "__main__":
    main()
