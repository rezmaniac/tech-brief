# Tech Brief

A zero-cost daily technology news site and English audio briefing, designed for GitHub Pages.

## What it does

- Reads public RSS feeds from Ars Technica, TechCrunch, The Verge, and Hacker News.
- Builds a mobile-first page with a Top Story and category filters.
- Produces a short English MP3 briefing using the open-source Kokoro neural voice `af_heart`.
- Updates daily at 06:00 UTC through GitHub Actions.

## Publish it for free

1. Create a public GitHub repository named `tech-brief`.
2. Upload these files to the repository root.
3. In GitHub, open **Settings → Pages**, choose **Deploy from a branch**, then select `main` and `/ (root)`.
4. Open the **Actions** tab and manually run “Update daily Tech Brief” once to create the first live content and MP3.

The website will be available at `https://rezmaniac.github.io/tech-brief/`.

## Notes

The audio uses Kokoro, an open-weight neural TTS model. The voice can be changed in the GitHub Action without affecting the web app.
