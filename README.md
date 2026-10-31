# Tech Brief

A zero-cost daily technology news site, designed for GitHub Pages.

## What it does

- Reads public RSS feeds from Ars Technica, TechCrunch, The Verge, Hacker News and CzechCrunch.
- Builds a mobile-first page with a Top Story, Daily Work Radar, Curiosity item and category filters.
- Updates daily at 06:00 UTC through GitHub Actions.
- Creates a Weekly Stack Review every Sunday at 10:00 Europe/Prague time.

## Publish it for free

1. Create a public GitHub repository named `tech-brief`.
2. Upload these files to the repository root.
3. In GitHub, open **Settings → Pages**, choose **Deploy from a branch**, then select `main` and `/ (root)`.
4. Open the **Actions** tab and manually run “Update daily Tech Brief” once to create the first live content.

The website will be available at `https://rezmaniac.github.io/tech-brief/`.

## Notes

Audio generation and the podcast player have been retired. Daily and weekly workflows publish text only. Earlier audio files remain recoverable in Git history.
