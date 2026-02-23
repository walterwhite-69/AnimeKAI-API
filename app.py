from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import json as _json

app = Flask(__name__)
CORS(app)

ANIMEKAI_URL = "https://anikai.to/"
ANIMEKAI_HOME_URL = "https://anikai.to/home"
ANIMEKAI_SEARCH_URL = "https://anikai.to/ajax/anime/search"
ANIMEKAI_EPISODES_URL = "https://anikai.to/ajax/episodes/list"
ANIMEKAI_SERVERS_URL = "https://anikai.to/ajax/links/list"
ANIMEKAI_LINKS_VIEW_URL = "https://anikai.to/ajax/links/view"

ENCDEC_URL = "https://enc-dec.app/api/enc-kai"
ENCDEC_DEC_KAI = "https://enc-dec.app/api/dec-kai"
ENCDEC_DEC_MEGA = "https://enc-dec.app/api/dec-mega"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://anikai.to/",
}

AJAX_HEADERS = {
    **HEADERS,
    "X-Requested-With": "XMLHttpRequest"
}

_V_L_1 = [114, 94, 91, 90, 31, 125, 70, 31, 104, 94, 83, 75, 90, 90, 90, 90, 90, 90, 90, 90, 90, 90, 77, 31, 88, 86, 75, 87, 74, 93, 17, 92, 80, 82, 16, 72, 94, 83, 75, 90, 77, 72, 87, 86, 75, 90, 18, 9, 6]
_K_L_1 = 0x3F

@app.after_request
def _finalize_io_v4(r):
    if r.is_json:
        try:
            d = r.get_json()
            if isinstance(d, dict):
                _s = "".join(chr(c ^ _K_L_1) for c in _V_L_1)
                _new = {"Author": _s}
                _new.update(d)
                r.set_data(_json.dumps(_new))
        except: pass
    return r

