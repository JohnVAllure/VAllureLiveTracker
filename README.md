# VAllure Live Stream Checker

Checks which VAllure talents are currently live on Twitch and YouTube every 15 minutes via GitHub Actions. Results are published to GitHub Pages as a JSON endpoint.

## Setup

### 1. Add repository secrets

Go to **Settings → Secrets and variables → Actions** and add:

- `TWITCH_CLIENT_ID` — Your Twitch app client ID
- `TWITCH_CLIENT_SECRET` — Your Twitch app client secret
- `HOLODEX_API_KEY` — Your Holodex API key

### 2. Enable GitHub Pages

Go to **Settings → Pages** and set:

- **Source**: Deploy from a branch
- **Branch**: `main`
- **Folder**: `/docs`

### 3. Test it

Go to **Actions → Check Live Streams → Run workflow** to trigger it manually. After it runs, check `https://<your-username>.github.io/<repo-name>/live.json`.

## JSON output format

```json
{
  "checked_at": "2025-03-15T12:30:00+00:00",
  "streams": [
    {
      "slug": "stronny",
      "name": "Stronny",
      "platform": "youtube",
      "url": "https://youtube.com/watch?v=..."
    },
    {
      "slug": "ceru",
      "name": "Ceru",
      "platform": "twitch",
      "url": "https://twitch.tv/cerufoxhound"
    }
  ]
}
```

When nobody is live, `streams` is an empty array.

## Editing talents

Edit the `TALENTS` list in `check_live.py` to add/remove talents. Each entry needs:

- `slug` — URL-friendly identifier (matches your website)
- `name` — Display name for the live bar
- `twitch` — Twitch username (lowercase)
- `youtube_id` — YouTube channel ID (the UC... string)

## Notes

- The cron runs every 15 minutes. GitHub Actions cron can sometimes be delayed by a few minutes during high load.
- Twitch usernames in the script may need to be verified/corrected — check each talent's actual Twitch URL.
- Holodex queries by the "VAllure" org tag first, then falls back to individual channel checks.
