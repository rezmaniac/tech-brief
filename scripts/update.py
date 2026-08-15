#!/usr/bin/env python3
"""Fetch public RSS feeds and create static Tech Brief data."""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FEEDS = [
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index", "en"),
    ("TechCrunch", "https://techcrunch.com/feed/", "en"),
    ("The Verge", "https://www.theverge.com/rss/index.xml", "en"),
    ("Hacker News", "https://news.ycombinator.com/rss", "en"),
    ("CzechCrunch", "https://cc.cz/feed/", "cs"),
]
CATEGORIES = {
    "Security": ["security", "vulnerability", "malware", "ransomware", "hack", "breach", "privacy"],
    "Hardware": ["chip", "gpu", "cpu", "hardware", "device", "phone", "laptop", "semiconductor"],
    "AI": ["ai", "artificial intelligence", "model", "openai", "anthropic", "llm", "machine learning"],
    "Dev": ["developer", "code", "software", "programming", "linux", "github", "api"],
    "Startups": ["startup", "funding", "raises", "venture", "ipo"],
}
WORK_SIGNALS = {
    "AI": "Watch for a concrete workflow you could automate or improve.",
    "Dev": "Potential engineering or developer-productivity takeaway.",
    "Security": "Useful context for safer tools, dependencies, or processes.",
    "Hardware": "Worth tracking if devices, compute, or procurement affect your work.",
    "Startups": "A signal about tools, vendors, or shifts in the market.",
}
CURIOUS_TERMS = ["why", "how", "research", "history", "unexpected", "behind", "first", "proč", "jak", "výzkum"]
STACK_TERMS = ["ai", "developer", "software", "automation", "api", "security", "cloud", "data", "productivity", "workflow"]


def clean(value: str | None) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def category_for(title: str, description: str) -> str:
    text = f"{title} {description}".lower()
    for category, terms in CATEGORIES.items():
        if any(re.search(rf"\b{re.escape(term)}\b", text) for term in terms):
            return category
    return "Dev"


def rss_items(source: str, url: str, language: str) -> list[dict]:
    request = Request(url, headers={"User-Agent": "TechBrief/1.0 RSS reader"})
    with urlopen(request, timeout=25) as response:
        root = ET.fromstring(response.read())
    items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
    parsed = []
    for item in items[:12]:
        title = clean(item.findtext("title") or item.findtext("{http://www.w3.org/2005/Atom}title"))
        link = clean(item.findtext("link"))
        if not link:
            link_node = item.find("{http://www.w3.org/2005/Atom}link")
            link = link_node.get("href", "") if link_node is not None else ""
        description = clean(item.findtext("description") or item.findtext("{http://www.w3.org/2005/Atom}summary"))
        if title and link:
            category = category_for(title, description)
            parsed.append({"title": title, "url": link, "description": description[:280] or "Open the original source for the full story.", "source": source, "language": language, "category": category, "workSignal": WORK_SIGNALS[category]})
    return parsed


def sample_stories() -> list[dict]:
    return [{"title": "New AI models reshape the developer toolkit", "description": "A placeholder story used until the first scheduled feed update.", "url": "https://news.ycombinator.com/", "source": "Tech Brief", "language": "en", "category": "AI", "workSignal": WORK_SIGNALS["AI"]}]


def select_diverse(stories: list[dict], limit: int = 18) -> list[dict]:
    """Interleave feeds so a prolific publisher cannot dominate the page."""
    buckets: dict[str, deque[dict]] = defaultdict(deque)
    source_order = [source for source, _, _ in FEEDS]
    for story in stories:
        buckets[story["source"]].append(story)
    source_order.extend(source for source in buckets if source not in source_order)
    selected = []
    while len(selected) < limit:
        added = False
        for source in source_order:
            if buckets[source] and len(selected) < limit:
                selected.append(buckets[source].popleft())
                added = True
        if not added:
            return selected
    return selected


def choose_curiosity(stories: list[dict]) -> dict:
    for story in reversed(stories):
        text = f"{story['title']} {story['description']}".lower()
        if any(term in text for term in CURIOUS_TERMS):
            return story
    return stories[-1]


def episode_script(stories: list[dict], weekly: bool = False) -> str:
    english_stories = [story for story in stories if story.get("language") == "en"][:6]
    intro = "Welcome to the Tech Brief weekly Stack Review." if weekly else "Welcome to Tech Brief. Here is your daily Work Radar."
    lines = [intro]
    for number, story in enumerate(english_stories, start=1):
        lines.append(f"Story {number}. {story['title']}. {story['description']} Source: {story['source']}.")
    lines.append("That was your Tech Brief. Open the website for all source links, including Czech stories.")
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
    parser.add_argument("--weekly", action="store_true", help="Create the weekly Stack Review files.")
    args = parser.parse_args()
    DATA.mkdir(exist_ok=True)
    stories: list[dict] = []
    if not args.sample:
        for source, url, language in FEEDS:
            try:
                stories.extend(rss_items(source, url, language))
            except Exception as error:
                print(f"Skipping {source}: {error}", file=sys.stderr)
    if not stories:
        stories = sample_stories()
    unique = {story["url"]: story for story in stories}
    stories = select_diverse(list(unique.values()))
    generated = datetime.now(timezone.utc)
    if args.weekly:
        ranked = sorted(stories, key=lambda story: sum(term in f"{story['title']} {story['description']}".lower() for term in STACK_TERMS), reverse=True)
        payload = {"generatedAt": generated.isoformat(), "label": "Weekly Stack Review", "episodeLength": max(3, round(len(ranked[:6]) * 0.75)), "topStory": ranked[0], "stories": ranked[:12], "curiosity": choose_curiosity(ranked), "stackNote": "Starter focus: AI, software, automation, APIs, security, cloud and data. Replace these with your real working stack when you are ready."}
        (DATA / "weekly.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        (DATA / "weekly.txt").write_text(episode_script(ranked, weekly=True), encoding="utf-8")
        return
    payload = {"generatedAt": generated.isoformat(), "label": "Daily Work Radar", "episodeLength": max(3, round(len(stories[:6]) * 0.75)), "topStory": stories[0], "stories": stories, "curiosity": choose_curiosity(stories)}
    (DATA / "news.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (DATA / "episode.txt").write_text(episode_script(stories), encoding="utf-8")
    write_podcast(stories, generated)


if __name__ == "__main__":
    main()
