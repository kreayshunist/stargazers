import argparse
import json
import os

import requests
from dotenv import load_dotenv


def load_stargazers(path: str):
    """Load stargazer data from saved_state file."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    decoder = json.JSONDecoder()
    stargazers, _ = decoder.raw_decode(content)
    return stargazers


def send_records(url: str, key: str, records: list):
    """Send records individually to the Supabase REST endpoint."""
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    for rec in records:
        resp = requests.post(url, headers=headers, json=rec)
        if resp.status_code >= 400:
            print(f"Failed to send {rec.get('user', {}).get('login')}: {resp.status_code} {resp.text}")
        else:
            print(f"Sent {rec.get('user', {}).get('login')}")


def main():
    parser = argparse.ArgumentParser(
        description="Send stargazer data with emails to Supabase"
    )
    parser.add_argument(
        "--repo", required=True, help="Repository in owner/repo format"
    )
    parser.add_argument(
        "--supabase-url",
        help="Full Supabase REST endpoint URL (e.g. https://project.supabase.co/rest/v1/table)",
    )
    parser.add_argument("--supabase-key", help="Supabase service role or anon key")
    parser.add_argument("--cache", default="./stargazer_cache", help="Cache directory")
    args = parser.parse_args()

    # Load environment variables from a .env file if present
    load_dotenv()

    url = args.supabase_url or os.getenv("SUPABASE_URL")
    key = args.supabase_key or os.getenv("SUPABASE_KEY")

    if not url or not key:
        parser.error("Supabase URL and key must be provided via arguments or environment variables")

    saved_state = os.path.join(args.cache, args.repo, "saved_state")
    if not os.path.exists(saved_state):
        raise FileNotFoundError(f"Saved state not found: {saved_state}")

    stargazers = load_stargazers(saved_state)
    with_emails = [s for s in stargazers if s.get('user', {}).get('email')]

    print(f"Sending {len(with_emails)} stargazers with emails to Supabase...")
    send_records(url, key, with_emails)


if __name__ == "__main__":
    main()
