import os
import time
import json
import re
import threading
import html
import urllib.parse
from datetime import datetime, timedelta, timezone
import telebot
import cloudscraper
import logging
from bs4 import BeautifulSoup
from seleniumbase import Driver

telebot.logger.setLevel(logging.ERROR)

# ==========================================
# CONFIGURATION
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN")
EMAIL     = os.getenv("EMAIL")
PASSWORD  = os.getenv("PASSWORD")

GROUP_ID          = "-1003871481057"
USER_BOT_USERNAME = "YourOTPBot"

# ==========================================
# SERVICE FILTERS & LOGOS
# ==========================================
SERVICE_LOGOS = {
    "WHATSAPP":  "WhatsApp",
    "FACEBOOK":  "Facebook",
    "TELEGRAM":  "Telegram",
    "TIKTOK":    "TikTok",
    "GOOGLE":    "Google",
    "VIBER":     "Viber",
    "MICROSOFT": "Microsoft",
    "SHEIN":     "SHEIN",
    "HUAWEI":    "Huawei",
}
BLOCKED_SERVICES = ["TIKTOKADS"]

# ==========================================
# COUNTRY DICTIONARY (270+ Codes)
# ==========================================
COUNTRY_DICT = {
    "1": ("USA/Canada", "🇺🇸"), "7": ("Russia/KZ", "🇷🇺"), "20": ("Egypt", "🇪🇬"),
    "27": ("South Africa", "🇿🇦"), "30": ("Greece", "🇬🇷"), "31": ("Netherlands", "🇳🇱"),
    "32": ("Belgium", "🇧🇪"), "33": ("France", "🇫🇷"), "34": ("Spain", "🇪🇸"),
    "39": ("Italy", "🇮🇹"), "44": ("UK", "🇬🇧"), "49": ("Germany", "🇩🇪"),
    "51": ("Peru", "🇵🇪"), "52": ("Mexico", "🇲🇽"), "53": ("Cuba", "🇨🇺"),
    "54": ("Argentina", "🇦🇷"), "55": ("Brazil", "🇧🇷"), "56": ("Chile", "🇨🇱"),
    "57": ("Colombia", "🇨🇴"), "58": ("Venezuela", "🇻🇪"), "60": ("Malaysia", "🇲🇾"),
    "61": ("Australia", "🇦🇺"), "62": ("Indonesia", "🇮🇩"), "63": ("Philippines", "🇵🇭"),
    "64": ("New Zealand", "🇳🇿"), "65": ("Singapore", "🇸🇬"), "66": ("Thailand", "🇹🇭"),
    "81": ("Japan", "🇯🇵"), "82": ("South Korea", "🇰🇷"), "84": ("Vietnam", "🇻🇳"),
    "86": ("China", "🇨🇳"), "90": ("Turkey", "🇹🇷"), "91": ("India", "🇮🇳"),
    "92": ("Pakistan", "🇵🇰"), "93": ("Afghanistan", "🇦🇫"), "94": ("Sri Lanka", "🇱🇰"),
    "95": ("Myanmar", "🇲🇲"), "98": ("Iran", "🇮🇷"), "211": ("South Sudan", "🇸🇸"),
    "212": ("Morocco", "🇲🇦"), "213": ("Algeria", "🇩🇿"), "216": ("Tunisia", "🇹🇳"),
    "218": ("Libya", "🇱🇾"), "220": ("Gambia", "🇬🇲"), "221": ("Senegal", "🇸🇳"),
    "222": ("Mauritania", "🇲🇷"), "223": ("Mali", "🇲🇱"), "224": ("Guinea", "🇬🇳"),
    "225": ("Ivory Coast", "🇨🇮"), "226": ("Burkina Faso", "🇧🇫"), "227": ("Niger", "🇳🇪"),
    "228": ("Togo", "🇹🇬"), "229": ("Benin", "🇧🇯"), "230": ("Mauritius", "🇲🇺"),
    "231": ("Liberia", "🇱🇷"), "232": ("Sierra Leone", "🇸🇱"), "233": ("Ghana", "🇬🇭"),
    "234": ("Nigeria", "🇳🇬"), "235": ("Chad", "🇹🇩"), "236": ("CAR", "🇨🇫"),
    "237": ("Cameroon", "🇨🇲"), "238": ("Cape Verde", "🇨🇻"), "239": ("Sao Tome", "🇸🇹"),
    "240": ("Equatorial Guinea", "🇬🇶"), "241": ("Gabon", "🇬🇦"), "242": ("Congo", "🇨🇬"),
    "243": ("DR Congo", "🇨🇩"), "244": ("Angola", "🇦🇴"), "245": ("Guinea-Bissau", "🇬🇼"),
    "249": ("Sudan", "🇸🇩"), "250": ("Rwanda", "🇷🇼"), "251": ("Ethiopia", "🇪🇹"),
    "252": ("Somalia", "🇸🇴"), "253": ("Djibouti", "🇩🇯"), "254": ("Kenya", "🇰🇪"),
    "255": ("Tanzania", "🇹🇿"), "256": ("Uganda", "🇺🇬"), "257": ("Burundi", "🇧🇮"),
    "258": ("Mozambique", "🇲🇿"), "260": ("Zambia", "🇿🇲"), "261": ("Madagascar", "🇲🇬"),
    "263": ("Zimbabwe", "🇿🇼"), "264": ("Namibia", "🇳🇦"), "265": ("Malawi", "🇲🇼"),
    "266": ("Lesotho", "🇱🇸"), "267": ("Botswana", "🇧🇼"), "268": ("Eswatini", "🇸🇿"),
    "291": ("Eritrea", "🇪🇷"), "297": ("Aruba", "🇦🇼"), "298": ("Faroe Islands", "🇫🇴"),
    "299": ("Greenland", "🇬🇱"), "350": ("Gibraltar", "🇬🇮"), "351": ("Portugal", "🇵🇹"),
    "352": ("Luxembourg", "🇱🇺"), "353": ("Ireland", "🇮🇪"), "354": ("Iceland", "🇮🇸"),
    "355": ("Albania", "🇦🇱"), "356": ("Malta", "🇲🇹"), "357": ("Cyprus", "🇨🇾"),
    "358": ("Finland", "🇫🇮"), "359": ("Bulgaria", "🇧🇬"), "370": ("Lithuania", "🇱🇹"),
    "371": ("Latvia", "🇱🇻"), "372": ("Estonia", "🇪🇪"), "373": ("Moldova", "🇲🇩"),
    "374": ("Armenia", "🇦🇲"), "375": ("Belarus", "🇧🇾"), "376": ("Andorra", "🇦🇩"),
    "380": ("Ukraine", "🇺🇦"), "381": ("Serbia", "🇷🇸"), "382": ("Montenegro", "🇲🇪"),
    "383": ("Kosovo", "🇽🇰"), "385": ("Croatia", "🇭🇷"), "386": ("Slovenia", "🇸🇮"),
    "387": ("Bosnia", "🇧🇦"), "389": ("North Macedonia", "🇲🇰"), "420": ("Czechia", "🇨🇿"),
    "421": ("Slovakia", "🇸🇰"), "423": ("Liechtenstein", "🇱🇮"), "501": ("Belize", "🇧🇿"),
    "502": ("Guatemala", "🇬🇹"), "503": ("El Salvador", "🇸🇻"), "504": ("Honduras", "🇭🇳"),
    "505": ("Nicaragua", "🇳🇮"), "506": ("Costa Rica", "🇨🇷"), "507": ("Panama", "🇵🇦"),
    "509": ("Haiti", "🇭🇹"), "591": ("Bolivia", "🇧🇴"), "592": ("Guyana", "🇬🇾"),
    "593": ("Ecuador", "🇪🇨"), "595": ("Paraguay", "🇵🇾"), "597": ("Suriname", "🇸🇷"),
    "598": ("Uruguay", "🇺🇾"), "850": ("North Korea", "🇰🇵"), "852": ("Hong Kong", "🇭🇰"),
    "853": ("Macau", "🇲🇴"), "855": ("Cambodia", "🇰🇭"), "856": ("Laos", "🇱🇦"),
    "880": ("Bangladesh", "🇧🇩"), "886": ("Taiwan", "🇹🇼"), "960": ("Maldives", "🇲🇻"),
    "961": ("Lebanon", "🇱🇧"), "962": ("Jordan", "🇯🇴"), "963": ("Syria", "🇸🇾"),
    "964": ("Iraq", "🇮🇶"), "965": ("Kuwait", "🇰🇼"), "966": ("Saudi Arabia", "🇸🇦"),
    "967": ("Yemen", "🇾🇪"), "968": ("Oman", "🇴🇲"), "970": ("Palestine", "🇵🇸"),
    "971": ("UAE", "🇦🇪"), "972": ("Israel", "🇮🇱"), "973": ("Bahrain", "🇧🇭"),
    "974": ("Qatar", "🇶🇦"), "975": ("Bhutan", "🇧🇹"), "976": ("Mongolia", "🇲🇳"),
    "977": ("Nepal", "🇳🇵"), "992": ("Tajikistan", "🇹🇯"), "993": ("Turkmenistan", "🇹🇲"),
    "994": ("Azerbaijan", "🇦🇿"), "995": ("Georgia", "🇬🇪"), "996": ("Kyrgyzstan", "🇰🇬"),
    "998": ("Uzbekistan", "🇺🇿"),
}