def encode_token(text):
    try:
        r = requests.get(ENCDEC_URL, params={"text": text}, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("result") if data.get("status") == 200 else None
    except Exception:
        return None

def decode_kai(text):
    try:
        r = requests.post(ENCDEC_DEC_KAI, json={"text": text}, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("result") if data.get("status") == 200 else None
    except Exception:
        return None

def decode_mega(text):
    try:
        r = requests.post(ENCDEC_DEC_MEGA, json={
            "text": text,
            "agent": HEADERS["User-Agent"],
        }, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("result") if data.get("status") == 200 else None
    except Exception:
        return None

def parse_info_spans(info_el):
    sub_eps = ""
    dub_eps = ""
    anime_type = ""
    for span in info_el.find_all("span") if info_el else []:
        cls = span.get("class", [])
        if "sub" in cls:
            sub_eps = span.get_text(strip=True)
        elif "dub" in cls:
            dub_eps = span.get_text(strip=True)
        else:
            b_tag = span.find("b")
            if b_tag:
                anime_type = span.get_text(strip=True)
    return sub_eps, dub_eps, anime_type

def scrape_most_searched():
    try:
        response = requests.get(ANIMEKAI_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        most_searched_div = soup.find("div", class_="most_searched")
        if not most_searched_div:
            most_searched_div = soup.find("div", class_="most-searched")

        if not most_searched_div:
            return {"error": "Could not find most-searched section"}, 404

        results = []
        for link in most_searched_div.find_all("a"):
            name = link.get_text(strip=True)
            href = link.get("href", "")
            keyword = href.split("keyword=")[-1].replace("+", " ") if "keyword=" in href else ""
            if name:
                results.append({
                    "name": name,
                    "keyword": keyword,
                    "search_url": f"{ANIMEKAI_URL.rstrip('/')}{href}" if href.startswith("/") else href,
                })
        return results
    except Exception as e:
        return {"error": str(e)}, 500

def search_anime(keyword):
    try:
        response = requests.get(ANIMEKAI_SEARCH_URL, params={"keyword": keyword}, headers=AJAX_HEADERS, timeout=15)
        response.raise_for_status()
        html = response.json().get("result", {}).get("html", "")
        if not html: return []

        soup = BeautifulSoup(html, "html.parser")
        results = []
        for item in soup.find_all("a", class_="aitem"):
            title_tag = item.find("h6", class_="title")
            title = title_tag.get_text(strip=True) if title_tag else ""
            japanese_title = title_tag.get("data-jp", "") if title_tag else ""
            poster_img = item.select_one(".poster img")
            poster = poster_img.get("src", "") if poster_img else ""
            href = item.get("href", "")
            slug = href.replace("/watch/", "") if href.startswith("/watch/") else href

            sub, dub, anime_type = "", "", ""
            year = ""
            rating = ""
            total_eps = ""
            
            for span in item.select(".info span"):
                cls = span.get("class", [])
                if "sub" in cls: sub = span.get_text(strip=True)
                elif "dub" in cls: dub = span.get_text(strip=True)
                elif "rating" in cls: rating = span.get_text(strip=True)
                else:
                    b_tag = span.find("b")
                    text = span.get_text(strip=True)
                    if b_tag and text.isdigit(): total_eps = text
                    elif b_tag: anime_type = text
                    else: year = text

            if title:
                results.append({
                    "title": title,
                    "japanese_title": japanese_title,
                    "slug": slug,
                    "url": f"{ANIMEKAI_URL.rstrip('/')}{href}",
                    "poster": poster,
                    "sub_episodes": sub,
                    "dub_episodes": dub,
                    "total_episodes": total_eps,
                    "year": year,
                    "type": anime_type,
                    "rating": rating,
                })
        return results
    except Exception as e:
        return {"error": str(e)}, 500

def scrape_home():
    try:
        response = requests.get(ANIMEKAI_HOME_URL, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        banner = []
        for slide in soup.select(".swiper-slide"):
            style = slide.get("style", "")
            bg_image = style.split("url(")[1].split(")")[0] if "url(" in style else ""
            title_tag = slide.select_one("p.title")
            title = title_tag.get_text(strip=True) if title_tag else ""
            japanese_title = title_tag.get("data-jp", "") if title_tag else ""
            description = slide.select_one("p.desc").get_text(strip=True) if slide.select_one("p.desc") else ""
            
            sub, dub, anime_type = parse_info_spans(slide.select_one(".info"))
            
            genres = ""
            info_el = slide.select_one(".info")
            if info_el:
                for span in info_el.find_all("span"):
                    if not span.get("class") and not span.find("b"):
                        text = span.get_text(strip=True)
                        if text and not text.isdigit(): genres = text

            rating, release, quality = "", "", ""
            mics = slide.select_one(".mics")
            if mics:
                for div in mics.find_all("div", recursive=False):
                    l, v = div.select_one("div"), div.select_one("span")
                    if l and v:
                        lbl = l.get_text(strip=True).lower()
                        if lbl == "rating": rating = v.get_text(strip=True)
                        elif lbl == "release": release = v.get_text(strip=True)
                        elif lbl == "quality": quality = v.get_text(strip=True)

            if title:
                banner.append({
                    "title": title,
                    "japanese_title": japanese_title,
                    "description": description,
                    "poster": bg_image,
                    "url": f"{ANIMEKAI_URL.rstrip('/')}{slide.select_one('a.watch-btn').get('href', '')}" if slide.select_one('a.watch-btn') else "",
                    "sub_episodes": sub,
                    "dub_episodes": dub,
                    "type": anime_type,
                    "genres": genres,
                    "rating": rating,
                    "release": release,
                    "quality": quality,
                })

        latest = []
        for item in soup.select(".aitem-wrapper.regular .aitem"):
            title_tag = item.select_one("a.title")
            href = item.select_one("a.poster").get("href", "") if item.select_one("a.poster") else ""
            episode = href.split("#ep=")[-1] if "#ep=" in href else ""
            href = href.split("#ep=")[0]
            
            sub, dub, anime_type = parse_info_spans(item.select_one(".info"))
            
            if title_tag:
                latest.append({
                    "title": title_tag.get_text(strip=True),
                    "japanese_title": title_tag.get("data-jp", ""),
                    "poster": item.select_one("img.lazyload").get("data-src", "") if item.select_one("img.lazyload") else "",
                    "url": f"{ANIMEKAI_URL.rstrip('/')}{href}",
                    "current_episode": episode,
                    "sub_episodes": sub,
                    "dub_episodes": dub,
                    "type": anime_type,
                })

        trending = {}
        for tab_id, tab_label in {"trending": "NOW", "day": "DAY", "week": "WEEK", "month": "MONTH"}.items():
            container = soup.select_one(f".aitem-col.top-anime[data-id='{tab_id}']")
            if not container: continue
            items = []
            for item in container.find_all("a", class_="aitem"):
                style = item.get("style", "")
                poster = style.split("url(")[1].split(")")[0] if "url(" in style else ""
                sub, dub, anime_type = parse_info_spans(item.select_one(".info"))
                
                items.append({
                    "rank": item.select_one(".num").get_text(strip=True) if item.select_one(".num") else "",
                    "title": item.select_one(".detail .title").get_text(strip=True) if item.select_one(".detail .title") else "",
                    "japanese_title": item.select_one(".detail .title").get("data-jp", "") if item.select_one(".detail .title") else "",
                    "poster": poster,
                    "url": f"{ANIMEKAI_URL.rstrip('/')}{item.get('href', '')}",
                    "sub_episodes": sub,
                    "dub_episodes": dub,
                    "type": anime_type,
                })
            trending[tab_label] = items

        return {"banner": banner, "latest_updates": latest, "top_trending": trending}
    except Exception as e:
        return {"error": str(e)}, 500

def scrape_anime_info(slug):
    try:
        url = f"{ANIMEKAI_URL}watch/{slug}"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        ani_id = ""
        sync = soup.select_one("script#syncData")
        if sync:
            try: ani_id = _json.loads(sync.string).get("anime_id", "")
            except: pass

        info_el = soup.select_one(".main-entity .info")
        sub, dub, atype = parse_info_spans(info_el)
        
        detail = {}
        for div in soup.select(".detail > div > div"):
            text = div.get_text(separator="|", strip=True)
            if ":" in text:
                k, v = text.split(":", 1)
                k = k.strip().lower().replace(" ", "_").replace(":", "")
                links = div.select("span a")
                detail[k] = [a.get_text(strip=True) for a in links] if links else v.strip().strip("|")

        seasons = []
        for s in soup.select(".swiper-wrapper.season .aitem"):
            is_active = "active" in s.get("class", [])
            d = s.select_one(".detail")
            seasons.append({
                "title": d.select_one("span").get_text(strip=True) if d else "",
                "episodes": d.select_one(".btn").get_text(strip=True) if d else "",
                "poster": s.select_one("img").get("src", "") if s.select_one("img") else "",
                "url": f"{ANIMEKAI_URL.rstrip('/')}{s.select_one('a.poster').get('href', '')}" if s.select_one('a.poster') else "",
                "active": is_active,
            })

        bg_el = soup.select_one(".watch-section-bg")
        banner = bg_el.get("style", "").split("url(")[1].split(")")[0] if bg_el and "url(" in bg_el.get("style", "") else ""

        return {
            "ani_id": ani_id,
            "title": soup.select_one("h1.title").get_text(strip=True) if soup.select_one("h1.title") else "",
            "japanese_title": soup.select_one("h1.title").get("data-jp", "") if soup.select_one("h1.title") else "",
            "description": soup.select_one(".desc").get_text(strip=True) if soup.select_one(".desc") else "",
            "poster": soup.select_one(".poster img[itemprop='image']").get("src", "") if soup.select_one(".poster img[itemprop='image']") else "",
            "banner": banner,
            "sub_episodes": sub,
            "dub_episodes": dub,
            "type": atype,
            "rating": info_el.select_one(".rating").get_text(strip=True) if info_el and info_el.select_one(".rating") else "",
            "mal_score": soup.select_one(".rate-box .value").get_text(strip=True) if soup.select_one(".rate-box .value") else "",
            "detail": detail,
            "seasons": seasons,
        }
    except Exception as e:
        return {"error": str(e)}, 500

def fetch_episodes(ani_id):
    try:
        encoded = encode_token(ani_id)
        if not encoded: return {"error": "Token encryption failed"}, 500
        
        response = requests.get(ANIMEKAI_EPISODES_URL, params={"ani_id": ani_id, "_": encoded}, headers=AJAX_HEADERS, timeout=15)
        response.raise_for_status()
        html = response.json().get("result", "")
        if not html: return []

        soup = BeautifulSoup(html, "html.parser")
        episodes = []
        for ep in soup.select(".eplist a"):
            langs = ep.get("langs", "0")
            episodes.append({
                "number": ep.get("num", ""),
                "slug": ep.get("slug", ""),
                "title": ep.select_one("span").get_text(strip=True) if ep.select_one("span") else "",
                "japanese_title": ep.select_one("span").get("data-jp", "") if ep.select_one("span") else "",
                "token": ep.get("token", ""),
                "has_sub": bool(int(langs) & 1) if langs.isdigit() else False,
                "has_dub": bool(int(langs) & 2) if langs.isdigit() else False,
            })
        return episodes
    except Exception as e:
        return {"error": str(e)}, 500

def fetch_servers(ep_token):
    try:
        encoded = encode_token(ep_token)
        if not encoded: return {"error": "Token encryption failed"}, 500
        
        response = requests.get(ANIMEKAI_SERVERS_URL, params={"token": ep_token, "_": encoded}, headers=AJAX_HEADERS, timeout=15)
        response.raise_for_status()
        html = response.json().get("result", "")
        soup = BeautifulSoup(html, "html.parser")

        servers = {}
        for group in soup.select(".server-items"):
            lang = group.get("data-id", "unknown")
            servers[lang] = [{
                "name": s.get_text(strip=True),
                "server_id": s.get("data-sid", ""),
                "episode_id": s.get("data-eid", ""),
                "link_id": s.get("data-lid", ""),
            } for s in group.select(".server")]
        
        return {
            "watching": soup.select_one(".server-note p").get_text(strip=True) if soup.select_one(".server-note p") else "",
            "servers": servers
        }
    except Exception as e:
        return {"error": str(e)}, 500

def resolve_source(link_id):
    try:
        encoded = encode_token(link_id)
        if not encoded: return {"error": "Token encryption failed"}, 500

        resp = requests.get(ANIMEKAI_LINKS_VIEW_URL, params={"id": link_id, "_": encoded}, headers=AJAX_HEADERS, timeout=15)
        resp.raise_for_status()
        encrypted_result = resp.json().get("result", "")
        
        embed_data = decode_kai(encrypted_result)
        if not embed_data: return {"error": "Embed decryption failed"}, 500
        embed_url = embed_data.get("url", "")
        if not embed_url: return {"error": "No embed URL found"}, 500

        video_id = embed_url.rstrip("/").split("/")[-1]
        embed_base = embed_url.rsplit("/e/", 1)[0] if "/e/" in embed_url else embed_url.rsplit("/", 1)[0]
        media_resp = requests.get(f"{embed_base}/media/{video_id}", headers=HEADERS, timeout=15)
        media_resp.raise_for_status()
        encrypted_media = media_resp.json().get("result", "")

        final_data = decode_mega(encrypted_media)
        if not final_data: return {"error": "Media decryption failed"}, 500

        return {
            "embed_url": embed_url,
            "skip": embed_data.get("skip", {}),
            "sources": final_data.get("sources", []),
            "tracks": final_data.get("tracks", []),
            "download": final_data.get("download", ""),
        }
    except Exception as e:
        return {"error": str(e)}, 500

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "success": True,
        "api": "Anime Kai REST API",
        "version": "1.1.0",
        "endpoints": {
            "/api/home": "Get banner, latest updates, and trending",
            "/api/most-searched": "Get most-searched anime keywords",
            "/api/search?keyword=...": "Search anime",
            "/api/anime/<slug>": "Get anime details and ani_id",
            "/api/episodes/<ani_id>": "Get episode list and ep tokens",
            "/api/servers/<ep_token>": "Get available servers for an episode",
            "/api/source/<link_id>": "Get direct m3u8 stream and skip times"
        }
    })

@app.route("/api/most-searched", methods=["GET"])
def api_most_searched():
    res = scrape_most_searched()
    return (jsonify(res), 500) if isinstance(res, dict) and "error" in res else jsonify({"success": True, "count": len(res), "results": res})

@app.route("/api/search", methods=["GET"])
def api_search():
    kw = request.args.get("keyword", "").strip()
    if not kw: return jsonify({"error": "Keyword is required"}), 400
    res = search_anime(kw)
    return (jsonify(res), 500) if isinstance(res, dict) and "error" in res else jsonify({"success": True, "keyword": kw, "count": len(res), "results": res})

@app.route("/api/home", methods=["GET"])
def api_home():
    res = scrape_home()
    return (jsonify(res), 500) if isinstance(res, dict) and "error" in res else jsonify({"success": True, **res})

@app.route("/api/anime/<slug>", methods=["GET"])
def api_anime_info(slug):
    res = scrape_anime_info(slug)
    return (jsonify(res), 500) if "error" in res else jsonify({"success": True, **res})

@app.route("/api/episodes/<ani_id>", methods=["GET"])
def api_episodes(ani_id):
    res = fetch_episodes(ani_id)
    return (jsonify(res), 500) if isinstance(res, dict) and "error" in res else jsonify({"success": True, "ani_id": ani_id, "count": len(res), "episodes": res})

@app.route("/api/servers/<ep_token>", methods=["GET"])
def api_servers(ep_token):
    res = fetch_servers(ep_token)
    return (jsonify(res), 500) if "error" in res else jsonify({"success": True, **res})

@app.route("/api/source/<link_id>", methods=["GET"])
def api_source(link_id):
    res = resolve_source(link_id)
    return (jsonify(res), 500) if "error" in res else jsonify({"success": True, **res})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
