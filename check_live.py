import json
import os
import requests
from datetime import datetime, timezone

# ── Talent config ──
# Add or remove talents here. Each needs a slug (for your site),
# display name, and their Twitch username + YouTube channel ID.
# Leave twitch or youtube_id empty if they don't use that platform.

TALENTS = [
    {"slug": "azura",   "name": "Azura",   "twitch": "azuradulait",      "youtube_id": "UCyB5jnJzSFmSvMQ-cFJMKJA"},
    {"slug": "icey",    "name": "Icey",     "twitch": "iceysnowpaws",     "youtube_id": "UCoNMWPcMqUxKSfpdkezuQYQ"},
    {"slug": "immy",    "name": "Immy",     "twitch": "immybisou",        "youtube_id": "UC7U7JOmMFKGseGBMiVidJOA"},
    {"slug": "mercy",   "name": "Mercy",    "twitch": "mercymodiste",     "youtube_id": "UCeMGnttZRMvi99LNOzmp_YA"},
    {"slug": "shibi",   "name": "Shibi",    "twitch": "shibicottonbum",   "youtube_id": "UC8cEqHJME6z1IvJP-grkh8A"},
    {"slug": "stronny", "name": "Stronny",  "twitch": "stronnycuttles",   "youtube_id": "UCCDh6BCZKNPR6pXPxiLtkwg"},
    {"slug": "ceru",    "name": "Ceru",     "twitch": "cerufoxhound",     "youtube_id": "UCkbFttoKBBaLTQfOa-ouGvA"},
    {"slug": "mara",    "name": "Mara",     "twitch": "maravespidae",     "youtube_id": "UCEcMKnqDNLCmVCZS1GNfemQ"},
    {"slug": "phyla",   "name": "Phyla",    "twitch": "phylaeinrose",     "youtube_id": "UCd6Nb7mH-FAxK-7VLcKlFtg"},
    {"slug": "quetzu",  "name": "Quetzu",   "twitch": "quetzusolscale",   "youtube_id": "UCMqWQKReJ3R1UM5JKBvEJ8Q"},
    {"slug": "sinthya", "name": "Sinthya",  "twitch": "sinthyasanguine",  "youtube_id": "UCXMSqaz2NO-q0CxiiSn2oAA"},
    {"slug": "willo",   "name": "Willo",    "twitch": "willowildfire",    "youtube_id": "UCjh1PRzBvFxANqJhIGpjCzg"},
]

def get_twitch_token(client_id, client_secret):
    """Get an app access token from Twitch."""
    resp = requests.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
    })
    resp.raise_for_status()
    return resp.json()["access_token"]

def check_twitch(client_id, client_secret):
    """Check which talents are live on Twitch. Returns a dict of twitch_username -> stream_url."""
    token = get_twitch_token(client_id, client_secret)

    usernames = [t["twitch"] for t in TALENTS if t["twitch"]]
    if not usernames:
        return {}

    # Twitch allows up to 100 user_login params per request
    resp = requests.get(
        "https://api.twitch.tv/helix/streams",
        headers={
            "Client-ID": client_id,
            "Authorization": f"Bearer {token}",
        },
        params=[("user_login", u) for u in usernames],
    )
    resp.raise_for_status()

    live = {}
    for stream in resp.json().get("data", []):
        username = stream["user_login"].lower()
        live[username] = f"https://twitch.tv/{username}"

    return live

def check_holodex(api_key):
    """Check which talents are live on YouTube via Holodex. Returns a dict of youtube_channel_id -> stream_url."""
    channel_ids = [t["youtube_id"] for t in TALENTS if t["youtube_id"]]
    if not channel_ids:
        return {}

    live = {}

    # Holodex /live endpoint — check each channel
    # We can batch by checking the VAllure org, or query individually
    resp = requests.get(
        "https://holodex.net/api/v2/live",
        headers={"X-APIKEY": api_key},
        params={
            "org": "VAllure",
            "status": "live",
        },
    )

    if resp.status_code == 200:
        for stream in resp.json():
            channel_id = stream.get("channel", {}).get("id", "")
            video_id = stream.get("id", "")
            if channel_id and video_id:
                live[channel_id] = f"https://youtube.com/watch?v={video_id}"

    # If org search didn't work, fall back to checking individual channels
    if not live:
        for cid in channel_ids:
            resp = requests.get(
                "https://holodex.net/api/v2/live",
                headers={"X-APIKEY": api_key},
                params={"channel_id": cid, "status": "live"},
            )
            if resp.status_code == 200:
                for stream in resp.json():
                    video_id = stream.get("id", "")
                    if video_id:
                        live[cid] = f"https://youtube.com/watch?v={video_id}"

    return live

def main():
    client_id = os.environ.get("TWITCH_CLIENT_ID", "")
    client_secret = os.environ.get("TWITCH_CLIENT_SECRET", "")
    holodex_key = os.environ.get("HOLODEX_API_KEY", "")

    streams = []

    # Check Twitch
    twitch_live = {}
    if client_id and client_secret:
        try:
            twitch_live = check_twitch(client_id, client_secret)
            print(f"Twitch: {len(twitch_live)} live")
        except Exception as e:
            print(f"Twitch error: {e}")

    # Check YouTube via Holodex
    holodex_live = {}
    if holodex_key:
        try:
            holodex_live = check_holodex(holodex_key)
            print(f"Holodex: {len(holodex_live)} live")
        except Exception as e:
            print(f"Holodex error: {e}")

    # Build the streams list
    for talent in TALENTS:
        # Check Twitch
        twitch_user = talent["twitch"].lower()
        if twitch_user in twitch_live:
            streams.append({
                "slug": talent["slug"],
                "name": talent["name"],
                "platform": "twitch",
                "url": twitch_live[twitch_user],
            })

        # Check YouTube
        yt_id = talent["youtube_id"]
        if yt_id in holodex_live:
            streams.append({
                "slug": talent["slug"],
                "name": talent["name"],
                "platform": "youtube",
                "url": holodex_live[yt_id],
            })

    # Write output
    output = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "streams": streams,
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/live.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"Output: {len(streams)} streams live")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