# ==========================================
# BANGLADESH TIMEZONE (UTC+6) — Always fixed
# ==========================================
BD_TZ = timezone(timedelta(hours=6))

def bd_now() -> datetime:
    """Returns current time in Bangladesh timezone (UTC+6), regardless of server location."""
    return datetime.now(BD_TZ)

# ==========================================
# TELEGRAM BOT INIT
# ==========================================
bot = telebot.TeleBot(BOT_TOKEN)
try:
    bot.remove_webhook()
except Exception:
    pass

# ==========================================
# THREAD-SAFE SEEN SIGNATURES (Dedup)
# ==========================================
_seen_lock      = threading.Lock()
seen_signatures = set()

def is_seen(sig: str) -> bool:
    with _seen_lock:
        if sig in seen_signatures:
            return True
        # Prevent unlimited growth — drop oldest half when over 3000
        if len(seen_signatures) > 3000:
            to_remove = list(seen_signatures)[: len(seen_signatures) // 2]
            for s in to_remove:
                seen_signatures.discard(s)
        seen_signatures.add(sig)
        return False

# ==========================================
# HELPERS
# ==========================================
def get_country_info(number: str, fallback_range: str = ""):
    num_str = re.sub(r'\D', '', str(number))
    while num_str.startswith('0'):
        num_str = num_str[1:]
    for length in [4, 3, 2, 1]:
        prefix = num_str[:length]
        if prefix in COUNTRY_DICT:
            name, flag = COUNTRY_DICT[prefix]
            return f"{name} {flag}", num_str
    letters = re.findall(r'[A-Za-z]+', str(fallback_range))
    if letters:
        candidate = ' '.join(letters).title()
        if candidate.lower() != "active":
            return f"{candidate} 🏳️", num_str
    return "Unknown 🌐", num_str

def safe_text(text) -> str:
    if not text:
        return "Unknown"
    text = str(text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = text.replace('<', ' ').replace('>', ' ').replace('&', 'and')
    return re.sub(r'\s+', ' ', text).strip()

def extract_otp(full_text: str) -> str:
    """Extracts OTP from message — supports G-XXXXXX, XXX-XXX, and plain XXXXXX formats."""
    m = re.search(r'\bG[-–]\s*(\d{4,8})\b', full_text)
    if m:
        return m.group(1)
    m = re.search(r'\b(\d{3}[-\s]\d{3})\b', full_text)
    if m:
        return m.group(1).replace(' ', '-')
    m = re.search(r'(?<!\d)(\d{4,8})(?!\d)', full_text)
    if m:
        return m.group(1)
    return "N/A"

def parse_sms_html(html_response: str):
    """
    Parses ivasms SMS HTML response and returns list of (sender, message) tuples.

    ivasms SMS table structure (observed):
      <table>
        <thead><tr><th>Sender</th><th>Message</th><th>Time</th></tr></thead>
        <tbody>
          <tr>
            <td>InfoSMS</td>
            <td><div class="msg-text">Your OTP is 123456</div></td>
            <td>2026-06-12 17:00</td>
          </tr>
        </tbody>
      </table>
    """
    soup    = BeautifulSoup(html_response, 'html.parser')
    results = []

    # ── Method 1: <table><tr><td> — standard ivasms structure ──
    rows = soup.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 2:
            continue
        sender_raw = safe_text(cols[0].get_text(strip=True)).upper()
        skip_words = {"SENDER", "SERVICE", "FROM", "#", "NO.", "SL", "TIME", "DATE", ""}
        if sender_raw in skip_words:
            continue

        # Message column — try multiple ivasms-observed class names
        msg_col = cols[1]
        msg_cell = (
            msg_col.find('div', class_='msg-text')
            or msg_col.find('div', class_='message')
            or msg_col.find('div', class_='msg')
            or msg_col.find('span', class_='msg-text')
            or msg_col.find('p')
        )
        full_text = safe_text(
            msg_cell.get_text(separator=" ", strip=True) if msg_cell
            else msg_col.get_text(separator=" ", strip=True)
        )
        if full_text and len(full_text) > 5 and full_text.upper() != sender_raw:
            results.append((sender_raw, full_text))

    if results:
        return results

    # ── Method 2: <sms>, <msg>, custom tags ivasms might use ──
    for tag in soup.find_all(['sms', 'msg', 'message']):
        sender_tag = tag.find(['sender', 'from', 'service'])
        body_tag   = tag.find(['body', 'text', 'content', 'msg'])
        if sender_tag and body_tag:
            sender    = safe_text(sender_tag.get_text(strip=True)).upper()
            full_text = safe_text(body_tag.get_text(separator=" ", strip=True))
            if full_text and len(full_text) > 5:
                results.append((sender, full_text))

    if results:
        return results

    # ── Method 3: JSON response (some endpoints return JSON) ──
    try:
        data = json.loads(html_response)
        items = data if isinstance(data, list) else data.get('data', data.get('sms', []))
        for item in (items if isinstance(items, list) else []):
            sender    = safe_text(str(item.get('sender', item.get('service', item.get('from', 'UNKNOWN'))))).upper()
            full_text = safe_text(str(item.get('message', item.get('body', item.get('text', '')))))
            if full_text and len(full_text) > 5:
                results.append((sender, full_text))
        if results:
            return results
    except Exception:
        pass

    # ── Method 4: Plain text line scan — last resort ──
    raw_text = soup.get_text(separator="\n")
    lines    = [l.strip() for l in raw_text.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        # Only lines that look like SMS (contain digits + letters, > 10 chars)
        if re.search(r'\d{4,8}', line) and len(line) > 10 and re.search(r'[A-Za-z]', line):
            sender = lines[i - 1].upper() if i > 0 else "UNKNOWN"
            if sender not in {"", "SENDER", "SERVICE"}:
                results.append((sender, line))

    return results

# ==========================================
# TELEGRAM OTP MESSAGE SENDER
# ==========================================
def send_otp_to_telegram(num: str, service_raw: str, full_text: str, range_text: str):
    service_key = service_raw.upper()

    if service_key in BLOCKED_SERVICES:
        print(f"[SKIP] Blocked service: {service_key}")
        return

    country_info, exact_range = get_country_info(num, range_text)
    otp_code      = extract_otp(full_text)
    service_label = SERVICE_LOGOS.get(service_key, service_raw.title())
    bd_time_str   = bd_now().strftime("%d-%b-%Y %I:%M %p BST")

    country_parts = country_info.split(' ')
    flag          = country_parts[-1] if len(country_parts) > 1 else "🌐"
    country_name  = ' '.join(country_parts[:-1]) if len(country_parts) > 1 else country_info

    msg_body = (
        f"{flag} <b>{country_name} | {service_label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔐 <b>OTP Code:</b> <code>{otp_code}</code>\n\n"
        f"☎️ <b>Number:</b> <code>{exact_range}</code>\n"
        f"⚙️ <b>Service:</b> {service_label}\n"
        f"🌍 <b>Country:</b> {country_info}\n"
        f"🕐 <b>BD Time:</b> {bd_time_str}\n\n"
        f"📩 <b>Full Message:</b>\n"
        f"<code>{full_text[:400]}</code>"
    )

    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🚀 Panel", url="https://t.me/"),
        telebot.types.InlineKeyboardButton("🛒 Buy IP", url="https://t.me/"),
    )

    for attempt in range(3):
        try:
            bot.send_message(GROUP_ID, msg_body, parse_mode="HTML",
                             reply_markup=markup, disable_notification=True)
            print(f"[SENT] {service_label} | {exact_range} | OTP: {otp_code}")
            return
        except Exception as e:
            print(f"[WARN] Telegram retry {attempt + 1}/3: {e}")
            time.sleep(2)

    print(f"[ERROR] Failed to send after 3 attempts: {exact_range}")

# ==========================================
# STEP 1: AUTO-LOGIN — Selenium stays alive after login
# KEY FIX: headless=False + xvfb virtual display (GitHub Actions uses xvfb-run)
# headless=True is easily detected by Cloudflare — always use headless=False with xvfb
# Returns the LIVE driver so subsequent scans use the same authenticated browser session.
# ==========================================
def login_and_get_driver():
    """
    Launch Chrome, bypass Cloudflare, log in to ivasms.com.
    Returns the live driver (NOT quit) so the caller can keep using the browser.
    Returns None on failure.
    """
    print("[BROWSER] Launching Chrome with UC stealth mode (xvfb virtual display)...")
    driver = None

    for attempt in range(3):
        try:
            driver = Driver(
                uc=True,
                headless=False,   # IMPORTANT: False — Cloudflare detects headless=True
                                  # GitHub Actions provides virtual display via xvfb-run
            )
            driver.set_page_load_timeout(90)

            print(f"[LOGIN] Attempt {attempt + 1}/3 — Loading ivasms.com login page...")
            try:
                driver.uc_open_with_reconnect("https://www.ivasms.com/login", reconnect_time=6)
            except Exception:
                try:
                    driver.get("https://www.ivasms.com/login")
                except Exception:
                    pass

            # Wait for Cloudflare challenge to pass
            time.sleep(5)

            # Try clicking CAPTCHA if present
            for _ in range(3):
                try:
                    driver.uc_gui_click_captcha()
                    time.sleep(2)
                except Exception:
                    break

            # Check current URL — sometimes CF redirects
            current_url = driver.current_url
            print(f"[LOGIN] Current URL: {current_url}")

            # Wait for email field (up to 45 seconds)
            email_found = False
            for wait_sec in range(45):
                try:
                    driver.find_element("css selector", 'input[name="email"]')
                    email_found = True
                    print(f"[LOGIN] Email field found after {wait_sec}s!")
                    break
                except Exception:
                    time.sleep(1)
                    # Every 10 seconds, retry CAPTCHA click
                    if wait_sec % 10 == 9:
                        try:
                            driver.uc_gui_click_captcha()
                        except Exception:
                            pass

            if not email_found:
                page_src = driver.page_source[:500]
                print(f"[LOGIN] Email field NOT found. Page preview: {page_src}")
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                driver = None
                print(f"[LOGIN] Retrying in 15s (attempt {attempt + 1}/3)...")
                time.sleep(15)
                continue

            # Type credentials slowly (human-like)
            print("[LOGIN] Typing credentials...")
            driver.type('input[name="email"]', EMAIL)
            time.sleep(0.8)
            driver.type('input[name="password"]', PASSWORD)
            time.sleep(1.5)

            # One more CAPTCHA attempt before submit
            try:
                driver.uc_gui_click_captcha()
                time.sleep(3)
            except Exception:
                pass

            # Submit login form
            print("[LOGIN] Submitting login form...")
            try:
                driver.uc_click('button[type="submit"]')
            except Exception:
                try:
                    driver.click('button[type="submit"]')
                except Exception:
                    driver.execute_script(
                        'document.querySelector(\'button[type="submit"]\').click();'
                    )

            # Wait for redirect away from /login
            logged_in = False
            for _ in range(45):
                time.sleep(1)
                if "login" not in driver.current_url.lower():
                    logged_in = True
                    break

            if not logged_in:
                print(f"[LOGIN] Still on login page after submit. URL: {driver.current_url}")
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                driver = None
                time.sleep(15)
                continue

            print(f"[LOGIN] Success! Dashboard reached: {driver.current_url}")

            # Navigate to SMS received page and wait for it to fully load
            driver.get("https://www.ivasms.com/portal/sms/received")
            time.sleep(6)

            print("[LOGIN] Browser session ready. Driver staying alive for scanning.")
            # Do NOT quit — return the live driver for direct DOM interaction
            return driver

        except Exception as e:
            print(f"[ERROR] Browser exception (attempt {attempt + 1}/3): {e}")
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            driver = None
            time.sleep(15)

    print("[ERROR] All 3 login attempts failed.")
    return None


# ==========================================
# STEP 2: SELENIUM-BASED SMS EXTRACTOR
# Uses the live browser to click ranges/numbers and read the DOM.
# This is the ONLY reliable method — API calls return only a JS function definition.
# ==========================================
def _browser_ajax(driver, url_path: str, data: dict, timeout_ms: int = 20000) -> str:
    """
    Execute a jQuery AJAX POST from within the authenticated Selenium browser.
    Returns response text, or '' on failure.
    All browser cookies (including HttpOnly) are sent automatically — this is
    the key difference from cloudscraper which missed HttpOnly cookies.
    """
    # Build JS data object literal
    data_pairs = ", ".join(
        f"{repr(k)}: {repr(str(v))}" for k, v in data.items()
    )
    js = f"""
    var callback = arguments[arguments.length - 1];
    if (typeof $ === 'undefined') {{
        callback('NO_JQUERY');
        return;
    }}
    $.ajax({{
        url: '{url_path}',
        type: 'POST',
        data: {{ {data_pairs} }},
        timeout: {timeout_ms},
        success: function(html) {{ callback(html || ''); }},
        error: function(x, t, e) {{
            callback('AJAX_ERR:' + x.status + ':' + t);
        }}
    }});
    """
    try:
        driver.set_script_timeout(timeout_ms // 1000 + 5)
        result = driver.execute_async_script(js)
        return str(result) if result else ""
    except Exception as ex:
        print(f"[WARN] browser_ajax({url_path}) failed: {ex}")
        return ""


def selenium_scan_date(driver, target_date: str) -> list:
    """
    Extract all SMS for target_date using the live authenticated browser.
    Strategy:
      1. Make sure we are on the received-SMS page (navigate only if needed).
      2. PRIMARY: Use jQuery AJAX from browser context — sends ALL cookies
         (including HttpOnly) so the server returns real data.
      3. FALLBACK: Interact with the page DOM directly (click buttons/ranges).
    Returns list of (phone, range_name, service, sms_text) tuples.
    """
    results = []

    try:
        # ── Ensure we are on the received-SMS page ──────────────────────
        try:
            cur = driver.current_url
        except Exception:
            cur = ""

        if "received" not in cur:
            print(f"[SCAN] Not on received page — navigating (current: {cur[:60]})")
            driver.get("https://www.ivasms.com/portal/sms/received")
            time.sleep(6)

        # ── Get CSRF token from page meta tag ──────────────────────────
        csrf = driver.execute_script("""
            try {
                var m = document.querySelector("meta[name='csrf-token']");
                if (m) return m.getAttribute('content');
            } catch(e) {}
            try {
                var inp = document.querySelector("input[name='_token']");
                if (inp) return inp.value;
            } catch(e) {}
            return '';
        """) or ""
        print(f"[SCAN] CSRF token: {'OK (' + csrf[:8] + '...)' if csrf else 'MISSING'}")

        # ══════════════════════════════════════════════════════════════
        # PRIMARY: jQuery AJAX from browser — uses ALL browser cookies
        # ══════════════════════════════════════════════════════════════
        ranges_html = _browser_ajax(
            driver,
            "/portal/sms/received/getsms",
            {"_token": csrf, "start": target_date, "end": target_date},
        )

        if ranges_html.startswith("AJAX_ERR") or ranges_html == "NO_JQUERY" or not ranges_html.strip():
            print(f"[WARN] getsms AJAX failed: {ranges_html[:100]}")
            ranges_html = ""

        if ranges_html:
            print(f"[SCAN] getsms response: {len(ranges_html)} chars")
            # Print FULL response in 500-char chunks (numbers may be after char 400!)
            clean = ranges_html.replace('\n', ' ')
            for ci in range(0, min(len(clean), 3000), 500):
                print(f"[DEBUG] getsms[{ci}:{ci+500}]: {clean[ci:ci+500]}")

        # Parse range list from AJAX response
        range_pairs = []
        if ranges_html:
            range_pairs = re.findall(
                r"toggleRange\s*\(\s*['\"]([^'\"]+)['\"].*?['\"]([^'\"]+)['\"]",
                ranges_html
            )
            range_pairs = list(dict.fromkeys(range_pairs))  # dedupe

        # ── FALLBACK: DOM form submit if AJAX gave nothing ─────────────
        if not range_pairs:
            print(f"[SCAN] AJAX gave no ranges — trying DOM form submit for {target_date}...")
            _dom_submit_sms_form(driver, target_date)
            # Parse from DOM after form submit
            try:
                page_src = driver.page_source or ""
                range_pairs = re.findall(
                    r"toggleRange\s*\(\s*['\"]([^'\"]+)['\"].*?['\"]([^'\"]+)['\"]",
                    page_src
                )
                range_pairs = list(dict.fromkeys(range_pairs))
                if range_pairs:
                    print(f"[SCAN] DOM fallback found {len(range_pairs)} range(s)")
                    ranges_html = page_src  # use page source as ranges_html
                else:
                    preview = page_src[:800].replace('\n', ' ')
                    print(f"[DEBUG] Page source preview: {preview}")
            except Exception:
                pass

        if not range_pairs:
            print(f"[SCAN] No ranges found for {target_date}.")
            return results

        print(f"[SCAN] {len(range_pairs)} range(s) for {target_date}: "
              f"{[p[0] for p in range_pairs[:3]]}")

        # ── Process each range ─────────────────────────────────────────
        for display_name, css_id in range_pairs:

            # ── STEP A: Try extracting numbers from the getsms response itself ──
            # The getsms response sub-divs (id="sp_CSS_ID") contain phone numbers.
            # Pattern: <div id="sp_CAMBODIA_5058">..toggleNum*(85566550030, 1)..</div>
            numbers = []
            if ranges_html:
                # Extract sub-div content for this specific range
                sub_pattern = (
                    r'id=["\']sp_' + re.escape(css_id) + r'["\'][^>]*>'
                    r'([\s\S]*?)'
                    r'(?=<div[^>]*class=["\'][^"\']*rng|<div[^>]*id=["\']sp_[A-Z]|$)'
                )
                sub_match = re.search(sub_pattern, ranges_html)
                if sub_match:
                    sub_html = sub_match.group(1)
                    numbers = extract_numbers_from_response(sub_html)
                    if numbers:
                        print(f"[SCAN] Numbers from getsms sub-div '{css_id}': {numbers[:3]}")

            # ── STEP B: If getsms sub-div had no numbers, call getsms/number ──
            num_html = ""
            if not numbers:
                num_html = _browser_ajax(
                    driver,
                    "/portal/sms/received/getsms/number",
                    {"_token": csrf, "Range": css_id,
                     "start": target_date, "end": target_date},
                )
                if num_html.startswith("AJAX_ERR") or not num_html.strip():
                    print(f"[WARN] getsms/number failed for {css_id}: {num_html[:60]}")
                    num_html = ""

                if num_html:
                    print(f"[DEBUG] getsms/number for {css_id}: {len(num_html)} chars")
                    clean_n = num_html.replace('\n', ' ')
                    for ci in range(0, min(len(clean_n), 1500), 500):
                        print(f"[DEBUG] numResp[{ci}:{ci+500}]: {clean_n[ci:ci+500]}")
                    numbers = extract_numbers_from_response(num_html)

            # ── STEP C: DOM click fallback ──────────────────────────────
            if not numbers:
                print(f"[SCAN] Trying DOM click for {css_id}...")
                numbers = _dom_click_range_get_numbers(driver, css_id, display_name)

            if not numbers:
                print(f"[WARN] No numbers found for range '{display_name}'")
                continue

            print(f"[SCAN] Range '{display_name}' → {len(numbers)} number(s): {numbers[:3]}")

            # ── Fetch SMS for each number via browser AJAX ─────────────
            # Extract numeric Range ID from num_html (or ranges_html) script block
            numeric_range_id = css_id
            for src in [num_html, ranges_html]:
                if src:
                    nids = re.findall(r"Range\s*:\s*['\"]?(\d+)['\"]?", src)
                    if nids:
                        numeric_range_id = nids[0]
                        print(f"[DEBUG] Numeric Range ID: {numeric_range_id}")
                        break

            for phone in numbers:
                sms_html = _browser_ajax(
                    driver,
                    "/portal/sms/received/getsms/number/sms",
                    {"_token": csrf, "Range": numeric_range_id,
                     "Number": phone, "start": target_date, "end": target_date},
                )

                if not sms_html or sms_html.startswith("AJAX_ERR"):
                    print(f"[WARN] SMS AJAX failed for {phone}: {sms_html[:60]}")
                    # Fallback: try clicking in DOM
                    sms_html = _dom_click_number_get_sms(driver, phone)

                if not sms_html or not sms_html.strip():
                    print(f"[WARN] No SMS HTML for {phone}")
                    continue

                print(f"[DEBUG] SMS for {phone} ({len(sms_html)} chars): "
                      f"{sms_html[:200].replace(chr(10),' ')}")

                sms_list = parse_sms_html(sms_html)
                if not sms_list:
                    print(f"[WARN] parse_sms_html returned 0 items for {phone}")
                for service, text in sms_list:
                    results.append((phone, display_name, service, text))

    except Exception as e:
        print(f"[ERROR] selenium_scan_date({target_date}) crashed: {e}")

    return results


# ── DOM helper: submit the "Get SMS" form on the current page ──────────────
def _dom_submit_sms_form(driver, target_date: str):
    """Fill in the date form and click Get SMS on the currently loaded page."""
    try:
        # Set dates via JS and fire change events
        driver.execute_script("""
            var fields = [
                ['input[name="start"]','#start','input[id*="start"]'],
                ['input[name="end"]',  '#end',  'input[id*="end"]']
            ];
            var val = arguments[0];
            fields.forEach(function(sels, i) {
                sels.forEach(function(sel) {
                    var el = document.querySelector(sel);
                    if (el) {
                        el.value = val;
                        el.dispatchEvent(new Event('input',   {bubbles:true}));
                        el.dispatchEvent(new Event('change',  {bubbles:true}));
                    }
                });
            });
        """, target_date)
        time.sleep(0.5)

        # Click submit button — try multiple selectors
        clicked = False
        for sel in [
            "button[type='submit']",
            "input[type='submit']",
            ".btn-warning",
            ".btn-success",
            ".btn-primary",
            "button.btn",
        ]:
            try:
                el = driver.find_element("css selector", sel)
                driver.execute_script("arguments[0].click();", el)
                clicked = True
                print(f"[SCAN] Clicked button: {sel}")
                break
            except Exception:
                pass

        if not clicked:
            # Last resort: submit first form
            driver.execute_script(
                "var f=document.querySelector('form'); if(f) f.submit();"
            )

        # Wait for AJAX ranges to load (up to 12 seconds)
        for _ in range(24):
            time.sleep(0.5)
            try:
                elems = driver.find_elements("css selector", ".rng")
                if elems:
                    print(f"[SCAN] .rng divs appeared after form submit ({len(elems)})")
                    return
            except Exception:
                pass

        print("[WARN] .rng divs did not appear within 12s after form submit")

    except Exception as e:
        print(f"[WARN] _dom_submit_sms_form failed: {e}")


# ── DOM helper: click a range div and extract phone numbers ───────────────
def _dom_click_range_get_numbers(driver, css_id: str, display_name: str) -> list:
    """
    Click on the range element in the DOM to trigger toggleRange AJAX,
    then extract phone numbers from the populated sub-div.
    """
    numbers = []
    try:
        # Find the range div by its data or onclick attributes
        rng_div = None
        for sel in [
            f"[onclick*=\"'{css_id}'\"]",
            f"[onclick*='{display_name}']",
            ".rng",
        ]:
            try:
                candidates = driver.find_elements("css selector", sel)
                if candidates:
                    rng_div = candidates[0]
                    break
            except Exception:
                pass

        if rng_div is None:
            print(f"[WARN] DOM: range div not found for {css_id}")
            return numbers

        # Click to expand
        driver.execute_script("arguments[0].scrollIntoView(true);", rng_div)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", rng_div)

        # Wait for sub-div to populate
        sub_id = f"sp_{css_id}"
        for _ in range(14):
            time.sleep(0.5)
            try:
                sub = driver.find_element("css selector", f"#{sub_id}")
                inner = sub.get_attribute("innerHTML") or ""
                if len(inner.strip()) > 50:
                    numbers = extract_numbers_from_response(inner)
                    if numbers:
                        print(f"[SCAN] DOM click got {len(numbers)} numbers for {css_id}")
                    else:
                        print(f"[DEBUG] sub div innerHTML: {inner[:300].replace(chr(10),' ')}")
                    return numbers
            except Exception:
                pass

        print(f"[WARN] DOM: sub-div #{sub_id} did not populate")

    except Exception as e:
        print(f"[WARN] _dom_click_range_get_numbers({css_id}): {e}")

    return numbers


# ── DOM helper: click a phone number element and read SMS from safe-div ───
def _dom_click_number_get_sms(driver, phone: str) -> str:
    """Click on the phone number element; return the innerHTML of #{phone}-safe."""
    try:
        # Click the num element that matches this phone
        for sel in [
            f"[onclick*='{phone}']",
            f".num",
        ]:
            try:
                els = driver.find_elements("css selector", sel)
                for el in els:
                    txt = el.text or el.get_attribute("onclick") or ""
                    if phone in txt:
                        driver.execute_script("arguments[0].click();", el)
                        break
                break
            except Exception:
                pass

        # Wait for safe-div to load
        for _ in range(10):
            time.sleep(0.7)
            try:
                safe_el = driver.find_element("css selector", f"#{phone}-safe")
                inner = safe_el.get_attribute("innerHTML") or ""
                if len(inner.strip()) > 30:
                    return inner
            except Exception:
                pass

    except Exception as e:
        print(f"[WARN] _dom_click_number_get_sms({phone}): {e}")

    return ""

# ==========================================
# iVASMS-SPECIFIC RESPONSE PARSERS
# ivasms uses: onclick="toggleRange('NAME','ID')"
#              onclick="toggleNumDkNtn('PHONE', safe)"
# ==========================================

def extract_ranges_from_response(raw: str):
    """
    Extracts range identifiers from ivasms getsms response.

    ivasms HTML: onclick="toggleRange('CAMBODIA 3572','CAMBODIA_3572')"
      arg1 = display name  ('CAMBODIA 3572')  — used for country detection
      arg2 = CSS/API id    ('CAMBODIA_3572')  — used for getsms/number API call

    Returns list of (display_name, api_id) tuples.
    Falls back to [(val, val)] for non-toggleRange patterns.
    """
    # PRIMARY — extract BOTH args from toggleRange (most reliable)
    pairs = re.findall(
        r"toggleRange\s*\(\s*['\"]([^'\"]+)['\"].*?['\"]([^'\"]+)['\"]",
        raw
    )
    if pairs:
        unique = list(dict.fromkeys(pairs))
        print(f"[DEBUG] Ranges via toggleRange(name, id): {unique[:3]}")
        return unique   # [(display_name, api_id), ...]

    # FALLBACK — <option> tags
    soup = BeautifulSoup(raw, 'html.parser')
    opt_ranges = []
    for opt in soup.find_all('option'):
        val = opt.get('value', '').strip()
        if val and val.lower() not in ('', '--', 'all', 'select'):
            opt_ranges.append((val, val))
    if opt_ranges:
        print(f"[DEBUG] Ranges via <option>: {opt_ranges[:3]}")
        return list(dict.fromkeys(opt_ranges))

    # FALLBACK — data attributes
    attr_ranges = []
    for tag in soup.find_all(True):
        for attr in ['data-range', 'data-id', 'data-value']:
            val = tag.get(attr, '').strip()
            if val and len(val) > 2:
                attr_ranges.append((val, val))
    if attr_ranges:
        print(f"[DEBUG] Ranges via data-attr: {attr_ranges[:3]}")
        return list(dict.fromkeys(attr_ranges))

    # FALLBACK — text/html regex
    plain      = soup.get_text(separator=" ")
    text_found = re.findall(r'\b([A-Z]{2,}(?:\s+[A-Z]+)*\s+\d{1,8})\b', plain)
    html_found = re.findall(r"['\"]([A-Z]{2,}(?:\s[A-Z]+)*\s\d{1,8})['\"]", raw)
    all_found  = [(v, v) for v in dict.fromkeys(text_found + html_found)]
    if all_found:
        print(f"[DEBUG] Ranges via regex: {all_found[:3]}")
        return all_found

    print("[DEBUG] No ranges found in response.")
    return []


def extract_numbers_from_response(raw: str) -> list:
    """
    Extracts phone numbers from ivasms number-list / range-list response.

    ivasms-observed patterns (in order of reliability):
      A) id="PHONE-safe"                 → jQuery $('#'+id+'-safe') pattern
      B) toggleNum*(PHONE, ...)          → ANY randomised function name (unquoted)
      C) toggleNum*('PHONE', ...)        → ANY randomised function name (quoted)
      D) data-id / data-number attrs
      E) <option value="PHONE">
      F) JSON array/object walk
      G) Quoted digit strings anywhere in HTML/JS
      H) Unquoted in plain text (last resort)
    """
    numbers = set()

    # ── A: id="PHONE-safe" ── (most reliable — always consistent)
    pat_a = re.findall(r'id=["\'](\d{6,15})-safe["\']', raw)
    if pat_a:
        print(f"[DEBUG] Numbers via id='X-safe': {pat_a[:5]}")
        return list(dict.fromkeys(pat_a))

    # ── B: ANY toggleNum* function call — UNQUOTED ──
    # ivasms randomises the function name per response to prevent scraping
    # e.g.: toggleNumFyOj(85566550030, 1)  or  toggleNumDkNtn(85561234567, 1)
    pat_b = re.findall(r'toggleNum\w+\s*\(\s*(\d{6,15})\s*[,)]', raw)
    if pat_b:
        print(f"[DEBUG] Numbers via toggleNum*(unquoted): {pat_b[:5]}")
        return list(dict.fromkeys(pat_b))

    # ── C: ANY toggleNum* function call — QUOTED ──
    pat_c = re.findall(r"toggleNum\w+\s*\(\s*['\"](\d{6,15})['\"]", raw)
    if pat_c:
        print(f"[DEBUG] Numbers via toggleNum*(quoted): {pat_c[:5]}")
        return list(dict.fromkeys(pat_c))

    # ── D: data-id / data-number / data-phone HTML attributes ──
    soup  = BeautifulSoup(raw, 'html.parser')
    pat_d = set()
    for tag in soup.find_all(True):
        for attr in ['data-id', 'data-number', 'data-phone', 'data-value', 'data-num']:
            val = str(tag.get(attr, '')).strip()
            if re.fullmatch(r'\d{6,15}', val):
                pat_d.add(val)
    if pat_d:
        print(f"[DEBUG] Numbers via data-attrs: {list(pat_d)[:5]}")
        return list(pat_d)

    # ── E: <option value="PHONE"> ──
    pat_e = set()
    for opt in soup.find_all('option'):
        for candidate in [opt.get('value', ''), opt.get_text(strip=True)]:
            if re.fullmatch(r'\d{6,15}', candidate.strip()):
                pat_e.add(candidate.strip())
    if pat_e:
        print(f"[DEBUG] Numbers via <option>: {list(pat_e)[:5]}")
        return list(pat_e)

    # ── F: JSON walk ──
    try:
        data = json.loads(raw)
        pat_f = set()
        def _walk(obj):
            if isinstance(obj, dict):
                for v in obj.values():
                    _walk(v)
            elif isinstance(obj, list):
                for item in obj:
                    _walk(item)
            elif isinstance(obj, (str, int)):
                s = str(obj).strip()
                if re.fullmatch(r'\d{6,15}', s):
                    pat_f.add(s)
        _walk(data)
        if pat_f:
            print(f"[DEBUG] Numbers via JSON: {list(pat_f)[:5]}")
            return list(pat_f)
    except Exception:
        pass

    # ── G: Quoted digit strings anywhere in raw HTML/JS ──
    pat_g = re.findall(r'["\'](\d{6,15})["\']', raw)
    numbers.update(pat_g)

    # ── H: Unquoted in plain text (last resort) ──
    plain = soup.get_text(separator=" ")
    pat_h = re.findall(r'(?<!\d)(\d{6,15})(?!\d)', plain)
    numbers.update(pat_h)

    if numbers:
        print(f"[DEBUG] Numbers via regex last-resort: {list(numbers)[:5]}")
    return list(numbers)


# ==========================================
# STEP 2: MAIN OTP SCANNER (BD Timezone, 3-Step)
# ==========================================
def monitor_ranges():
    """
    Main scanner loop.
    Uses the live Selenium browser (login_and_get_driver) to directly
    click on ranges/numbers and extract SMS from the DOM.
    Re-logins automatically when the session expires or too many errors occur.
    """
    driver = None

    while True:
        # ── Login and get a live browser session ──
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass
            driver = None

        driver = login_and_get_driver()

        if driver is None:
            print("[SCANNER] Login failed. Retrying in 60 seconds...")
            time.sleep(60)
            continue

        print("[SCANNER] Browser session established. Starting OTP scan (Bangladesh timezone)...")

        consecutive_errors = 0

        while consecutive_errors < 6:
            try:
                today_bd     = bd_now().strftime("%Y-%m-%d")
                yesterday_bd = (bd_now() - timedelta(days=1)).strftime("%Y-%m-%d")
                date_list    = [today_bd, yesterday_bd]

                print(f"[SCAN] Scanning BD dates: {date_list}")
                total_sent = 0

                # ── Check session still alive ──
                try:
                    current = driver.current_url
                    if "login" in current.lower():
                        print("[SCAN] Session expired (redirected to login). Re-logging in...")
                        consecutive_errors = 999
                        break
                except Exception:
                    print("[SCAN] Browser session lost. Re-logging in...")
                    consecutive_errors = 999
                    break

                # ── Scan each date with Selenium ──
                for target_date in date_list:
                    sms_entries = selenium_scan_date(driver, target_date)

                    for phone, range_name, service_raw, full_text in sms_entries:
                        if not full_text or len(full_text) < 5:
                            continue
                        sig = f"{phone}|{service_raw}|{full_text[:120]}"
                        if is_seen(sig):
                            continue
                        send_otp_to_telegram(phone, service_raw, full_text, range_name)
                        total_sent += 1
                        time.sleep(0.3)

                if total_sent == 0:
                    print(f"[SCAN] No new OTPs for {today_bd}. Next check in 15s...")
                else:
                    print(f"[SCAN] Cycle complete — sent {total_sent} OTP(s).")

                consecutive_errors = 0

            except Exception as e:
                print(f"[ERROR] Scan cycle error: {e}")
                consecutive_errors += 1

            time.sleep(15)

        print("[SCANNER] Too many errors or session expired. Re-logging in...")

# ==========================================
# TELEGRAM COMMANDS
# ==========================================
@bot.message_handler(commands=['setbot'])
def cmd_setbot(message):
    global USER_BOT_USERNAME
    try:
        if str(message.chat.id) == GROUP_ID:
            parts = message.text.split()
            if len(parts) > 1:
                USER_BOT_USERNAME = parts[1].replace('https://t.me/', '').replace('@', '')
                bot.reply_to(message, f"✅ <b>Bot link updated:</b> @{USER_BOT_USERNAME}", parse_mode="HTML")
    except Exception:
        pass

@bot.message_handler(commands=['status'])
def cmd_status(message):
    bd_str = bd_now().strftime("%d-%b-%Y %I:%M:%S %p BST")
    bot.reply_to(
        message,
        f"✅ <b>Bot is running</b>\n"
        f"🕐 <b>BD Time:</b> {bd_str}\n"
        f"📦 <b>Tracked Signatures:</b> {len(seen_signatures)}",
        parse_mode="HTML"
    )

# ==========================================
# ENTRY POINT
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print("iVASMS OTP Bot starting...")
    print(f"BD Time: {bd_now().strftime('%d-%b-%Y %I:%M %p BST')}")
    print("Scanning: today + yesterday (Bangladesh dates)")
    print("=" * 60)

    if not BOT_TOKEN:
        print("[FATAL] BOT_TOKEN environment variable is not set!")
        exit(1)
    if not EMAIL or not PASSWORD:
        print("[FATAL] EMAIL or PASSWORD environment variable is not set!")
        exit(1)

    scanner_thread = threading.Thread(target=monitor_ranges, daemon=True, name="OTP-Scanner")
    scanner_thread.start()

    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10, skip_pending=True)
        except Exception as e:
            print(f"[WARN] Telegram polling error: {e}. Retrying in 5s...")
            time.sleep(5)
