# Power Intelligence

Mobile-friendly personal news dashboard for power infrastructure and data centers.

## Run locally

From the project folder run `python -m http.server 8000`, then visit `http://localhost:8000`.

Run `python scripts/update.py` to collect public RSS articles. Without an API key, article titles and excerpts remain in their original language; no AI translation is claimed. With `OPENAI_API_KEY` set, the updater generates Chinese AI summaries of newly fetched articles. Summaries use RSS metadata only, not full articles.

## Publish to GitHub Pages

1. Create a GitHub repository and upload the contents of this folder, including `.github/workflows/daily.yml`.
2. Repository **Settings → Pages → Build and deployment → Deploy from a branch**, select `main` and `/ (root)`.
3. Repository **Settings → Secrets and variables → Actions → New repository secret**: name it `OPENAI_API_KEY` and enter your own OpenAI API key. Do not paste keys into files or chat.
4. Open **Actions → Daily Industry Update → Run workflow** to fetch the first real stories.
5. The published URL will generally be `https://USERNAME.github.io/REPOSITORY/`. Replace USERNAME and REPOSITORY with yours.

The workflow runs daily at 06:15 UTC (07:15 in Denmark winter, 08:15 summer), subject to GitHub Actions scheduling delays. Adjust the cron for your preferred schedule. Public GitHub Pages repositories publish the news dataset publicly; do not put confidential company information in the repository. Local bookmarks and notes stay in browser localStorage and are not synced between devices. GitHub Actions and the OpenAI API may incur costs/usage limits depending on your plan. RSS providers can change feeds or block requests. News items are filtered by simple keywords; the first version is not a comprehensive licensed news service. The workflow keeps up to 500 articles.

## Project structure

- `index.html` — responsive searchable website and browser-local bookmarks/notes
- `data/articles.json` — generated public article archive
- `scripts/update.py` — RSS collection and optional AI summaries
- `.github/workflows/daily.yml` — daily automation
