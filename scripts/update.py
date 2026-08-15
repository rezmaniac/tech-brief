#!/usr/bin/env python3
"""Fetch public RSS feeds and create the static daily Tech Brief data."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FEEDS = {
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Hacker News": "https://news.ycombinator.com/rss",
}
CATEGORIES = {
    "Security": ["security", "vulnerability", "malware", "ransomware", "hack", "breach", "privacy"],
    "Hardware": ["chip", "gpu", "cpu", "hardware", "device", "phone", "laptop", "semiconductor"],
    "AI": ["ai", "artificial intelligence", "model", "openai", "anthropic", "llm", "machine learning"],
    "Dev": ["developer", "code", "software", "programming", "linux", "github", "api"],
    "Startups": ["startup", "funding", "raises", "venture", "ipo"],
}


def clean(value: str | None) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def category_for(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    for category, terms in CATEGORIES.items():
        if any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms):
            return category
    return "Dev"


def rss_items(source: str, url: str) -> list[dict]:
    request = Request(url, headers={"User-Agent": "TechBrief/1.0 RSS reader"})
    with urlopen(request, timeout=25) as response:
        root = ET.fromstring(response.read())
    items = root.findall(".//item")
    if not items:
        items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    parsed = []
    for item in items[:12]:
        title = clean(item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title"))
        link = clean(item.findtext("link"))
        if not link:
            link_node = item.find("{http://www.w3.org/2005/Atom}link")
            link = link_node.get("href", "") if link_node is not None else ""
        description = clean(item.findtext("description") or item.findtext("{http://www.w3.org/2005/Atom}summary"))
        if title and link:
            parsed.append({"title": title, "url": link, "description": description[:280] or "Open the original source for the full story.", "source": source, "category": category_for(title, description)})
    return parsed


def sample_stories() -> list[dict]:
    return [
        {"title": "New AI models reshape the developer toolkit", "description": "A placeholder story used until the first scheduled feed update.", "url": "https://news.ycombinator.com/", "source": "Tech Brief", "category": "AI"},
        {"title": "Chip launch raises the bar", "description": "The first live update will replace this sample item.", "url": "https://arstechnica.com/", "source": "Tech Brief", "category": "Hardware"},
        {"title": "Security watch: keep your dependencies current", "description": "A sample entry for the Security category.", "url": "https://www.theverge.com/", "source": "Tech Brief", "category": "Security"},
    ]


def episode_script(stories: list[dict]) -> str:
    lines = ["Welcome to Tech Brief. Here are the stories worth knowing today."]
    for number, story in enumerate(stories[:6], start=1):
        lines.append(f"Story {number}. {story['title']}. {story['description']} Source: {story['source']}.")
    lines.append("That was your Tech Brief. Open the website for all source links.")
    return "\n".join(lines)


def write_podcast(stories: list[dict], generated: datetime) -> None:
    site_url = "https://rezmaniac.github.io/tech-brief"
    date = generated.strftime("%a, %d %b %Y %H:%M:%S +0000")
    title = html.escape(f"Tech Brief — {generated.strftime('%d %b %Y')}")
    feed = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Tech Brief</title><link>{site_url}</link><description>A daily technology news briefing.</description><language>en</language>
<item><title>{title}</title><guid>{generated.strftime('%Y-%m-%d')}</guid><pubDate>{date}</pubDate><enclosure url="{site_url}/data/today.mp3" length="0" type="audio/mpeg"/></item>
</channel></rss>'''
    (DATA / "podcast.xml").write_text(feed, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", action="store_true", help="Create offline sample data.")
    args = parser.parse_args()
    DATA.mkdir(exist_ok=True)
    stories: list[dict] = []
    if not args.sample:
        for source, url in FEEDS.items():
            try:
                stories.extend(rss_items(source, url))
            except Exception as error:
                print(f"Skipping {source}: {error}", file=sys.stderr)
    if not stories:
        stories = sample_stories()
    unique = {story["url"]: story for story in stories}
    stories = list(unique.values())[:18]
    generated = datetime.now(timezone.utc)
    payload = {"generatedAt": generated.isoformat(), "episodeLength": max(3, round(len(stories[:6]) * 0.75)), "topStory": stories[0], "stories": stories}
    (DATA / "news.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "episode.txt").write_text(episode_script(stories), encoding="utf-8")
    write_podcast(stories, generated)


if __name__ == "__main__":
    main()
