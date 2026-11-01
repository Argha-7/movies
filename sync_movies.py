#!/usr/bin/env python3
"""
MovieBox Blogger Sync Bot
Automatically scrapes trending & new movies, builds deep-link play buttons for VLC & MX Player,
and posts them to your Blogger website or static web portal via GitHub Actions.
"""

import os
import sys
import json
import smtplib
import argparse

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import requests

HISTORY_FILE = Path(__file__).parent / "published_history.json"
CINEMETA_CATALOG = "https://v3-cinemeta.strem.io/catalog/movie/top.json"
CINEMETA_META = "https://v3-cinemeta.strem.io/meta/movie/{id}.json"

def load_history() -> set:
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("published_ids", []))
        except Exception as e:
            print(f"[!] Warning reading history file: {e}")
    return set()

def save_history(published_ids: set):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"published_ids": sorted(list(published_ids))}, f, indent=2)
    print(f"[+] Updated history: {len(published_ids)} total movies tracked.")

def fetch_top_movies(limit=15):
    print(f"[*] Fetching catalog from Cinemeta...")
    try:
        resp = requests.get(CINEMETA_CATALOG, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("metas", [])
        return items[:limit]
    except Exception as e:
        print(f"[x] Error fetching catalog: {e}")
        return []

def fetch_movie_details(imdb_id: str) -> dict:
    url = CINEMETA_META.format(id=imdb_id)
    try:
        resp = requests.get(url, timeout=12)
        resp.raise_for_status()
        meta = resp.json().get("meta", {})
        return meta
    except Exception as e:
        print(f"[!] Could not fetch extra details for {imdb_id}: {e}")
        return {}

def build_stream_links(imdb_id: str, title: str) -> dict:
    """
    Builds video player links:
    - Android Deep Link for VLC Player
    - Android Deep Link for MX Player
    - Web Embed Player for Desktop & in-browser watching
    """
    # Web streaming mirrors
    web_player_vidsrc = f"https://vidsrc.cc/v2/embed/movie/{imdb_id}"
    web_player_embedsu = f"https://embed.su/embed/movie/{imdb_id}"
    
    # Direct stream endpoints and intents
    # Android Intent to launch VLC directly:
    # intent:<url>#Intent;package=org.videolan.vlc;action=android.intent.action.VIEW;type=video/*;end
    vlc_intent = f"intent:{web_player_vidsrc}#Intent;package=org.videolan.vlc;action=android.intent.action.VIEW;type=video/*;end"
    
    # Android Intent to launch MX Player directly:
    mx_intent = f"intent:{web_player_vidsrc}#Intent;package=com.mxtech.videoplayer.ad;action=android.intent.action.VIEW;type=video/*;end"

    return {
        "vlc_intent": vlc_intent,
        "mx_intent": mx_intent,
        "web_player_vidsrc": web_player_vidsrc,
        "web_player_embedsu": web_player_embedsu,
    }

def generate_blogger_html(movie: dict, links: dict) -> str:
    title = movie.get("name") or "Movie"
    year = movie.get("year") or movie.get("releaseInfo") or ""
    poster = movie.get("poster") or "https://via.placeholder.com/400x600?text=No+Poster"
    genres = ", ".join(movie.get("genres", [])) or "Movies"
    description = movie.get("description") or "No synopsis available."
    imdb_rating = movie.get("imdbRating") or "8.0"
    runtime = movie.get("runtime") or "1h 50m"

    html = f"""
<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f1016; color: #f0f0f0; padding: 24px 16px; border-radius: 16px; max-width: 600px; margin: 0 auto; box-shadow: 0 10px 30px rgba(0,0,0,0.5); border: 1px solid #232533;">
  
  <!-- Movie Poster -->
  <div style="text-align: center; margin-bottom: 20px;">
    <img src="{poster}" alt="{title}" style="width: 100%; max-width: 320px; border-radius: 12px; box-shadow: 0 8px 25px rgba(0,0,0,0.6); border: 2px solid #2a2d3e;" />
  </div>

  <!-- Title & Year -->
  <h1 style="font-size: 24px; font-weight: 800; text-align: center; margin: 10px 0; color: #ffffff; letter-spacing: -0.5px;">
    {title} <span style="font-size: 18px; color: #a0a5b8; font-weight: 500;">({year})</span>
  </h1>

  <!-- Metadata Badges -->
  <div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; margin: 14px 0 20px 0;">
    <span style="background: #e50914; color: #ffffff; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 6px;">⭐ {imdb_rating} / 10</span>
    <span style="background: #252837; color: #ffffff; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 6px;">⏱️ {runtime}</span>
    <span style="background: #252837; color: #ffffff; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 6px;">🎬 {genres}</span>
    <span style="background: #10b981; color: #ffffff; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 6px;">4K / 1080p FHD</span>
  </div>

  <!-- Synopsis -->
  <div style="background: #181922; padding: 14px; border-radius: 10px; margin-bottom: 24px; border-left: 4px solid #e50914;">
    <p style="font-size: 14px; line-height: 1.6; margin: 0; color: #d1d5db;">
      {description}
    </p>
  </div>

  <!-- Action Play Buttons for Mobile and Web -->
  <div style="display: flex; flex-direction: column; gap: 12px;">

    <!-- VLC Mobile Player Button -->
    <a href="{links['vlc_intent']}" 
       style="display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); color: #ffffff; text-decoration: none; padding: 14px 20px; border-radius: 10px; font-size: 16px; font-weight: 700; box-shadow: 0 4px 15px rgba(249, 115, 22, 0.4); text-align: center;">
      <span style="margin-right: 8px; font-size: 18px;">▶</span> Open in VLC Player (Android)
    </a>

    <!-- MX Player Button -->
    <a href="{links['mx_intent']}" 
       style="display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%); color: #ffffff; text-decoration: none; padding: 14px 20px; border-radius: 10px; font-size: 16px; font-weight: 700; box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4); text-align: center;">
      <span style="margin-right: 8px; font-size: 18px;">▶</span> Open in MX Player (Android)
    </a>

    <!-- In-Browser Web Player -->
    <a href="{links['web_player_vidsrc']}" target="_blank" rel="noopener noreferrer"
       style="display: flex; align-items: center; justify-content: center; background: #232533; color: #e2e8f0; text-decoration: none; padding: 12px 20px; border-radius: 10px; font-size: 14px; font-weight: 600; border: 1px solid #3b3f54; text-align: center;">
      <span style="margin-right: 8px;">🌐</span> Watch in Browser (Desktop / iPhone)
    </a>

  </div>

  <!-- Note for Mobile Users -->
  <p style="text-align: center; font-size: 12px; color: #71717a; margin-top: 18px; margin-bottom: 0;">
    💡 <i>Tip: Mobile me "Open in VLC" par click karte hi direct playback shuru ho jayega!</i>
  </p>

</div>
"""
    return html.strip()

def send_blogger_email(subject: str, html_content: str, secret_email: str, smtp_user: str, smtp_pass: str) -> bool:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = smtp_user
        msg["To"] = secret_email

        part = MIMEText(html_content, "html", "utf-8")
        msg.attach(part)

        print(f"[*] Sending email to Blogger: {secret_email}...")
        # Connecting with SSL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, [secret_email], msg.as_string())

        print(f"[+] Successfully published via Email: {subject}")
        return True
    except Exception as e:
        print(f"[x] Error sending email to Blogger: {e}")
        return False

def post_blogger_api(title: str, html_content: str, blog_id: str, access_token: str, labels: list) -> bool:
    try:
        url = f"https://www.googleapis.com/blogger/v3/blogs/{blog_id}/posts/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "kind": "blogger#post",
            "title": title,
            "content": html_content,
            "labels": labels
        }
        res = requests.post(url, headers=headers, json=payload, timeout=20)
        res.raise_for_status()
        print(f"[+] Successfully published via Blogger API: {title}")
        return True
    except Exception as e:
        print(f"[x] Blogger API error: {e}")
        return False

def generate_static_portal(movies_list: list):
    """Generates an index.html file suitable for GitHub Pages or local preview"""
    public_dir = Path(__file__).parent / "public"
    public_dir.mkdir(exist_ok=True)
    
    cards_html = ""
    for item in movies_list:
        m = item["movie"]
        l = item["links"]
        title = m.get("name") or "Movie"
        year = m.get("year") or m.get("releaseInfo") or ""
        poster = m.get("poster") or ""
        cards_html += f"""
        <div class="movie-card">
            <img src="{poster}" alt="{title}" loading="lazy" />
            <div class="card-info">
                <h3>{title} ({year})</h3>
                <div class="actions">
                    <a href="{l['vlc_intent']}" class="btn btn-vlc">▶ VLC</a>
                    <a href="{l['mx_intent']}" class="btn btn-mx">▶ MX</a>
                    <a href="{l['web_player_vidsrc']}" target="_blank" class="btn btn-web">🌐 Watch</a>
                </div>
            </div>
        </div>
        """

    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MovieBox Mobile Stream Portal</title>
    <style>
        body {{
            background: #0f1016;
            color: #fff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        h1 {{ margin: 0; font-size: 26px; color: #f97316; }}
        p.subtitle {{ color: #94a3b8; font-size: 14px; margin-top: 5px; }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .movie-card {{
            background: #181922;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #232533;
            transition: transform 0.2s;
        }}
        .movie-card:hover {{ transform: translateY(-4px); }}
        .movie-card img {{
            width: 100%;
            height: 270px;
            object-fit: cover;
        }}
        .card-info {{ padding: 12px; }}
        .card-info h3 {{
            font-size: 14px;
            margin: 0 0 10px 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .actions {{
            display: flex;
            gap: 6px;
        }}
        .btn {{
            flex: 1;
            text-align: center;
            text-decoration: none;
            padding: 8px 4px;
            font-size: 11px;
            font-weight: bold;
            border-radius: 6px;
            color: #fff;
        }}
        .btn-vlc {{ background: #ea580c; }}
        .btn-mx {{ background: #0284c7; }}
        .btn-web {{ background: #374151; }}
    </style>
</head>
<body>
    <header>
        <h1>MovieBox Stream Portal</h1>
        <p class="subtitle">Tap "VLC" or "MX" on mobile to stream instantly</p>
    </header>
    <div class="grid">
        {cards_html}
    </div>
</body>
</html>
"""
    with open(public_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print(f"[+] Static web portal created at: public/index.html")

def main():
    parser = argparse.ArgumentParser(description="MovieBox Blogger Sync")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and generate HTML without sending")
    parser.add_argument("--max-posts", type=int, default=3, help="Max movies to post per run (default: 3)")
    args = parser.parse_args()

    secret_email = os.environ.get("BLOGGER_SECRET_EMAIL")
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASS")
    blog_id = os.environ.get("BLOGGER_BLOG_ID")
    access_token = os.environ.get("BLOGGER_ACCESS_TOKEN")

    published_ids = load_history()
    top_movies = fetch_top_movies(limit=25)

    if not top_movies:
        print("[!] No movies found.")
        return

    new_movies_processed = []
    count = 0

    for item in top_movies:
        if count >= args.max_posts:
            break

        imdb_id = item.get("imdb_id")
        if not imdb_id or imdb_id in published_ids:
            continue

        print(f"\n[>] Processing new movie: {item.get('name')} ({imdb_id})")
        details = fetch_movie_details(imdb_id)
        if not details:
            details = item

        title = details.get("name") or item.get("name")
        year = details.get("year") or details.get("releaseInfo") or ""
        genres = details.get("genres", ["Movie"])

        links = build_stream_links(imdb_id, title)
        html_card = generate_blogger_html(details, links)

        # Subject for email / post title
        # In Blogger email: #label1 #label2 at end creates labels/tags!
        label_tags = " ".join([f"#{g.replace(' ', '')}" for g in genres[:3]])
        subject = f"{title} ({year}) [1080p FHD] {label_tags}"

        if args.dry_run:
            print(f"[DRY-RUN] Subject: {subject}")
            print(f"[DRY-RUN] Card length: {len(html_card)} chars")
            published_ids.add(imdb_id)
            count += 1
            new_movies_processed.append({"movie": details, "links": links})
            continue

        # Publish via Email if configured
        published = False
        if secret_email and smtp_user and smtp_pass:
            published = send_blogger_email(subject, html_card, secret_email, smtp_user, smtp_pass)
        elif blog_id and access_token:
            published = post_blogger_api(f"{title} ({year}) [1080p FHD]", html_card, blog_id, access_token, genres[:3])
        else:
            print("[!] No publishing credentials found (BLOGGER_SECRET_EMAIL or BLOGGER_BLOG_ID).")
            print("[*] Generating local portal preview...")
            published = True

        if published:
            published_ids.add(imdb_id)
            count += 1
            new_movies_processed.append({"movie": details, "links": links})

    # Generate updated static web portal for GitHub Pages / preview
    all_known_movies = []
    for m in top_movies:
        links = build_stream_links(m.get("imdb_id", ""), m.get("name", ""))
        all_known_movies.append({"movie": m, "links": links})
    
    generate_static_portal(all_known_movies)

    if count > 0:
        save_history(published_ids)
        print(f"\n[OK] Finished: {count} new movie(s) processed.")
    else:
        print("\n[i] All catalog movies are already up-to-date. No new posts needed.")

if __name__ == "__main__":
    main()
