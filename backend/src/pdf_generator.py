
class MockUser:
    id = '0'
    display_name = 'WebUser'
    mention = '@WebUser'
class MockColor:
    @classmethod
    def green(cls): return 0
    @classmethod
    def gold(cls): return 0
    @classmethod
    def red(cls): return 0
    @classmethod
    def blue(cls): return 0
class MockUtils:
    @staticmethod
    def utcnow():
        from datetime import datetime
        return datetime.now()
class MockEmbed:
    def __init__(self, **kwargs): pass
    def add_field(self, **kwargs): pass
    def set_footer(self, **kwargs): pass
class discord:
    User = MockUser
    Color = MockColor
    utils = MockUtils
    Embed = MockEmbed
    HTTPException = Exception
    
import io
import os
import re
import requests
from typing import Optional, Any
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.lib import fonts  # Do manipulacji _ps2tt
import json
import sqlite3
import traceback
from datetime import datetime
import random
import math

# Kolory
COLOR_TEXT = HexColor("#0F212B")
COLOR_LINK = HexColor("#13406D")
COLOR_GREY = HexColor("#BDBDBD")
COLOR_TW_BG = HexColor("#000000")
COLOR_TW_TEXT = HexColor("#FFFFFF")
COLOR_TW_SUB = HexColor("#71767B")

# Folder z zasobami (logo, czcionki)
SERVER_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(SERVER_ROOT, "assets")
DATA_DIR = os.path.join(SERVER_ROOT, "data")

# Fallback dla kompatybilności
FRONTEND_ASSETS = ASSETS_DIR
BACKEND_DATA = DATA_DIR
PROJECT_ROOT = SERVER_ROOT

def _ordinal_date(dt):
    """Pomocnicza funkcja daty (np. March 20th, 2026)."""
    suffix = "th" if 11 <= dt.day <= 13 else {1:"st", 2:"nd", 3:"rd"}.get(dt.day % 10, "th")
    return dt.strftime(f"%B {dt.day}{suffix}, %Y")

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION – dostosuj według próprio serwera
# ─────────────────────────────────────────────────────────────────────────────

DOCS_CHANNEL_ID = 1483813760048169142          # TODO: Ustaw ID kanału gdzie ma wisieć panel
GUILD_ID        = 1246200136573649027
LOG_CHANNEL_ID  = 1453206606035812493

# Dane organizacji (dla pierwszego typu dokumentu)
ORG_NAME        = "Los Santos Police Department"
ORG_SUBTITLE    = "Los Santos, San Andreas"
DOC_TYPE_LABEL  = "News Release"

# Stopka dokumentu (3 linie, jak na zdjęciu poglądowym)
FOOTER_LINE_1 = "Dołącz do zespołu  ·  LSPD na LifeInvader  ·  LSPD na Twitterze"
FOOTER_LINE_2 = "1308 San Andreas Avenue  ·  Los Santos, San Andreas"
FOOTER_LINE_3 = "Linia cywilna: 9101  ·  Email: pio@lspd.online"

from xhtml2pdf import pisa

DIVISIONS = {
    "metro": ("Metropolitan Division",             "l-metro.png"),
    "raed":  ("Recruitment And Employment Division","l-raed.png"),
    "fod":   ("Fiscal Operations Division",        "l-fod.png"),
    "fld":   ("Firearms Licensing Division",       "l-fld.png"),
    "pd":    ("Personnel Division",                "l-pd.png"),
    "cd":    ("Communications Division",           "l-cd.png"),
    "bss":   ("Behavioral Science Services",       "l-bss.png"),
    "dtp":   ("Detective Training Program",        "l-dtp.png"),
    "stp":   ("Supervisor Training Program",       "l-stp.png"),
    "ftp":   ("Field Training Program",            "l-ftp.png"),
    "pcd":   ("Public Communications Division",     "l-pcd.png"),
    "iag":   ("Internal Affairs Group",            "l-iag.png"),
    "rmalag":("Risk Management And Legal Affairs Group","l-rmalag.png"),
    "fts":   ("Firearms Training Section",         "l-fts.png"),
    "td":    ("Traffic Division",                  "l-td.png"),
    "asd":   ("Air Support Division",              "l-asd.png"),
    "missionrow": ("Patrol Division",              "l-missionrow.png"),
    "k9":    ("K9",                                "l-k9.png"),
    "bs":    ("Bomb Squad",                        "l-bs.png"),
    "fsd":   ("Forensic Science Division",         "l-fsd.png"),
    "git":   ("Gang Impact Team",                  "l-git.png"),
    "db":    ("Detective Bureau",                  "l-db.png"),
    "mcd":   ("Major Crimes Division",             "l-mcd.png"),
    "gnd":   ("Gang & Narcotics Division",         "l-gnd.png"),
    "gd":    ("Mission Row Gang Detail",           "l-gd.png"),
    "slo":   ("Senior Lead Program",           "l-slo.png"),
}

def generate_html_pdf(html_content: str) -> Optional[io.BytesIO]:
    """Konwertuje HTML (z BBCode) na PDF przy użyciu xhtml2pdf."""
    result = io.BytesIO()
    
    def link_callback(uri, rel):
        """Pomaga xhtml2pdf znaleźć lokalne arkusze i obrazy."""
        if uri.startswith('assets/'):
            path = os.path.join(FRONTEND_ASSETS, uri.replace('assets/', ''))
        else:
            # Fallback dla innych ścieżek
            path = os.path.join(PROJECT_ROOT, uri)
            
        if not os.path.isfile(path):
            print(f"[DOCS_PDF] Asset not found: {path} (from URI: {uri})")
            return uri
        return path

    # Dodaj style bazowe dla BBCode jeśli nie ma ich w HTML
    styled_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: a4; margin: 1.5cm; }}
            body {{ font-family: Helvetica; font-size: 10pt; color: #333; }}
            .paper-sheet-content {{ background: white; }}
            .bb-divbox2 {{ border: 2px solid #333; padding: 15px; margin-bottom: 10px; }}
            .bb-hr {{ border-top: 1px solid #ccc; margin: 10px 0; }}
            .bb-align-center {{ text-align: center; }}
            .bb-align-right {{ text-align: right; }}
            .bb-spoiler-header {{ background: #eee; padding: 5px; font-weight: bold; border: 1px solid #ccc; }}
            .bb-spoiler-content {{ border: 1px solid #ccc; border-top: none; padding: 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td, th {{ padding: 5px; border: 1px solid #eee; }}
        </style>
    </head>
    <body class="paper-sheet-content">
        {html_content}
    </body>
    </html>
    """
    
    # xhtml2pdf nie wspiera wszystkich tagów HTML5, ale dla BBCode wystarczy
    pisa_status = pisa.CreatePDF(styled_html, dest=result, link_callback=link_callback)
    
    if pisa_status.err:
        print(f"[DOCS_PDF] Błąd generowania: {pisa_status.err}")
        return None
        
    result.seek(0)
    return result


async def log_action(bot, action: str, user: Any, data: dict, extra: str = ""):
    """Wysyła embed na kanał LOG_CHANNEL_ID."""
    if not bot: return # No bot connection (e.g. web api)
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        try:
            channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        except Exception:
            print(f"[LOG_ERROR] Nie znaleziono kanału logów: {LOG_CHANNEL_ID}")
            return

    # Kolory zależne od akcji: zielony = generate, żółty = edit, czerwony = recall, niebieski = view/export
    colors_map = {
        "generate": discord.Color.green(),
        "edit": discord.Color.gold(),
        "recall": discord.Color.red(),
        "view": discord.Color.blue(),
        "export": discord.Color.blue(),
        "error": discord.Color.red()
    }

    action_lower = action.lower()
    current_color = discord.Color.blue()
    
    if any(k in action_lower for k in ["wygenerowany", "zapisano", "zapisuje"]):
        current_color = colors_map["generate"]
    elif any(k in action_lower for k in ["edycja", "edytuj", "otwarty", "zatwierdzony"]):
        current_color = colors_map["edit"]
    elif any(k in action_lower for k in ["wycofany", "recall", "błąd", "nieudany", "anuluj", "krytyczny"]):
        current_color = colors_map["recall"]

    embed = discord.Embed(
        title="📝 Log Systemu Dokumentów",
        color=current_color,
        timestamp=discord.utils.utcnow()
    )
    
    u_mention = getattr(user, 'mention', user.get('mention', '@WebUser')) if isinstance(user, dict) else getattr(user, 'mention', '@WebUser')
    u_id = getattr(user, 'id', user.get('id', '0')) if isinstance(user, dict) else getattr(user, 'id', '0')
    u_name = getattr(user, 'display_name', user.get('display_name', 'WebUser')) if isinstance(user, dict) else getattr(user, 'display_name', 'WebUser')

    embed.add_field(name="Akcja", value=action, inline=True)
    embed.add_field(name="Autor", value=f"{u_mention} ({u_id})", inline=True)
    
    doc_num = data.get("doc_number", "Brak")
    doc_title = data.get("title", data.get("subject", "Bez tytułu"))
    embed.add_field(name="Dokument", value=f"#{doc_num} - {doc_title}", inline=False)
    
    template = data.get("template_name", data.get("template", "Nieokreślony"))
    embed.add_field(name="Szablon", value=template, inline=True)
    embed.add_field(name="Czas", value=f"<t:{int(discord.utils.utcnow().timestamp())}:F>", inline=True)
    
    if extra:
        embed.add_field(name="Extra", value=f"```{extra[:1000]}```", inline=False)
        
    embed.set_footer(text=f"User ID: {u_id}")
    
    try:
        await channel.send(embed=embed)
    except Exception as e:
        print(f"[LOG_ERROR] Błąd wysyłania loga: {e}")


def format_discord_error(e: discord.HTTPException) -> str:
    """Konwertuje techniczny błąd Discorda na czytelny komunikat dla użytkownika."""
    original_text = e.text
    friendly_errors = []
    
    if "Not a well formed URL" in original_text or "Invalid Form Body" in original_text and "url" in original_text.lower():
        friendly_errors.append("- 🔗 **Błędny link (URL):** Jeden z wklejonych linków do zdjęć jest nieprawidłowy. Upewnij się, że link zaczyna się od `http://` lub `https://` i prowadzi bezpośrednio do pliku graficznego.")
    
    if "Must be 1024 or fewer in length" in original_text:
        friendly_errors.append("- 📝 **Zbyt długi tekst w polu:** Jedno z pól tekstowych przekracza limit 1024 znaków Discorda. Spróbuj skrócić opis lub podzielić go na części.")
    
    if "Must be 2048 or fewer in length" in original_text:
        friendly_errors.append("- 🔗 **Link jest zbyt długi:** URL, który wkleiłeś, ma ponad 2048 znaków. Discord nie obsługuje tak długich linków.")

    if "Must be 4000 or fewer in length" in original_text:
        friendly_errors.append("- 📝 **Całkowita treść jest zbyt długa:** Łączna liczba znaków w dokumencie przekracza limity Discorda.")

    if not friendly_errors:
        return f"❌ **Wystąpił błąd podczas komunikacji z Discordem:**\n`{original_text}`\n\nUżyj przycisku poniżej, aby spróbować poprawić dane."
    
    return (
        "### ❌ Wykryto błąd w Twoich danych!\n"
        "Twoja wiadomość nie mogła zostać przetworzona z następujących powodów:\n\n"
        + "\n".join(friendly_errors) +
        "\n\n**Co teraz?** Kliknij przycisk **Edytuj**, aby powrócić do formularza. Twoje dane nie zostały utracone!"
    )


# ─────────────────────────────────────────────────────────────────────────────
# ARCHIWUM SQLITE
# ─────────────────────────────────────────────────────────────────────────────

DB_PATH = os.path.join(BACKEND_DATA, "archive.db")

def init_db():
    """Tworzy tabelę dokumentów jeśli nie istnieje."""
    os.makedirs(BACKEND_DATA, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    try:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_number TEXT UNIQUE,
                template TEXT,
                title TEXT,
                author_id TEXT,
                author_name TEXT,
                guild_id TEXT,
                created_at TEXT,
                data_json TEXT,
                status TEXT DEFAULT 'active',
                notes TEXT DEFAULT ''
            )
        ''')
        conn.commit()
    finally:
        conn.close()

async def archive_document(data: dict, user: Any, guild_id: str):
    """Zapisuje dokument w bazie danych."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=15.0)
        try:
            c = conn.cursor()
            c.execute('''
                INSERT INTO documents (doc_number, template, title, author_id, author_name, guild_id, created_at, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get("doc_number"),
                data.get("template_name"),
                data.get("title") or data.get("subject", "Bez tytułu"),
                str(getattr(user, 'id', user.get('id', '0')) if isinstance(user, dict) else getattr(user, 'id', '0')),
                getattr(user, 'display_name', user.get('display_name', 'WebUser')) if isinstance(user, dict) else getattr(user, 'display_name', 'WebUser'),
                str(guild_id),
                datetime.now().isoformat(),
                json.dumps(data)
            ))
            conn.commit()
            last_id = c.lastrowid
            return last_id
        finally:
            conn.close()
    except Exception as e:
        print(f"[DB_ERROR] Błąd archiwizacji: {e}")
        return None

async def get_document(doc_number: str):
    """Pobiera dokument z bazy."""
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    try:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM documents WHERE doc_number = ?", (doc_number,))
        row = c.fetchone()
        return row
    finally:
        conn.close()

async def list_documents(limit=10, offset=0, template=None, author_id=None):
    """Listuje dokumenty z paginacją."""
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    try:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        query = "SELECT * FROM documents"
        params = []
        
        if template or author_id:
            query += " WHERE "
            conditions = []
            if template:
                conditions.append("template = ?")
                params.append(template)
            if author_id:
                conditions.append("author_id = ?")
                params.append(str(author_id))
            query += " AND ".join(conditions)
            
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        c.execute(query, tuple(params))
        rows = c.fetchall()
        return rows
    finally:
        conn.close()

async def recall_document(bot, doc_number: str, reason: str, user: dict):
    """Wycofuje dokument (zmienia status na 'recalled')."""
    try:
        conn = sqlite3.connect(DB_PATH, timeout=15.0)
        try:
            c = conn.cursor()
            c.execute("UPDATE documents SET status = 'recalled', notes = ? WHERE doc_number = ?", (reason, doc_number))
            success = c.rowcount > 0
            conn.commit()
        finally:
            conn.close()
        
        if success:
            await log_action(bot, "recalled", user, {"doc_number": doc_number}, extra=f"Powód: {reason}")
        return success
    except Exception as e:
        print(f"[DB_ERROR] Błąd recall: {e}")
        return False

async def get_stats():
    """Pobiera statystyki z archiwum."""
    conn = sqlite3.connect(DB_PATH, timeout=15.0)
    try:
        c = conn.cursor()
        
        stats = {}
        
        # Total
        c.execute("SELECT COUNT(*) FROM documents")
        stats['total'] = c.fetchone()[0]
        
        # By template
        c.execute("SELECT template, COUNT(*) FROM documents GROUP BY template")
        stats['by_template'] = dict(c.fetchall())
        
        # Last 7 days
        from datetime import timedelta
        seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
        c.execute("SELECT COUNT(*) FROM documents WHERE created_at >= ?", (seven_days_ago,))
        stats['last_7_days'] = c.fetchone()[0]
        
        # Top Authors
        c.execute("SELECT author_name, COUNT(*) as count FROM documents GROUP BY author_id ORDER BY count DESC LIMIT 3")
        stats['top_authors'] = c.fetchall()
        
        return stats
    finally:
        conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# CZCIONKI – Arial z automatycznym fallbackiem na Helvetica
# ─────────────────────────────────────────────────────────────────────────────

_fonts_ready = False
_font_family = "Helvetica"
_font_r  = "Helvetica"
_font_b  = "Helvetica-Bold"
_font_i  = "Helvetica-Oblique"
_font_bi = "Helvetica-BoldOblique"
_font_s  = "Helvetica-Oblique"
_font_tw_r = "Helvetica"
_font_tw_b = "Helvetica-Bold"

def _setup_fonts():
    global _fonts_ready, _font_r, _font_b, _font_i, _font_bi, _font_s, _font_family, _font_tw_r, _font_tw_b
    if _fonts_ready:
        return _font_r, _font_b, _font_i, _font_bi, _font_s

    # ── ŚCIEŻKI WYSZUKIWANIA ──────────────────────────────────────────────
    search_paths = [
        FRONTEND_ASSETS,
        # Windows Fonts
        "C:/Windows/Fonts",
        os.path.expanduser("~/AppData/Local/Microsoft/Windows/Fonts"),
    ]

    candidates = {
        # Główna czcionka dokumentów – Arial (wspiera polskie znaki jako TTF)
        "Arial":            ["arial.ttf",   "Arial.ttf",    "LiberationSans-Regular.ttf",  "FreeSans.ttf"],
        "Arial-Bold":       ["arialbd.ttf", "Arial_Bold.ttf","LiberationSans-Bold.ttf",     "FreeSansBold.ttf"],
        "Arial-Italic":     ["ariali.ttf",  "Arial_Italic.ttf","LiberationSans-Italic.ttf", "FreeSansOblique.ttf"],
        "Arial-BoldItalic": ["arialbi.ttf", "Arial_Bold_Italic.ttf","LiberationSans-BoldItalic.ttf","FreeSansBoldOblique.ttf"],
        # Twitter – Segoe UI
        "SegoeUI":          ["segoeuiregular.ttf", "segoeui.ttf"],
        "SegoeUI-Bold":     ["segoeuibold.ttf",    "segoeuib.ttf"],
        # Podpis odręczny
        "Signature":        ["podpis.ttf", "Signature.ttf"],
    }

    def _find(names):
        for p in search_paths:
            for n in names:
                fp = os.path.join(p, n)
                if os.path.exists(fp): return fp
        return None

    # ── REJESTRACJA TTF ───────────────────────────────────────────────────
    for reg_name, filenames in candidates.items():
        path = _find(filenames)
        if path:
            try:
                pdfmetrics.registerFont(TTFont(reg_name, path))
                if reg_name == "Arial":            _font_r  = "Arial"
                elif reg_name == "Arial-Bold":     _font_b  = "Arial-Bold"
                elif reg_name == "Arial-Italic":   _font_i  = "Arial-Italic"
                elif reg_name == "Arial-BoldItalic": _font_bi = "Arial-BoldItalic"
                elif reg_name == "SegoeUI":        _font_tw_r = "SegoeUI"
                elif reg_name == "SegoeUI-Bold":   _font_tw_b = "SegoeUI-Bold"
                elif reg_name == "Signature":      _font_s  = "Signature"
                print(f"[DOCS] Font załadowany: {reg_name} from {path}")
            except Exception as e:
                print(f"[DOCS] Błąd ładowania fontu {reg_name} ({path}): {e}")
        else:
            if reg_name in ("Arial", "Arial-Bold"):
                print(f"[DOCS] UWAGA: Font {reg_name} nie znaleziony – polskie znaki mogą nie działać!")

    # ── REJESTRACJA RODZIN (dla <b>, <i> w Paragraph) ─────────────────────
    try:
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        from reportlab.lib.fonts import addMapping

        # Arial – pełna rodzina (normal / bold / italic / boldItalic)
        if _font_r == "Arial":
            bold  = _font_b  if _font_b  == "Arial-Bold"        else "Arial"
            ital  = _font_i  if _font_i  == "Arial-Italic"       else "Arial"
            bital = _font_bi if _font_bi == "Arial-BoldItalic"   else bold
            
            registerFontFamily("Arial", normal="Arial", bold=bold, italic=ital, boldItalic=bital)
            addMapping("Arial", 0, 0, "Arial")
            addMapping("Arial", 1, 0, bold)
            addMapping("Arial", 0, 1, ital)
            addMapping("Arial", 1, 1, bital)
            
            # Mapowanie nazw małych liter dla kompatybilności
            if hasattr(fonts, '_ps2tt'):
                fonts._ps2tt["arial"]           = ("Arial", 0, 0)
                fonts._ps2tt["arial-bold"]      = (bold,   1, 0)
                fonts._ps2tt["arial-italic"]    = (ital,   0, 1)
                fonts._ps2tt["arial-bolditalic"]= (bital,  1, 1)
            _font_i  = ital
            _font_bi = bital

        # SegoeUI (Twitter)
        if _font_tw_r == "SegoeUI":
            # SegoeUI często nie ma wszystkich wariantów w assets, mapujemy co mamy
            tw_bold = _font_tw_b if _font_tw_b == "SegoeUI-Bold" else "SegoeUI"
            registerFontFamily("SegoeUI", normal="SegoeUI", bold=tw_bold, italic="SegoeUI", boldItalic=tw_bold)
            addMapping("SegoeUI", 0, 0, "SegoeUI")
            addMapping("SegoeUI", 1, 0, tw_bold)
            addMapping("SegoeUI", 0, 1, "SegoeUI")
            addMapping("SegoeUI", 1, 1, tw_bold)
            if hasattr(fonts, '_ps2tt'):
                fonts._ps2tt["segoeui"]      = ("SegoeUI", 0, 0)
                fonts._ps2tt["segoeui-bold"] = (tw_bold, 1, 0)

        # Helvetica – Standardowa rodzina (zawsze warto zarejestrować jawnie)
        registerFontFamily("Helvetica", normal="Helvetica", bold="Helvetica-Bold", italic="Helvetica-Oblique", boldItalic="Helvetica-BoldOblique")
        addMapping("Helvetica", 0, 0, "Helvetica")
        addMapping("Helvetica", 1, 0, "Helvetica-Bold")
        addMapping("Helvetica", 0, 1, "Helvetica-Oblique")
        addMapping("Helvetica", 1, 1, "Helvetica-BoldOblique")

    except Exception as e:
        print(f"[DOCS] Błąd rejestracji rodziny fontów: {e}")

    _fonts_ready = True
    return _font_r, _font_b, _font_i, _font_bi, _font_s


# ─────────────────────────────────────────────────────────────────────────────
# PARSER DISCORD MARKDOWN → ReportLab Paragraph XML
# ─────────────────────────────────────────────────────────────────────────────

def _xml_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _md_inline(text: str) -> str:
    """Konwertuje inline markdown → tagi ReportLab."""
    text = _xml_escape(text)

    # 1. Bold + Italic (3 znaczniki) - najpierw najdłuższe
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'___(.+?)___',     r'<b><i>\1</i></b>', text)

    # 2. Bold / Underline (2 znaczniki)
    text = re.sub(r'\*\*(.+?)\*\*',     r'<b>\1</b>',         text)
    text = re.sub(r'__(.+?)__',         r'<u>\1</u>',         text)

    # 3. Italic (1 znacznik) - używamy [^*] i [^_] aby nie łapać fragmentów pogrubienia
    text = re.sub(r'\*([^*]+?)\*',       r'<i>\1</i>',         text)
    text = re.sub(r'_([^_]+?)_',         r'<i>\1</i>',         text)
    
    # NOWE ZNACZNIKI INLINE
    text = re.sub(r'~~(.+?)~~', r'<strike>\1</strike>', text)
    
    # {{tekst}} -> caption: 8pt, italic, szary
    text = re.sub(r'\{\{(.+?)\}\}', r'<font size="8" color="#888888"><i>\1</i></font>', text)
    
    # [REDACTED] -> czarny prostokąt
    text = text.replace("[REDACTED]", '<font color="black" backColor="black">REDACTED</font>')
    
    # {CLASSIFIED} -> czerwony stempel
    text = text.replace("{CLASSIFIED}", '<font color="#E62325"><b>[ CLASSIFIED ]</b></font>')
    
    # Twitter Hashtags & Mentions -> Blue (Obsługa polskich znaków)
    # Zapobieganie dopasowaniu kolorów HEX (np. #888888) poprzez lookbehind (nie może być poprzedzony = lub ")
    text = re.sub(r'(?<![="])#([a-zA-Z0-9ąęśćźżółńĄĘŚĆŹŻÓŁŃ]+)', r'<font color="#1D9BF0">#\1</font>', text)
    text = re.sub(r'@([a-zA-Z0-9ąęśćźżółńĄĘŚĆŹŻÓŁŃ._]+)', r'<font color="#1D9BF0">@\1</font>', text)
    
    return text
def _parse_content(text: str, data: dict = None) -> list:
    """
    Zwraca listę dict:
      {'kind': 'title'|'subtitle'|'paragraph'|'bullet'|..., 'xml': str}
    """
    if data:
        # Auto-replace dynamic tags
        from datetime import timedelta
        now = datetime.now() + timedelta(hours=1)
        text = text.replace("{DATE}", _ordinal_date(now))
        text = text.replace("{TIME}", now.strftime("%H:%M"))
        text = text.replace("{YEAR}", str(now.year))
        text = text.replace("{AUTHOR}", data.get("author_name", "Author"))
        text = text.replace("{DOC_NUMBER}", data.get("doc_number", "NR-000"))

    items = []
    lines = text.split("\n")
    in_checklist = False
    
    for line in lines:
        stripped = line.strip()
        
        # Obsługa ((przypis)) - musimy je wyciągnąć blokowo jeśli chcemy je na dole
        # Ale user chce superscript w miejscu wywołania.
        # Robimy to sprytnie: szukamy wszystkich ((...)) w linii.
        
        if stripped == "":
            items.append({"kind": "spacer"})
            continue
            
        # BLOKOWE
        if stripped == "---":
            items.append({"kind": "separator"})
        elif stripped == "===":
            items.append({"kind": "separator_double"})
        elif stripped.startswith("## "):
            items.append({"kind": "subtitle_centered", "xml": _md_inline(stripped[3:])})
        elif stripped.startswith("# "):
            items.append({"kind": "subtitle", "xml": _md_inline(stripped[2:])})
        elif stripped.startswith("- "):
            if in_checklist:
                items.append({"kind": "checklist", "xml": _md_inline(stripped[2:])})
            else:
                items.append({"kind": "bullet", "xml": _md_inline(stripped[2:])})
        elif stripped.startswith(":::"):
            items.append({"kind": "blockquote", "xml": _md_inline(stripped.replace(":::", ""))})
        elif stripped.startswith(">>"):
            items.append({"kind": "indent", "xml": _md_inline(stripped[2:])})
        elif stripped.startswith("!WARNING:"):
            items.append({"kind": "box", "box_type": "warning", "xml": _md_inline(stripped[9:])})
        elif stripped.startswith("!NOTE:"):
            items.append({"kind": "box", "box_type": "note", "xml": _md_inline(stripped[6:])})
        elif stripped.startswith("!INFO:"):
            items.append({"kind": "box", "box_type": "info", "xml": _md_inline(stripped[6:])})
        elif stripped.startswith("!IMPORTANT:"):
            items.append({"kind": "box", "box_type": "important", "xml": _md_inline(stripped[11:])})
        elif stripped.startswith("!LEGAL:"):
            items.append({"kind": "box", "box_type": "legal", "xml": _md_inline(stripped[7:])})
        elif stripped.startswith("!SIGNATURE:"):
            # Obsługa !SIGNATURE: Imię | Ranga lub fallback na !SIGNATURE: Imię, Ranga lub po prostu tekst
            content_sig = stripped[11:].strip()
            if "|" in content_sig:
                parts = content_sig.split("|")
                name = parts[0].strip() if len(parts) > 0 else ""
                rank = parts[1].strip() if len(parts) > 1 else ""
            elif "," in content_sig:
                parts = content_sig.split(",", 1)
                name = parts[0].strip()
                rank = parts[1].strip()
            else:
                name = content_sig
                rank = ""
            items.append({"kind": "signature", "name": name, "rank": rank})
        elif stripped.startswith("!AUTH:"):
            name = stripped[6:].strip()
            items.append({"kind": "handwritten_signature", "name": name})
        elif stripped == "!CHECKLIST:":
            in_checklist = True
        elif stripped.startswith("|") and stripped.endswith("|"):
            # Table logic
            cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if len(items) > 0 and items[-1]['kind'] == 'table' and not items[-1].get('closed'):
                items[-1]['rows'].append(cells)
            else:
                items.append({"kind": "table", "headers": cells, "rows": []})
        elif stripped.startswith("<<") and stripped.endswith(">>"):
            items.append({"kind": "paragraph", "xml": f'<para align="right">{_md_inline(stripped[2:-2])}</para>'})
        elif "[IMG:" in stripped:
            match = re.search(r'\[IMG:(.+?)\]', stripped)
            if match:
                items.append({"kind": "image", "url": match.group(1)})
        else:
            # Inline tags check for full line formatting
            xml = _md_inline(stripped)
            # Obsługa ((przypis)) - musimy nadać im numery
            # Ten konkretny znacznik wymaga specjalnego traktowania w render_content_block
            items.append({"kind": "paragraph", "xml": xml})
                
    return items


def get_next_doc_number(doc_type_key: str) -> str:
    """Generuje i inkrementuje numer dokumentu (np. NR003-3js)."""
    os.makedirs(BACKEND_DATA, exist_ok=True)
    counter_path = os.path.join(BACKEND_DATA, "counters.json")
    counters = {}
    
    if os.path.exists(counter_path):
        try:
            with open(counter_path, "r") as f:
                counters = json.load(f)
        except Exception:
            pass

    # Konfiguracja numeracji
    if doc_type_key == "missing_person":
        prefix = "DR# "
        suffix = ""
        current = counters.get(doc_type_key, 2026020) # Rok + numer
    elif doc_type_key == "wanted":
        prefix = "HR-26"
        suffix = ""
        current = counters.get(doc_type_key, 11)
    elif doc_type_key == "personnel_change":
        prefix = "PC-26"
        suffix = ""
        current = counters.get(doc_type_key, 5)
    elif doc_type_key == "disciplinary_action":
        prefix = "DA-26"
        suffix = ""
        current = counters.get(doc_type_key, 1)
    elif doc_type_key == "official_letter":
        prefix = "OL-26"
        suffix = ""
        current = counters.get(doc_type_key, 1)
    elif doc_type_key == "division_letter":
        prefix = "DL-26"
        suffix = "-js"
        current = counters.get(doc_type_key, 1)
    elif doc_type_key == "tweet":
        prefix = "TW-26"
        suffix = ""
        current = counters.get(doc_type_key, 1)
    else:
        prefix = "NR"
        suffix = "-3js"
        current = counters.get(doc_type_key, 2)
    
    if current < 2 and doc_type_key not in ["missing_person", "wanted"]: 
        current = 2 
    
    next_num = current + 1
    counters[doc_type_key] = next_num

    try:
        with open(counter_path, "w") as f:
            json.dump(counters, f)
    except Exception as e:
        print(f"[DOCS] Błąd zapisu licznika: {e}")

    return f"{prefix}{next_num:03d}{suffix}"


def _fetch_image(url: str) -> Optional[io.BytesIO]:
    if not url: return None
    import io
    if url.startswith("data:image/"):
        import base64
        try:
            head, base64_data = url.split(',', 1)
            img_data = base64.b64decode(base64_data)
            return io.BytesIO(img_data)
        except Exception as e:
            print(f"[DOCS] Błąd dekodowania base64: {e}")
            return None

    # Przycinanie .com na i.imgur.com dla skopiowanych adresów z paska
    if "imgur.com" in url and "i.imgur.com" not in url:
        url = url.replace("imgur.com", "i.imgur.com")
        if not url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            url += ".png"

    req_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "image/webp,image/apng,image/png,image/jpeg,image/*,*/*;q=0.8",
    }

    urls_to_try = [url]

    # Fallback: media.discordapp.net → cdn.discordapp.com
    if "media.discordapp.net" in url:
        cdn_url = url.replace("media.discordapp.net", "cdn.discordapp.com")
        # media proxy dodaje ?width=&height= — usuń, bo cdn tego nie obsługuje
        cdn_url = re.sub(r'[&?](width|height)=\d+', '', cdn_url).rstrip('?&')
        urls_to_try.append(cdn_url)

    for try_url in urls_to_try:
        try:
            resp = requests.get(try_url, headers=req_headers, stream=True, timeout=10, allow_redirects=True)
            if resp.status_code == 200:
                return io.BytesIO(resp.content)
            else:
                print(f"[DOCS] Status {resp.status_code} dla {try_url}")
        except Exception as e:
            print(f"[DOCS] Błąd pobierania obrazu ({try_url}): {e}")

    return None


def render_content_block(c, items, x, y, width, styles, limit_y=50):
    """
    Uniwersalna funkcja renderująca bloki treści na canvasie.
    """
    curr_y = y
    footnotes = []

    def process_footnotes(xml_text):
        nonlocal footnotes
        found = re.findall(r'\(\((.+?)\)\)', xml_text)
        for f in found:
            num = len(footnotes) + 1
            footnotes.append(f)
            xml_text = xml_text.replace(f"(({f}))", f'<sup>{num}</sup>')
        return xml_text

    first_sig = True
    for item in items:
        # Sprawdzanie limitu wysokości (stopka)
        if curr_y < limit_y:
            break

        kind = item.get("kind")
        xml = item.get("xml", "")
        
        if kind in ["paragraph", "bullet", "checklist", "blockquote", "indent", "subtitle", "subtitle_centered"]:
             xml = process_footnotes(xml)
             first_sig = True # Reset gap trigger for signatures

        if kind == "paragraph":
            p = Paragraph(xml, styles['para'])
            _, h = p.wrap(width, 10000)
            p.drawOn(c, x, curr_y - h)
            curr_y -= h + styles['para'].spaceAfter
            
        elif kind == "subtitle":
            p = Paragraph(xml, styles['subtitle'])
            _, h = p.wrap(width, 10000)
            p.drawOn(c, x, curr_y - h)
            curr_y -= h + styles['subtitle'].spaceAfter
            
        elif kind == "subtitle_centered":
            p = Paragraph(xml, styles['subtitle_centered'])
            _, h = p.wrap(width, 10000)
            p.drawOn(c, x, curr_y - h)
            curr_y -= h + styles['subtitle_centered'].spaceAfter

        elif kind == "bullet":
            p = Paragraph(f"• {xml}", styles['bullet'])
            _, h = p.wrap(width, 10000)
            p.drawOn(c, x, curr_y - h)
            curr_y -= h + styles['bullet'].spaceAfter

        elif kind == "checklist":
            p = Paragraph(f"□ {xml}", styles['bullet'])
            _, h = p.wrap(width, 10000)
            p.drawOn(c, x, curr_y - h)
            curr_y -= h + styles['bullet'].spaceAfter

        elif kind == "separator":
            c.setLineWidth(0.5)
            c.setStrokeColor(HexColor("#BDBDBD"))
            c.line(x, curr_y - 5, x + width, curr_y - 5)
            curr_y -= 15

        elif kind == "separator_double":
            c.setLineWidth(0.5)
            c.setStrokeColor(HexColor("#BDBDBD"))
            c.line(x, curr_y - 3, x + width, curr_y - 3)
            c.line(x, curr_y - 6, x + width, curr_y - 6)
            curr_y -= 18

        elif kind == "blockquote":
            bar_color = HexColor("#13406D")
            p = Paragraph(xml, styles.get('italic', styles['para']))
            _, h = p.wrap(width - 25, 10000)
            c.setLineWidth(2)
            c.setStrokeColor(bar_color)
            c.line(x + 5, curr_y, x + 5, curr_y - h)
            p.drawOn(c, x + 20, curr_y - h)
            curr_y -= h + 15

        elif kind == "indent":
            p = Paragraph(xml, styles['para'])
            _, h = p.wrap(width - 30, 10000)
            p.drawOn(c, x + 30, curr_y - h)
            curr_y -= h + styles['para'].spaceAfter

        elif kind == "box":
            box_type = item.get("box_type", "info")
            cfg = {
                "warning": {"stroke": "#E62325", "fill": "#FFF0F0", "bold": True},
                "note":    {"stroke": "#13406D", "fill": "#F0F4FF", "bold": False},
                "info":    {"stroke": "#BDBDBD", "fill": "#F8F8F8", "bold": False},
                "important":{"stroke":"#FF8C00", "fill": "#FFF8F0", "bold": True},
                "legal":   {"stroke": "none",    "fill": "#F8F8F8", "bold": False, "font_size": 8, "text_color": "#666666"}
            }.get(box_type, {"stroke": "#BDBDBD", "fill": "#F8F8F8", "bold": False})
            
            p_style = ParagraphStyle(
                name=f"box_{box_type}",
                fontName=_font_b if cfg.get("bold") else _font_r,
                fontSize=cfg.get("font_size", 10),
                leading=cfg.get("font_size", 10) + 4,
                textColor=HexColor(cfg.get("text_color", "#0F212B")),
                alignment=TA_LEFT
            )
            
            p = Paragraph(xml, p_style)
            padding = 6
            _, h = p.wrap(width - 2 * padding, 10000)
            
            if cfg['fill'] != "none":
                c.setFillColor(HexColor(cfg['fill']))
                c.rect(x, curr_y - h - 2 * padding, width, h + 2 * padding, fill=1, stroke=0)
            if cfg['stroke'] != "none":
                c.setLineWidth(1)
                c.setStrokeColor(HexColor(cfg['stroke']))
                c.rect(x, curr_y - h - 2 * padding, width, h + 2 * padding, fill=0, stroke=1)
            p.drawOn(c, x + padding, curr_y - h - padding)
            curr_y -= h + 2 * padding + 15
            first_sig = True

        elif kind == "signature":
            if first_sig:
                curr_y -= 15 # Dodatkowy odstęp od treści dokumentu
                first_sig = False
                
            name = item.get("name", "")
            rank = item.get("rank", "")
            
            # Styl dla podpisu (zacieśniony)
            st_sig = ParagraphStyle("sig", parent=styles['para'], leading=12, spaceAfter=0)
            
            xml_name = f"<b>{name}</b>" if rank else name
            p_name = Paragraph(xml_name, st_sig)
            _, h_name = p_name.wrap(width, 100)
            p_name.drawOn(c, x, curr_y - h_name)
            curr_y -= h_name + 0
            
            if rank:
                p_rank = Paragraph(rank, st_sig)
                _, h_rank = p_rank.wrap(width, 100)
                p_rank.drawOn(c, x, curr_y - h_rank)
                curr_y -= h_rank + 0
            
            curr_y -= 1 # Minimalny odstęp między blokami podpisów

        elif kind == "handwritten_signature":
            if first_sig:
                curr_y -= 2 # Zmniejszono z 15 - prawie brak odstępu od 'Approved by'
                first_sig = False
            
            name = item.get("name", "")
            c.setFont(_font_s, 34)
            c.setFillColor(COLOR_TEXT)
            c.drawString(x, curr_y - 25, name) # Zmniejszono z 30
            curr_y -= 32 # Zmniejszono z 42

        elif kind == "image":
            url = item.get("url")
            img_loaded = False
            if url:
                img_data = _fetch_image(url)
                if img_data:
                    try:
                        img = ImageReader(img_data)
                        iw, ih = img.getSize()
                        aspect = ih / iw
                        draw_w = width
                        draw_h = width * aspect
                        c.drawImage(img, x, curr_y - draw_h, width=draw_w, height=draw_h, mask="auto")
                        curr_y -= draw_h + 15
                        img_loaded = True
                    except Exception as e:
                        print(f"[DOCS] Błąd renderowania obrazu ({url}): {e}")

            if not img_loaded:
                placeholder_h = 40
                c.setLineWidth(0.5)
                c.setStrokeColor(HexColor("#BDBDBD"))
                c.setFillColor(HexColor("#F8F8F8"))
                c.rect(x, curr_y - placeholder_h, width, placeholder_h, fill=1, stroke=1)
                short_url = (url[:60] + "…") if url and len(url) > 60 else (url or "brak URL")
                p = Paragraph(f"<i>[ Nie można załadować obrazu: {short_url} ]</i>", styles['para'])
                _, h = p.wrap(width - 10, 1000)
                p.drawOn(c, x + 5, curr_y - placeholder_h / 2 - h / 2)
                curr_y -= placeholder_h + 15

        elif kind == "table":
            headers_list = item.get("headers", [])
            rows = item.get("rows", [])
            if not headers_list: continue
            col_w = width / len(headers_list)
            c.setFillColor(HexColor("#0F212B"))
            c.rect(x, curr_y - 20, width, 20, fill=1, stroke=0)
            c.setFillColor(colors.white)
            c.setFont(_font_b, 10)
            for i, h_text in enumerate(headers_list):
                c.drawString(x + i*col_w + 5, curr_y - 14, str(h_text))
            curr_y -= 20
            c.setFont(_font_r, 9)
            for i, row in enumerate(rows):
                row_h = 18
                if i % 2 == 1:
                    c.setFillColor(HexColor("#F5F5F5"))
                    c.rect(x, curr_y - row_h, width, row_h, fill=1, stroke=0)
                c.setFillColor(HexColor("#0F212B"))
                for j, cell in enumerate(row):
                    if j < len(headers_list):
                        c.drawString(x + j*col_w + 5, curr_y - 13, str(cell))
                curr_y -= row_h
            curr_y -= 10

    if footnotes:
        curr_y -= 10
        c.setLineWidth(0.3)
        c.setStrokeColor(HexColor("#BDBDBD"))
        c.line(x, curr_y, x + 50, curr_y)
        curr_y -= 12
        for i, text in enumerate(footnotes):
            p = Paragraph(f'<font size="8" color="#666666"><sup>{i+1}</sup> {text}</font>', styles['para'])
            _, h = p.wrap(width, 1000)
            p.drawOn(c, x, curr_y - h)
            curr_y -= h + 2

    return curr_y



# ─────────────────────────────────────────────────────────────────────────────
# HELPER – data z sufiksem ordinalnym (Polish/EN style)
# ─────────────────────────────────────────────────────────────────────────────

def _ordinal_date(dt: datetime) -> str:
    months_pl = {
        1: "stycznia", 2: "lutego", 3: "marca", 4: "kwietnia",
        5: "maja", 6: "czerwca", 7: "lipca", 8: "sierpnia",
        9: "września", 10: "października", 11: "listopada", 12: "grudnia"
    }
    return f"{dt.day} {months_pl[dt.month]} {dt.year}"


# ─────────────────────────────────────────────────────────────────────────────
# GENERATOR PDF
# ─────────────────────────────────────────────────────────────────────────────

def _draw_doc_template(c, page_height, data):
    """Pomocnicza funkcja rysująca ramkę, nagłówek i stopkę na każdej stronie."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    BORDER_M = 14.0
    LOGO_SIZE = 62

    # ── RAMKA ─────────────────────────────────────────────────────────────
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_TEXT)
    c.rect(BORDER_M, BORDER_M, PAGE_W - 2*BORDER_M, page_height - 2*BORDER_M, stroke=1, fill=0)

    # ── NAGŁÓWEK ──────────────────────────────────────────────────────────
    logo_x = MARGIN
    logo_y = page_height - MARGIN - LOGO_SIZE
    logo_path = os.path.join(ASSETS_DIR, "logo.png")
    logo_drawn = False
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, logo_x, logo_y, width=LOGO_SIZE, height=LOGO_SIZE, preserveAspectRatio=True, mask="auto")
            logo_drawn = True
        except: pass

    text_x = MARGIN + (LOGO_SIZE + 10 if logo_drawn else 0)
    c.setFillColor(COLOR_TEXT)
    c.setFont(font_b, 17)
    c.drawString(text_x, page_height - MARGIN - 20, data.get("org_name", ORG_NAME))
    c.setFont(font_r, 10)
    c.drawString(text_x, page_height - MARGIN - 35, data.get("org_subtitle", ORG_SUBTITLE))

    doc_type = data.get("doc_type", DOC_TYPE_LABEL)
    c.setFont(font_b, 30)
    line_y = logo_y - 8
    c.drawRightString(PAGE_W - MARGIN, line_y + 8, doc_type)

    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_GREY)
    c.line(MARGIN, line_y, PAGE_W - MARGIN, line_y)

    date_y = line_y - 14
    c.setFillColor(COLOR_TEXT)
    c.setFont(font_b, 10)
    c.drawString(MARGIN, date_y, data.get("date", _ordinal_date(datetime.now())))
    c.drawRightString(PAGE_W - MARGIN, date_y, data.get("doc_number", ""))

    # ── STOPKA ────────────────────────────────────────────────────────────
    foot_sep_y = BORDER_M + 58
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_GREY)
    c.line(MARGIN, foot_sep_y, PAGE_W - MARGIN, foot_sep_y)

    st_footer_links = ParagraphStyle("footer_links", fontName=_font_b, fontSize=9, leading=11, alignment=TA_CENTER, textColor=COLOR_LINK)
    footer_links_xml = (
        f'<link href="https://forum.devgaming.pl/">Dołącz do zespołu</link>  ·  '
        f'<link href="https://forum.devgaming.pl/">LSPD na LifeInvader</link>  ·  '
        f'<link href="https://forum.devgaming.pl/">LSPD na Twitterze</link>'
    )
    p_links = Paragraph(footer_links_xml, st_footer_links)
    _, _ = p_links.wrap(PAGE_W - 2 * MARGIN, 100)
    p_links.drawOn(c, MARGIN, foot_sep_y - 18)

    c.setFont(font_r, 8)
    c.setFillColor(COLOR_TEXT)
    c.drawCentredString(PAGE_W / 2, foot_sep_y - 30, FOOTER_LINE_2)
    c.drawCentredString(PAGE_W / 2, foot_sep_y - 42, FOOTER_LINE_3)

    return date_y - 25 # zwraca y, od którego można zacząć treść

def generate_document_pdf(data: dict) -> io.BytesIO:
    """
    Generuje stylowany dokument PDF (wielostronicowy, dynamiczna wysokość).
    """
    _setup_fonts()
    PAGE_W    = 595.0
    MIN_PAGE_H = 842.0
    MAX_PAGE_H = 1500.0
    MARGIN    = 38.0
    INNER_W   = PAGE_W - 2 * MARGIN
    
    st_para = ParagraphStyle("docs_para", fontName=_font_r, fontSize=11, leading=16, spaceBefore=0, spaceAfter=10, alignment=TA_LEFT, textColor=COLOR_TEXT)
    st_bullet = ParagraphStyle("docs_bullet", fontName=_font_r, fontSize=11, leading=16, spaceBefore=0, spaceAfter=4, leftIndent=18, alignment=TA_LEFT, textColor=COLOR_TEXT)
    st_title = ParagraphStyle("docs_title", fontName=_font_b, fontSize=15, leading=20, spaceBefore=0, spaceAfter=12, alignment=TA_CENTER, textColor=COLOR_TEXT)
    st_subtitle = ParagraphStyle("docs_subtitle", fontName=_font_b, fontSize=12, leading=17, spaceBefore=0, spaceAfter=10, alignment=TA_LEFT, textColor=COLOR_TEXT)
    st_subtitle_centered = ParagraphStyle("docs_subtitle_centered", fontName=_font_b, fontSize=12, leading=17, spaceBefore=0, spaceAfter=10, alignment=TA_CENTER, textColor=COLOR_TEXT)
    
    styles = {
        'para': st_para, 'bullet': st_bullet, 'subtitle': st_subtitle,
        'subtitle_centered': st_subtitle_centered, 'title': st_title,
        'italic': ParagraphStyle("italic", parent=st_para, fontName=_font_i)
    }

    parsed = _parse_content(data.get("content", ""), data)
    
    # Measure total height to decide page size of first page
    temp_buf = io.BytesIO()
    temp_c = canvas.Canvas(temp_buf, pagesize=(PAGE_W, 10000))
    # We must account for title height too
    p_title = Paragraph(_md_inline(data.get("title", "")), st_title)
    _, h_title = p_title.wrap(INNER_W - 4, 10000)
    
    # Calculate content height
    measured_y = render_content_block(temp_c, parsed, MARGIN, 9000, INNER_W, styles)
    content_h = (9000 - measured_y) + h_title + 15 + 100 # +title +buffer
    
    # Calculate PAGE_H
    PAGE_H = max(450, content_h + 120) 
    
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    
    # Draw branding
    y = _draw_doc_template(c, PAGE_H, data)
    
    # Draw title
    p_title.drawOn(c, MARGIN + 2, y - h_title)
    y -= h_title + 15
    
    render_content_block(c, parsed, MARGIN, y, INNER_W, styles, limit_y=100)

    c.save()
    buf.seek(0)
    return buf


def _draw_missing_person_template(c, page_height, data):
    """Pomocnicza funkcja rysująca branding Missing Person."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    BORDER_M = 14.0
    
    # Ramka
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_TEXT)
    c.rect(BORDER_M, BORDER_M, PAGE_W - 2*BORDER_M, page_height - 2*BORDER_M, stroke=1)
    
    # Logo ls.png
    logo_path = os.path.join(ASSETS_DIR, "ls.png")
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, MARGIN, page_height - MARGIN - 100, width=100, height=100, preserveAspectRatio=True, mask="auto")
        except: pass

    # Nagłówek
    c.setFillColor(colors.black)
    c.setFont(font_b, 44)
    c.drawCentredString(PAGE_W / 2 + 40, page_height - MARGIN - 55, "MISSING PERSON")
    
    c.setFont(font_r, 16)
    c.drawCentredString(PAGE_W / 2 + 40, page_height - MARGIN - 80, "Los Santos Police Department")
    c.setFont(font_b, 14)
    c.drawCentredString(PAGE_W / 2 + 40, page_height - MARGIN - 98, "1308 San Andreas Ave. - Los Santos, SA 90012")
    c.setFont(font_b, 14)
    c.drawCentredString(PAGE_W / 2 + 40, page_height - MARGIN - 116, data.get("date", ""))

    c.setFillColor(HexColor("#CE1126"))
    c.setFont(font_b, 16)
    c.drawCentredString(PAGE_W / 2, page_height - 182, data.get("doc_number", ""))

    # Stopka
    footer_y = BORDER_M + 40
    c.setFillColor(colors.black)
    c.setFont(font_r, 12)
    c.drawCentredString(PAGE_W / 2, footer_y + 30, "Jeśli posiadasz jakiekolwiek informacje, prosimy o kontakt")
    c.drawCentredString(PAGE_W / 2, footer_y + 15, "z wydziałem ds. osób zaginionych LSPD pod numerami:")
    c.setFont(font_b, 13)
    c.drawCentredString(PAGE_W / 2, footer_y, "(213) 996-1800 lub 877-527-3247")
    
    return page_height - 190 # start y dla zdjęcia lub treści

def _draw_internal_memo_template(c, page_height, data):
    """Rysuje branding Intradepartamental Correspondence (Internal Memo)."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    BORDER_M = 14.0
    
    # Ramka wokół całej strony
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_TEXT)
    c.rect(BORDER_M, BORDER_M, PAGE_W - 2*BORDER_M, page_height - 2*BORDER_M, stroke=1)
    
    # Tytuł (Wyśrodkowany)
    c.setFillColor(colors.black)
    c.setFont(font_b, 14)
    c.drawCentredString(PAGE_W / 2, page_height - 50, "INTRADEPARTAMENTAL CORRESPONDENCE")
    
    # Data i Numer (Pod nagłówkiem)
    c.setFont(font_r, 11)
    c.drawString(MARGIN, page_height - 85, data.get("date", ""))
    
    # Pola nagłówkowe: TO, FROM, SUBJECT
    y = page_height - 120
    
    def _draw_field(label, value, y_pos):
        c.setFont(font_b, 11)
        c.drawString(MARGIN, y_pos, label)
        c.setFont(font_r, 11)
        # Zawijanie pola jeśli za długie
        xml = _md_inline(value)
        p = Paragraph(xml, ParagraphStyle("memo_meta", fontName=_font_r, fontSize=11, leading=14))
        w_meta = PAGE_W - MARGIN - 120
        _, h = p.wrap(w_meta, 100)
        p.drawOn(c, MARGIN + 80, y_pos - h + 10)
        return max(25, h + 15)

    y -= _draw_field("TO:", data.get("recipient", ""), y)
    y -= _draw_field("FROM:", data.get("sender", ""), y)
    y -= _draw_field("SUBJECT:", data.get("subject", ""), y)
    
    return y - 20 # zwraca punkt startowy treść

def generate_internal_memo_pdf(data: dict) -> io.BytesIO:
    """Generator dla Intradepartamental Correspondence."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MIN_PAGE_H = 842.0
    MARGIN = 38.0
    INNER_W = PAGE_W - 2 * MARGIN
    
    st_memo = ParagraphStyle("memo_text", fontName=_font_r, fontSize=11, leading=16, spaceAfter=10, textColor=COLOR_TEXT)
    styles = {
        'para': st_memo, 'bullet': st_memo, 'subtitle': st_memo,
        'subtitle_centered': st_memo, 'title': st_memo,
        'italic': ParagraphStyle("italic", parent=st_memo, fontName=_font_i)
    }

    parsed = _parse_content(data.get("content", ""), data)
    
    # Measure
    temp_buf = io.BytesIO()
    temp_c = canvas.Canvas(temp_buf, pagesize=(PAGE_W, 20000))
    measured_y = render_content_block(temp_c, parsed, MARGIN, 15000, INNER_W, styles)
    content_h = 15000 - measured_y
    
    # Przeliczenie estymacji samego header'a
    def _est_field_h(value):
        p = Paragraph(_md_inline(value), ParagraphStyle("tmp", fontName=_font_r, fontSize=11, leading=14))
        _, h = p.wrap(PAGE_W - MARGIN - 120, 100)
        return max(25, h + 15)
        
    h_meta = 120 + _est_field_h(data.get("recipient", "")) + _est_field_h(data.get("sender", "")) + _est_field_h(data.get("subject", "")) + 20
    
    total_needed = h_meta + content_h + 100 # header + content + buffer
    PAGE_H = max(400, total_needed)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    
    y = _draw_internal_memo_template(c, PAGE_H, data)
    
    render_content_block(c, parsed, MARGIN, y, INNER_W, styles, limit_y=40)

    c.save()
    buf.seek(0)
    return buf

def _draw_personnel_change_template(c, page_height, data):
    """Rysuje branding Personnel Change (flspd.png + nagłówek w ramce)."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    BORDER_M = 14.0
    INNER_W = PAGE_W - 2 * MARGIN
    
    # Logo flspd.png w nagłówku
    logo_path = os.path.join(ASSETS_DIR, "flspd.png")
    
    # Wyliczamy centrowanie pionowe dla nagłówka
    # head_h = 130, head_y = page_height - head_h - 20
    # Chcemy: Logo (65), Branding (10), Tytuł (14), Approved (11)
    
    curr_y = page_height - 35
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, (PAGE_W - 65)/2, curr_y - 65, width=65, height=65, preserveAspectRatio=True, mask="auto")
            curr_y -= 65
        except: pass

    # Górna ramka (Nagłówek)
    head_h = 130
    head_y = page_height - head_h - 20
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.rect(BORDER_M, head_y, PAGE_W - 2*BORDER_M, head_h, stroke=1)
    
    # Branding - LOS SANTOS POLICE DEPARTMENT
    c.setFillColor(colors.black)
    c.setFont(font_r, 9)
    c.drawCentredString(PAGE_W / 2, curr_y - 12, "LOS SANTOS POLICE DEPARTMENT")
    curr_y -= 15

    # Tytuł
    c.setFont(font_b, 14)
    title = "PERSONNEL CHANGE WITH IMMEDIATE EFFECT"
    c.drawCentredString(PAGE_W / 2, curr_y - 18, title)
    curr_y -= 20
    
    # Approved by (opcjonalne)
    approved = data.get("approved_by", "").strip()
    if approved:
        c.setFont(font_b, 11)
        c.drawCentredString(PAGE_W / 2, curr_y - 12, f"APPROVED BY {approved.upper()}")
        curr_y -= 15
    
    # Główna ramka na treść
    content_y = BORDER_M
    content_h = head_y - BORDER_M - 10
    c.setLineWidth(1)
    c.rect(BORDER_M, content_y, PAGE_W - 2*BORDER_M, content_h, stroke=1)
    
    doc_num = data.get("doc_number", "")
    if doc_num:
        c.setFont(font_b, 10)
        c.drawString(MARGIN, head_y - 25, f"N/REF: {doc_num}")
    
    return head_y - 20

def generate_personnel_change_pdf(data: dict) -> io.BytesIO:
    """Generator dla Personnel Change."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    INNER_W = PAGE_W - 2 * MARGIN
    
    st_label = ParagraphStyle("pc_label", fontName=_font_b, fontSize=11, leading=14, textColor=COLOR_TEXT)
    st_value = ParagraphStyle("pc_value", fontName=_font_r, fontSize=12, leading=16, textColor=COLOR_TEXT)
    
    fields = [
        ("NAME", data.get("name", "")),
        ("RANK", data.get("rank_before", "")),
        ("ASSIGNMENT", data.get("assignment_before", "")),
        ("RANK", data.get("rank_after", "")),
        ("ASSIGNMENT", data.get("assignment_after", "")),
        ("TYPE", data.get("type", ""))
    ]
    
    # Estimate height
    # Header (~130) + Margins (~40) + Fields
    est_h = 240 
    for label, val in fields:
        p_val = Paragraph(f"<b>{label}:</b> {val.upper() if val else ''}", st_value)
        _, h = p_val.wrap(PAGE_W - 2 * MARGIN, 1000)
        est_h += h + 15
    
    # Lower floor to 400 since it's very compact now
    PAGE_H = max(400, est_h)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    
    y_start = _draw_personnel_change_template(c, PAGE_H, data)
    
    # Calculate available height in content box
    # content_y = BORDER_M = 14
    # head_y = PAGE_H - 150
    # content_h = head_y - 14 - 10 = PAGE_H - 174
    BORDER_M = 14.0
    content_y = BORDER_M
    content_h = (PAGE_H - 150) - BORDER_M - 10
    
    fields_to_draw = [
        ("NAME", data.get("name", ""), 20),
        ("RANK", data.get("rank_before", ""), 2),
        ("ASSIGNMENT", data.get("assignment_before", ""), 20),
        ("RANK", data.get("rank_after", ""), 2),
        ("ASSIGNMENT", data.get("assignment_after", ""), 20),
        ("TYPE", data.get("type", ""), 0)
    ]
    
    total_text_h = 0
    for label, val, gap in fields_to_draw:
        p = Paragraph(f"<b>{label}:</b> {val.upper() if val else ''}", st_value)
        w_val = PAGE_W - 2 * MARGIN - 20
        _, h = p.wrap(w_val, 100)
        total_text_h += h + 2 + gap

    # Start Y calculation for perfectly centering vertically
    center_y = content_y + (content_h / 2.0)
    y = center_y + (total_text_h / 2.0)
    
    def draw_inline_field(label, val, y_pos):
        # Format inline: LABEL: VALUE
        p = Paragraph(f"<b>{label}:</b> {val.upper() if val else ''}", st_value)
        w_val = PAGE_W - 2 * MARGIN - 20
        _, h = p.wrap(w_val, 100)
        p.drawOn(c, MARGIN + 10, y_pos - h)
        return h + 2 # Bardzo mały spacing

    for label, val, gap in fields_to_draw:
        y -= draw_inline_field(label, val, y)
        y -= gap

    c.save()
    buf.seek(0)
    return buf

def _draw_disciplinary_action_template(c, page_height, data):
    """Rysuje branding Disciplinary Action (podobnie do Personnel Change)."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    BORDER_M = 14.0
    
    logo_path = os.path.join(ASSETS_DIR, "flspd.png")
    curr_y = page_height - 35
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, (PAGE_W - 65)/2, curr_y - 65, width=65, height=65, preserveAspectRatio=True, mask="auto")
            curr_y -= 65
        except: pass

    c.setFont(font_b, 14)
    # Tytuł dla DA (zawijany jeśli zadługi)
    title = f"DISCIPLINARY ACTION - {data.get('type', 'NOTICE')}".upper()
    
    st_title = ParagraphStyle("da_title", fontName=_font_b, fontSize=14, leading=16, alignment=TA_CENTER, textColor=colors.black)
    p_title = Paragraph(title, st_title)
    w_title = PAGE_W - 2 * MARGIN - 20
    _, h_title = p_title.wrap(w_title, 100)
    
    # Dynamiczny rozmiar ramki nagłówka
    head_h = 110 + h_title # 110 bazowo na loga/tekst departamentu + tytuł
    head_y = page_height - head_h - 20
    
    c.setLineWidth(1)
    c.setStrokeColor(colors.black)
    c.rect(BORDER_M, head_y, PAGE_W - 2*BORDER_M, head_h, stroke=1)
    
    p_title.drawOn(c, MARGIN + 10, head_y + 15)
    
    content_y = BORDER_M
    content_h = head_y - BORDER_M - 10
    c.setLineWidth(1)
    c.rect(BORDER_M, content_y, PAGE_W - 2*BORDER_M, content_h, stroke=1)
    
    doc_num = data.get("doc_number", "")
    if doc_num:
        c.setFont(font_b, 10)
        c.drawString(MARGIN, content_y + content_h - 15, f"N/REF: {doc_num}")
    
    return head_y, content_h

def generate_disciplinary_action_pdf(data: dict) -> io.BytesIO:
    """Generator dla Disciplinary Action."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    
    st_label = ParagraphStyle("da_label", fontName=_font_b, fontSize=11, leading=14, textColor=COLOR_TEXT)
    st_value = ParagraphStyle("da_value", fontName=_font_r, fontSize=12, leading=16, textColor=COLOR_TEXT)
    
    fields_data = [
        ("NAME", data.get("name", "")),
        ("RANK", data.get("rank", "")),
        ("REASON", data.get("reason", "")),
        ("EXPIRES", data.get("expires", "N/A"))
    ]
    
    # Obliczenie wysokości tytułu do estymacji
    title = f"DISCIPLINARY ACTION - {data.get('type', 'NOTICE')}".upper()
    st_title_temp = ParagraphStyle("da_title_tmp", fontName=_font_b, fontSize=14, leading=16, alignment=TA_CENTER)
    p_title_tmp = Paragraph(title, st_title_temp)
    _, h_title = p_title_tmp.wrap(PAGE_W - 2 * MARGIN - 20, 100)
    
    est_h = 110 + h_title + 30 + 30 # head_h + buffers
    for label, val in fields_data:
        p_val = Paragraph(f"<b>{label}:</b> {val.upper() if val else ''}", st_value)
        _, h = p_val.wrap(PAGE_W - 2 * MARGIN, 1000)
        est_h += h + 20
        
    PAGE_H = max(450, est_h)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    
    head_y, calculated_content_h = _draw_disciplinary_action_template(c, PAGE_H, data)
    
    BORDER_M = 14.0
    content_y = BORDER_M
    content_h = calculated_content_h
    
    total_text_h = 0
    fields_to_draw = [
        ("NAME", data.get("name", ""), 20),
        ("RANK", data.get("rank", ""), 20),
        ("REASON", data.get("reason", ""), 20),
        ("EXPIRES", data.get("expires", "N/A") if data.get("expires") else "N/A", 0)
    ]
    
    for label, val, gap in fields_to_draw:
        p = Paragraph(f"<b>{label}:</b> {val.upper() if val else ''}", st_value)
        _, h = p.wrap(PAGE_W - 2 * MARGIN, 1000)
        total_text_h += h + 8 + gap

    # Poczatek rysowania w content_boxie biorac pod uwagę N/REF.
    # N/REF jest rysowane 15px ponizej gornej krawedzi content boxa (czyli content_y + content_h - 15)
    # Wiec realna przestrzen zaczyna sie od content_y do content_y + content_h - 30.
    available_h = content_h - 30 
    center_y = content_y + (available_h / 2.0)
    y = center_y + (total_text_h / 2.0)
    
    def draw_inline_field(label, val, y_pos):
        p = Paragraph(f"<b>{label}:</b> {val.upper() if val else ''}", st_value)
        w_val = PAGE_W - 2 * MARGIN - 20
        _, h = p.wrap(w_val, 100)
        p.drawOn(c, MARGIN + 10, y_pos - h)
        return h + 8

    for label, val, gap in fields_to_draw:
        y -= draw_inline_field(label, val, y)
        y -= gap

    c.save()
    buf.seek(0)
    return buf


def generate_missing_person_pdf(data: dict) -> io.BytesIO:
    """
    Generator dla Missing Person z obsługą wielu stron.
    """
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MIN_PAGE_H = 842.0
    MAX_PAGE_H = 1500.0
    MARGIN = 38.0
    INNER_W = PAGE_W - 2 * MARGIN

    st_missing = ParagraphStyle("missing_desc", fontName=_font_b, fontSize=12, leading=16, alignment=TA_LEFT, textColor=COLOR_TEXT)
    styles = {
        'para': st_missing, 'bullet': st_missing, 'subtitle': st_missing,
        'subtitle_centered': st_missing, 'title': st_missing,
        'italic': ParagraphStyle("italic", parent=st_missing, fontName=_font_bi)
    }

    parsed1 = _parse_content(data.get("appearance", ""), data)
    parsed2 = _parse_content(data.get("missing_details", ""), data)
    parsed = parsed1 + [{"kind": "spacer"}] + parsed2

    # Measure
    temp_buf = io.BytesIO()
    temp_c = canvas.Canvas(temp_buf, pagesize=(PAGE_W, 20000))
    measured_y = render_content_block(temp_c, parsed, MARGIN, 15000, INNER_W, styles)
    text_height = 15000 - measured_y
    
    photo_h = 300 if data.get("photo_url") else 10
    total_needed = 200 + photo_h + 50 + text_height + 100 # header + photo + name + text + footer
    PAGE_H = max(650, total_needed)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    
    y = _draw_missing_person_template(c, PAGE_H, data)
    
    # Photo logic
    photo_url = data.get("photo_url", "")
    if photo_url:
        p_buf = _fetch_image(photo_url)
        if p_buf:
            try:
                img_reader = ImageReader(p_buf)
                box_w, box_h = 260, 260
                box_x, box_y = (PAGE_W - box_w)/2, y - box_h
                iw, ih = img_reader.getSize()
                aspect = iw / ih
                draw_w, draw_h = (box_w, box_w/aspect) if aspect > 1 else (box_h*aspect, box_h)
                c.drawImage(img_reader, box_x + (box_w - draw_w)/2, box_y + (box_h - draw_h)/2, width=draw_w, height=draw_h, mask="auto")
                y -= box_h + 35
            except Exception as e:
                print(f"[DOCS] Błąd renderowania zdjęcia ({photo_url}): {e}")
                y -= 10
        else:
            y -= 10
    else: y -= 10

    # Name and Age
    c.setFillColor(COLOR_TEXT)
    c.setFont(font_b, 22)
    name_age = f"{data.get('name', '')} LAT: {data.get('age', '')}"
    c.drawCentredString(PAGE_W / 2, y, name_age)
    y -= 40

    render_content_block(c, parsed, MARGIN, y, INNER_W, styles, limit_y=120)

    c.save()
    buf.seek(0)
    return buf


def _draw_wanted_template(c, page_height, data, banner_text="COMMUNITY ALERT"):
    """Pomocnicza funkcja rysująca branding WANTED na każdej stronie."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    BORDER_M = 14.0
    INNER_W = PAGE_W - 2 * MARGIN
    
    st_title_red = ParagraphStyle("w_title", fontName=_font_b, fontSize=32, leading=36, alignment=TA_CENTER, textColor=HexColor("#E62325"))
    st_subtitle_red = ParagraphStyle("w_sub", fontName=_font_b, fontSize=38, leading=42, alignment=TA_CENTER, textColor=HexColor("#E62325"))

    # Ramka 
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_GREY)
    c.rect(BORDER_M, BORDER_M, PAGE_W - 2*BORDER_M, page_height - 2*BORDER_M, stroke=1)
    
    # Header logos
    logo_l = os.path.join(ASSETS_DIR, "ls.png")
    logo_r = os.path.join(ASSETS_DIR, "logo.png")
    if os.path.exists(logo_l):
        try:
            c.drawImage(logo_l, MARGIN, page_height - 120, width=80, height=80, preserveAspectRatio=True, mask="auto")
        except: pass
    if os.path.exists(logo_r):
        try:
            c.drawImage(logo_r, PAGE_W - MARGIN - 80, page_height - 120, width=80, height=80, preserveAspectRatio=True, mask="auto")
        except: pass

    # Header texts
    p1 = Paragraph("COMMUNITY ALERT", st_title_red)
    w, _ = p1.wrap(INNER_W, 400)
    p1.drawOn(c, (PAGE_W-w)/2, page_height - 65)
    
    p2 = Paragraph("WANTED", st_subtitle_red)
    w, _ = p2.wrap(INNER_W, 400)
    p2.drawOn(c, (PAGE_W-w)/2, page_height - 105)
    
    c.setFillColor(colors.black)
    c.setFont(font_b, 14)
    c.drawCentredString(PAGE_W/2, page_height - 130, "LOS SANTOS POLICE DEPARTMENT")
    c.setFont(font_r, 9)
    c.drawCentredString(PAGE_W/2, page_height - 142, "OFFICIAL PUBLIC RELEASE OF THE CENTRAL BUREAU CRIME ANALYSIS")

    # Banner
    st_banner = ParagraphStyle("w_ban", fontName=_font_b, fontSize=20, leading=22, alignment=TA_CENTER, textColor=HexColor("#E62325"))
    p_banner = Paragraph(banner_text.upper(), st_banner)
    w_banner, h_banner = p_banner.wrap(INNER_W - 20, 400)
    
    # 35 to bazowa minimalna wysokosc, jeśli wrap da więcej, to rozszerzamy
    banner_rect_h = max(35, h_banner + 16)
    banner_y = page_height - 150 - banner_rect_h # przesuwamy y w dół zależnie od h
    
    c.setFillColor(HexColor("#1A2B3D")) 
    c.rect(MARGIN, banner_y, INNER_W, banner_rect_h, fill=1, stroke=0)
    
    p_banner.drawOn(c, MARGIN + 10, banner_y + (banner_rect_h - h_banner)/2.0 - 2)

    # Stopka
    footer_y = BORDER_M + 30
    c.setLineWidth(1.5)
    c.setStrokeColor(colors.black)
    c.line(MARGIN, footer_y + 35, PAGE_W - MARGIN, footer_y + 35)
    c.setFillColor(colors.black)
    c.setFont(font_r, 9)
    c.drawCentredString(PAGE_W/2, footer_y + 12, "Po godzinach urzędowania prosimy o kontakt z Centrum Operacyjnym Departamentu pod numerem 213-484-6700.")
    c.setFont(font_b, 10)
    c.drawCentredString(PAGE_W/2, footer_y, f"S-ID {data.get('doc_number', 'DR# ????')}")

    return banner_y - 10


def generate_wanted_pdf(data: dict) -> io.BytesIO:
    """
    Generator dla szablonu WANTED (High Risk) - NOWY DESIGN.
    Siatka zdjęć 1-4, branding COMMUNITY ALERT, ciemna belka.
    """
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    
    # ── PARAMETRY BAZOWE ───────────────────────────────────────────────────
    PAGE_W = 595.0
    MIN_PAGE_H = 842.0
    MARGIN = 38.0
    INNER_W = PAGE_W - 2 * MARGIN
    BORDER_M = 14.0
    
    # Stylówka
    st_title_red = ParagraphStyle("w_title", fontName=_font_b, fontSize=32, leading=36, alignment=TA_CENTER, textColor=HexColor("#E62325"))
    st_subtitle_red = ParagraphStyle("w_sub", fontName=_font_b, fontSize=38, leading=42, alignment=TA_CENTER, textColor=HexColor("#E62325"))
    
    st_name_red = ParagraphStyle("w_name", fontName=_font_b, fontSize=36, leading=40, alignment=TA_CENTER, textColor=HexColor("#E62325"))
    st_details = ParagraphStyle("w_det", fontName=_font_b, fontSize=14, leading=18, alignment=TA_CENTER, textColor=colors.black)
    
    st_para = ParagraphStyle("w_para", fontName=_font_r, fontSize=11, leading=14, alignment=TA_CENTER, textColor=colors.black)
    st_warning = ParagraphStyle("w_warn", fontName=_font_b, fontSize=18, leading=22, alignment=TA_CENTER, textColor=HexColor("#E62325"))
    st_para_bold = ParagraphStyle("w_para_b", fontName=_font_b, fontSize=11, leading=14, alignment=TA_CENTER, textColor=colors.black)

    styles = {
        'para': st_para,
        'bullet': st_para,
        'subtitle': st_para_bold,
        'subtitle_centered': st_para_bold,
        'title': st_para_bold,
        'italic': ParagraphStyle("italic", parent=st_para, fontName=_font_i)
    }

    # ── PRZYGOTOWANIE ZDJĘĆ ────────────────────────────────────────────────
    urls = data.get("photo_urls", [])
    images = []
    for url in urls[:4]:
        if not url: continue
        img_data = _fetch_image(url)
        if img_data:
            try:
                images.append(ImageReader(img_data))
            except Exception as e:
                print(f"[DOCS] Błąd dekodowania zdjęcia ({url}): {e}")


    # ── OBLICZANIE WYSOKOŚCI ────────────────────────────────────────────────
    # Dynamicznie obliczamy wysokość tekstu
    paragraphs_all = []
    
    def _wrap(text, style, space=10):
        if not text: return None, 0, 0
        xml = _md_inline(text)
        p = Paragraph(xml, style)
        _, h = p.wrap(INNER_W, 2000)
        return p, h, space

    parsed_main = _parse_content(data.get("reasons", ""), data)
    
    # Measure
    temp_buf = io.BytesIO()
    temp_c = canvas.Canvas(temp_buf, pagesize=(PAGE_W, 20000))
    measured_y = render_content_block(temp_c, parsed_main, MARGIN, 15000, INNER_W, styles)
    h_reasons = 15000 - measured_y
    
    alert_text = data.get("alert_type", "NAPAŚĆ SEKSUALNA – NAKAZ W TOKU")
    p_banner_tmp = Paragraph(alert_text.upper(), ParagraphStyle("tmp", fontName=_font_b, fontSize=20, leading=22))
    _, h_banner_tmp = p_banner_tmp.wrap(INNER_W - 20, 400)
    
    # Calculate name wrap height
    p_name_tmp = Paragraph(_md_inline(data.get("name", "").upper()), st_name_red)
    _, h_name_tmp = p_name_tmp.wrap(INNER_W, 2000)
    
    # Calculate details wrap height
    p_det_tmp = Paragraph(_md_inline(data.get("details_line", "")), st_details)
    _, h_det_tmp = p_det_tmp.wrap(INNER_W, 2000)
    
    h_meta = h_name_tmp + 10 + h_det_tmp + 25 # dynamic name + details + paddings
    h_warn = 60
    
    # header(200) + pics(290) + footer(100) = 590
    total_needed = 200 + h_banner_tmp + 290 + h_meta + h_reasons + h_warn + 150 
    PAGE_H = max(800.0, total_needed)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    
    y = _draw_wanted_template(c, PAGE_H, data, banner_text=alert_text)

    # Draw Grid
    num_imgs = len(images)
    grid_h = 270
    top_y = y - 10 
    actual_grid_height = 0
    
    if num_imgs == 1:
        box_w = 320
        c.drawImage(images[0], (PAGE_W-box_w)/2, top_y - grid_h, width=box_w, height=grid_h, preserveAspectRatio=True, anchor='c')
        actual_grid_height = grid_h
    elif num_imgs >= 2:
        gap_x, gap_y = 10, 10
        row_h = (grid_h - gap_y) / 2 if num_imgs > 2 else grid_h
        img_data = []
        for img in images[:4]:
            iw, ih = img.getSize()
            aspect = iw / ih
            draw_w = min(240, row_h * aspect)
            img_data.append((img, draw_w))
        rows_data = [img_data] if num_imgs == 2 else ([img_data[:2], [img_data[2]]] if num_imgs == 3 else [img_data[:2], img_data[2:4]])
        curr_y = top_y
        for row in rows_data:
            total_row_w = sum(d[1] for d in row) + (gap_x * (len(row) - 1))
            x_off = (PAGE_W - total_row_w) / 2
            for img, dw in row:
                c.drawImage(img, x_off, curr_y - row_h, width=dw, height=row_h, mask="auto")
                x_off += dw + gap_x
            curr_y -= (row_h + gap_y)
        actual_grid_height = top_y - curr_y

    y = top_y - actual_grid_height - 15
    
    # Name and Details
    def _draw_centered_p(text, style, y_pos):
        xml = _md_inline(text)
        p = Paragraph(xml, style)
        _, h = p.wrap(INNER_W, 2000)
        p.drawOn(c, MARGIN, y_pos - h)
        return h

    h_n = _draw_centered_p(data.get("name", "").upper(), st_name_red, y)
    y -= h_n + 10
    h_d = _draw_centered_p(data.get("details_line", ""), st_details, y)
    y -= h_d + 25

    # Warning
    warning_text = "OSOBA MOŻE BYĆ UZBROJONA I NIEBEZPIECZNA. NIE ZBLIŻAJ SIĘ, DZWOŃ POD 911."
    # We need to calculate where the content ended - rendering limit_y to 100 to keep it clear of the footer line
    y_final = render_content_block(c, parsed_main, MARGIN, y, INNER_W, styles, limit_y=100)
    _draw_centered_p(warning_text, st_warning, y_final - 20)

    c.save()
    buf.seek(0)
    return buf


def generate_field_interview_pdf(data: dict) -> io.BytesIO:
    """Generator dla Field Interview Card."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    return io.BytesIO()


def _draw_official_letter_template(c, page_height, data):
    """Rysuje branding Official Letter (jak na zdjęciu - pismo urzędowe z Chief of Police)."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    BORDER_M = 14.0

    # Ramka
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_TEXT)
    c.rect(BORDER_M, BORDER_M, PAGE_W - 2*BORDER_M, page_height - 2*BORDER_M, stroke=1, fill=0)

    # ── NAGŁÓWEK ──────────────────────────────────────────────────────────
    HEADER_H = 110
    header_top = page_height - BORDER_M
    header_bot = header_top - HEADER_H

    # Linia pod nagłówkiem
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_TEXT)
    c.line(BORDER_M, header_bot, PAGE_W - BORDER_M, header_bot)

    # Logo flspd.png - wyśrodkowane w nagłówku
    logo_path = os.path.join(ASSETS_DIR, "flspd.png")
    LOGO_SIZE = 70
    logo_x = (PAGE_W - LOGO_SIZE) / 2
    logo_y = header_bot + (HEADER_H - LOGO_SIZE) / 2
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, logo_x, logo_y, width=LOGO_SIZE, height=LOGO_SIZE,
                        preserveAspectRatio=True, mask="auto")
        except: pass

    # Tytuł departamentu - u góry wyśrodkowany
    c.setFillColor(colors.black)
    c.setFont(font_b, 13)
    c.drawCentredString(PAGE_W / 2, header_top - 20, "LOS SANTOS POLICE DEPARTMENT")

    # Lewa kolumna: Chief of Police
    chief_name = data.get("chief_name", "GREGORY EDWARDS")
    c.setFont(font_b, 10)
    c.drawString(MARGIN, header_bot + 55, chief_name)
    c.setFont(font_r, 9)
    c.drawString(MARGIN, header_bot + 42, "Chief of Police")

    # Prawa kolumna: adres
    addr_lines = [
        "P.O. Box 30412",
        "Los Santos Police Department",
        "Los Santos, San Andreas 90030",
        "206 Station Avenue",
    ]
    c.setFont(font_r, 9)
    for i, line in enumerate(addr_lines):
        c.drawRightString(PAGE_W - MARGIN, header_bot + 55 - i * 11, line)

    # ── STOPKA ────────────────────────────────────────────────────────────
    footer_y = BORDER_M + 40
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_TEXT)
    c.line(BORDER_M, footer_y, PAGE_W - BORDER_M, footer_y)

    c.setFont(font_b, 8)
    c.setFillColor(COLOR_TEXT)
    c.drawCentredString(PAGE_W / 2, footer_y - 12, "AN EQUAL OPPORTUNITY EMPLOYER")

    st_link = ParagraphStyle("ol_link", fontName=font_r, fontSize=8, leading=10,
                              alignment=TA_CENTER, textColor=COLOR_LINK)
    p_links = Paragraph(
        '<link href="http://www.LSPDonline.org">www.LSPDonline.org</link>    '
        '<link href="http://www.joinLSPD.com">www.joinLSPD.com</link>',
        st_link
    )
    _, _ = p_links.wrap(PAGE_W - 2 * MARGIN, 50)
    p_links.drawOn(c, MARGIN, footer_y - 26)

    # Zwraca y, od którego zaczyna się treść
    return header_bot - 10


def generate_official_letter_pdf(data: dict) -> io.BytesIO:
    """Generator dla Official Letter (pismo departamentowe)."""
    _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    INNER_W = PAGE_W - 2 * MARGIN

    st_para = ParagraphStyle("ol_para", fontName=_font_r, fontSize=11, leading=16,
                              spaceAfter=10, alignment=TA_JUSTIFY, textColor=COLOR_TEXT)
    st_bullet = ParagraphStyle("ol_bullet", fontName=_font_r, fontSize=11, leading=16,
                                spaceAfter=4, leftIndent=18, textColor=COLOR_TEXT)
    st_subtitle = ParagraphStyle("ol_sub", fontName=_font_b, fontSize=12, leading=17,
                                  spaceAfter=10, textColor=COLOR_TEXT)
    st_subtitle_centered = ParagraphStyle("ol_subc", fontName=_font_b, fontSize=12,
                                           leading=17, spaceAfter=10, alignment=TA_CENTER,
                                           textColor=COLOR_TEXT)
    styles = {
        'para': st_para, 'bullet': st_bullet, 'subtitle': st_subtitle,
        'subtitle_centered': st_subtitle_centered,
        'title': ParagraphStyle("ol_title", fontName=_font_b, fontSize=13, leading=18,
                                 spaceAfter=12, alignment=TA_CENTER, textColor=COLOR_TEXT),
        'italic': ParagraphStyle("ol_italic", parent=st_para, fontName=_font_i)
    }

    # Header height estimation: 110 header + 10 gap + date_block + content + footer(~60)
    DATE_BLOCK_H = 60   # data + odstęp
    FOOTER_H = 60
    HEADER_H = 120

    full_content = data.get("content", "")
    parsed = _parse_content(full_content, data)

    # Measure content height
    temp_buf = io.BytesIO()
    temp_c = canvas.Canvas(temp_buf, pagesize=(PAGE_W, 20000))
    measured_y = render_content_block(temp_c, parsed, MARGIN, 15000, INNER_W, styles)
    content_h = 15000 - measured_y

    PAGE_H = max(500, HEADER_H + DATE_BLOCK_H + content_h + FOOTER_H + 100)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))

    start_y = _draw_official_letter_template(c, PAGE_H, data)

    # Data i adresat
    from datetime import timedelta
    now = datetime.now() + timedelta(hours=1)
    date_str = data.get("date", _ordinal_date(now))

    c.setFont(_font_r, 11)
    c.setFillColor(COLOR_TEXT)
    curr_y = start_y - 15
    c.drawString(MARGIN, curr_y, date_str)
    curr_y -= 30

    # Adresat (To)
    recipient = data.get("recipient", "").strip()
    if recipient:
        p_rec = Paragraph(f"Do {_md_inline(recipient)},", st_para)
        _, h_rec = p_rec.wrap(INNER_W, 10000)
        p_rec.drawOn(c, MARGIN, curr_y - h_rec)
        curr_y -= h_rec + 15

    render_content_block(c, parsed, MARGIN, curr_y, INNER_W, styles, limit_y=60)

    c.save()
    buf.seek(0)
    return buf


def _draw_division_letter_template(c, page_height, data):
    """Rysuje branding Division Letter: dwa loga + nagłówek + pola TO/FROM/SUBJECT."""
    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    BORDER_M = 14.0

    # ── RAMKA ──────────────────────────────────────────────────────────────
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_TEXT)
    c.rect(BORDER_M, BORDER_M, PAGE_W - 2*BORDER_M, page_height - 2*BORDER_M, stroke=1, fill=0)

    # ── LOGA (wyśrodkowane, obok siebie) ───────────────────────────────────
    LOGO_SIZE = 72
    logo_gap = 5  # zbliżone do siebie
    total_logos_w = LOGO_SIZE * 2 + logo_gap
    logos_x_start = (PAGE_W - total_logos_w) / 2
    logo_y = page_height - MARGIN - LOGO_SIZE

    # Lewe logo: zawsze l-lspd.png
    left_logo_path = os.path.join(ASSETS_DIR, "l-lspd.png")
    if os.path.exists(left_logo_path):
        try:
            c.drawImage(left_logo_path, logos_x_start, logo_y,
                        width=LOGO_SIZE, height=LOGO_SIZE,
                        preserveAspectRatio=True, mask="auto")
        except: pass

    # Prawe logo: plik dywizji
    division_logo_file = data.get("division_logo", "")
    if division_logo_file:
        right_logo_path = os.path.join(ASSETS_DIR, division_logo_file)
        if os.path.exists(right_logo_path):
            try:
                c.drawImage(right_logo_path, logos_x_start + LOGO_SIZE + logo_gap, logo_y,
                            width=LOGO_SIZE, height=LOGO_SIZE,
                            preserveAspectRatio=True, mask="auto")
            except: pass

    # ── NAGŁÓWEK TEKST ─────────────────────────────────────────────────────
    text_top_y = logo_y - 35  # Zwiększony odstęp od logotypów (było -8)
    c.setFillColor(colors.black)
    c.setFont(font_b, 13)
    c.drawCentredString(PAGE_W / 2, text_top_y, "Los Santos Police Department")
    c.setFont(font_b, 11)
    division_name = data.get("division_name", "").upper()
    c.drawCentredString(PAGE_W / 2, text_top_y - 16, division_name)

    # Linia po nagłówku
    sep_y = text_top_y - 28
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_GREY)
    c.line(MARGIN, sep_y, PAGE_W - MARGIN, sep_y)

    # ── DATA + NUMER ───────────────────────────────────────────────────────
    date_y = sep_y - 15
    c.setFillColor(COLOR_TEXT)
    c.setFont(font_r, 10)
    c.drawString(MARGIN, date_y, data.get("date", ""))
    c.setFont(font_b, 10)
    c.drawRightString(PAGE_W - MARGIN, date_y, data.get("doc_number", ""))

    # ── POLA TO / FROM / SUBJECT ───────────────────────────────────────────
    y = date_y - 25

    def _draw_field(label, value, y_pos):
        c.setFont(font_b, 11)
        c.setFillColor(COLOR_TEXT)
        c.drawString(MARGIN, y_pos, label)
        xml = _md_inline(value)
        p = Paragraph(xml, ParagraphStyle(
            "dl_meta", fontName=_font_r, fontSize=11, leading=14,
            textColor=COLOR_TEXT
        ))
        w_meta = PAGE_W - MARGIN - 120
        _, h = p.wrap(w_meta, 200)
        p.drawOn(c, MARGIN + 80, y_pos - h + 10)
        return max(25, h + 10)

    y -= _draw_field("To:", data.get("recipient", ""), y)
    y -= _draw_field("From:", data.get("sender", ""), y)
    y -= _draw_field("Subject:", data.get("subject", ""), y)

    # Linia po polach nagłówka
    c.setLineWidth(0.5)
    c.setStrokeColor(COLOR_GREY)
    c.line(MARGIN, y - 5, PAGE_W - MARGIN, y - 5)

    # ── STOPKA ─────────────────────────────────────────────────────────────
    c.setFont(font_r, 9)
    c.setFillColor(COLOR_TEXT)
    footer_addr = data.get("footer_address", "7105 Hawick, Elgin Avenue")
    c.drawCentredString(PAGE_W / 2, BORDER_M + 12, footer_addr)

    return y - 20  # punkt startowy treści


def generate_division_letter_pdf(data: dict) -> io.BytesIO:
    """Generator dla Division Letter (pismo dywizji) z dwoma logami w nagłówku."""
    
    div_key = data.get("division_key")
    if div_key and "division_name" not in data:
        div_info = DIVISIONS.get(div_key)
        if div_info:
            data["division_name"], data["division_logo"] = div_info

    font_r, font_b, font_i, font_bi, font_s = _setup_fonts()
    PAGE_W = 595.0
    MARGIN = 38.0
    INNER_W = PAGE_W - 2 * MARGIN

    st_para = ParagraphStyle("dl_para", fontName=_font_r, fontSize=11, leading=16,
                              spaceAfter=10, alignment=TA_JUSTIFY, textColor=COLOR_TEXT)
    st_bullet = ParagraphStyle("dl_bullet", fontName=_font_r, fontSize=11, leading=16,
                                spaceAfter=4, leftIndent=18, textColor=COLOR_TEXT)
    st_subtitle = ParagraphStyle("dl_sub", fontName=_font_b, fontSize=12, leading=17,
                                  spaceAfter=10, textColor=COLOR_TEXT)
    st_subtitle_centered = ParagraphStyle("dl_subc", fontName=_font_b, fontSize=12,
                                           leading=17, spaceAfter=10, alignment=TA_CENTER,
                                           textColor=COLOR_TEXT)
    styles = {
        'para': st_para, 'bullet': st_bullet, 'subtitle': st_subtitle,
        'subtitle_centered': st_subtitle_centered,
        'title': ParagraphStyle("dl_title", fontName=_font_b, fontSize=13, leading=18,
                                 spaceAfter=12, alignment=TA_CENTER, textColor=COLOR_TEXT),
        'italic': ParagraphStyle("dl_italic", parent=st_para, fontName=_font_i)
    }

    parsed = _parse_content(data.get("content", ""), data)

    # Measure content height
    temp_buf = io.BytesIO()
    temp_c = canvas.Canvas(temp_buf, pagesize=(PAGE_W, 20000))
    measured_y = render_content_block(temp_c, parsed, MARGIN, 15000, INNER_W, styles)
    content_h = 15000 - measured_y

    # Header estimate: logo(77) + tekst(35) + linia(10) + data(20) + 3 pola (~80) + linia(15) = ~237
    HEADER_H = 260
    FOOTER_H  = 30
    PAGE_H = max(500, HEADER_H + content_h + FOOTER_H + 80)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))

    y = _draw_division_letter_template(c, PAGE_H, data)
    render_content_block(c, parsed, MARGIN, y, INNER_W, styles, limit_y=40)

    c.save()
    buf.seek(0)
    return buf


def generate_tweet_pdf(data: dict) -> io.BytesIO:

    """Zaktualizowany generator dla Tweeta LSPD — naprawa nakładania się elementów."""
    _setup_fonts()
    PAGE_W = 600.0  
    MARGIN = 30.0
    INNER_W = PAGE_W - 2 * MARGIN
    CONTENT_X = MARGIN + 65  
    CONTENT_W = PAGE_W - CONTENT_X - MARGIN

    st_content = ParagraphStyle("tw_content", fontName=_font_tw_r, 
                                 fontSize=16, leading=22,
                                 textColor=COLOR_TW_TEXT, alignment=TA_LEFT)
    styles = {'para': st_content}

    # Przygotowanie contentu
    full_content = data.get("content", "")
    parsed = _parse_content(full_content, data)

    # Obliczenie wysokości treści
    temp_buf = io.BytesIO()
    temp_c = canvas.Canvas(temp_buf, pagesize=(PAGE_W, 10000))
    measured_y = render_content_block(temp_c, parsed, CONTENT_X, 9000, CONTENT_W, styles)
    content_h = 9000 - measured_y

    # Obliczenie wysokości zdjęcia
    photo_h = 0
    photo_url = data.get("photo_url", "").strip()
    if photo_url:
        photo_h = 320

    # Kalkulacja wysokości strony dopasowana do zacieśnionego układu
    # Header area (~50) + Content area + Photo? + Stats area (~40) + Margins
    photo_part = (photo_h + 10) if photo_h else 5
    total_h = MARGIN + 50 + content_h + photo_part + 40 + MARGIN
    PAGE_H = math.ceil(total_h)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PAGE_W, PAGE_H))
    
    # Czarne tło z zapasem (bleed)
    c.setFillColor(COLOR_TW_BG)
    c.rect(-10, -10, PAGE_W + 20, PAGE_H + 20, stroke=0, fill=1)

    curr_y = PAGE_H - MARGIN

    # 1. AWATAR (Środek na Y - 25 względem góry treści)
    pfp_path = os.path.join(ASSETS_DIR, "lspdtwitterprofile.png")
    if os.path.exists(pfp_path):
        try:
            c.saveState()
            p = c.beginPath()
            p.circle(MARGIN + 25, curr_y - 25, 25)
            c.clipPath(p, stroke=0)
            c.drawImage(pfp_path, MARGIN, curr_y - 50, width=50, height=50, mask='auto', preserveAspectRatio=True)
            c.restoreState()
        except: pass
    
    # 2. HEADER
    header_y = curr_y - 32 
    c.setFont(_font_tw_b, 16)
    c.setFillColor(COLOR_TW_TEXT)
    name_str = "LSPD HQ"
    name_w = c.stringWidth(name_str, _font_tw_b, 16)
    c.drawString(CONTENT_X, header_y, name_str)
    
    verified_path = os.path.join(ASSETS_DIR, "verifiedicon.png")
    if os.path.exists(verified_path):
        try:
            c.drawImage(verified_path, CONTENT_X + name_w + 5, header_y - 1, width=19, height=19, mask='auto', preserveAspectRatio=True)
        except: pass
    
    c.setFont(_font_tw_r, 15)
    c.setFillColor(COLOR_TW_SUB)
    handle_str = "@lspdhq  •  " + data.get("tw_date", "16 Marca")
    c.drawString(CONTENT_X + name_w + 30, header_y, handle_str)
    
    c.setFont(_font_tw_r, 16)
    c.drawRightString(PAGE_W - MARGIN, header_y + 4, "...")

    # 3. TREŚĆ
    curr_y = header_y - 12
    final_y = render_content_block(c, parsed, CONTENT_X, curr_y, CONTENT_W, styles)
    curr_y = final_y - 12  # Bezpieczny odstęp od końca tekstu (naprawa nakładania się)

    # 4. ZDJĘCIE
    if photo_url:
        try:
            img_buf = _fetch_image(photo_url)
            if img_buf:
                img_reader = ImageReader(img_buf)
                c.saveState()
                r = 16
                path = c.beginPath()
                path.roundRect(CONTENT_X, curr_y - photo_h, CONTENT_W, photo_h, r)
                c.clipPath(path, stroke=0)
                c.drawImage(img_reader, CONTENT_X, curr_y - photo_h, width=CONTENT_W, height=photo_h, preserveAspectRatio=True, anchor='c')
                c.restoreState()
                curr_y -= photo_h + 10
        except Exception as e:
            print(f"[DOCS] Tweet photo err: {e}")
            curr_y -= 5

    # 5. STATYSTYKI
    stats_y = curr_y - 18 # Pozycja ikon statystyk pod tekstem/zdjęciem
    def fmt(n): return f"{n/1000:.1f}k" if n >= 1000 else str(n)
    
    v = random.randint(1000, 7000)
    l = random.randint(100, 990)
    r = random.randint(5, 30)
    m = random.randint(2, 90)
    
    stats_data = [
        ("commenticon.png", str(m)),
        ("retweeticon.png", str(r)),
        ("likeicon.png", str(l)),
        ("viewsicon.png", fmt(v)),
        ("downloadicon.png", "")
    ]
    
    c.setFont(_font_tw_r, 13)
    c.setFillColor(COLOR_TW_SUB)
    icon_sz = 20
    spacing = CONTENT_W / (len(stats_data) - 0.5)
    
    for i, (icon, val) in enumerate(stats_data):
        icon_path = os.path.join(ASSETS_DIR, icon)
        ix = CONTENT_X + i * spacing
        if os.path.exists(icon_path):
            try:
                c.drawImage(icon_path, ix, stats_y, width=icon_sz, height=icon_sz, mask='auto', preserveAspectRatio=True)
            except: pass
        if val:
            c.drawString(ix + 28, stats_y + 5, val)

    c.save()
    buf.seek(0)
    return buf

# ─────────────────────────────────────────────────────────────────────────────
# KONWERSJA PDF → PNG
# ─────────────────────────────────────────────────────────────────────────────

async def _pdf_to_png(pdf_buf: io.BytesIO) -> Optional[io.BytesIO]:
    """Konwertuje wszystkie strony PDF na jeden wysoki obraz PNG (pionowy stos)."""
    try:
        import fitz  # PyMuPDF
        from PIL import Image
        
        pdf_buf.seek(0)
        doc = fitz.open(stream=pdf_buf.read(), filetype="pdf")
        if doc.page_count == 0:
            return None
            
        images = []
        total_h = 0
        max_w = 0
        
        for i in range(doc.page_count):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=150)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
            total_h += pix.height
            if pix.width > max_w:
                max_w = pix.width
                
        # Składanie w jeden obraz
        # Używamy czarnego tła (0, 0, 0) zamiast białego, aby uniknąć szarych linii w Dark Mode
        combined = Image.new("RGB", (max_w, total_h), (0, 0, 0))
        y_off = 0
        for img in images:
            combined.paste(img, (0, y_off))
            y_off += img.height
            
        out = io.BytesIO()
        combined.save(out, format="PNG")
        out.seek(0)
        return out
        
    except ImportError:
        print("[DOCS] Brak biblioteki pymupdf lub pillow.")
    except Exception as e:
        print(f"[DOCS] Błąd konwersji PNG: {e}")
    return None


from xhtml2pdf import pisa
def generate_html_pdf(html_content):
    """Konwertuje HTML (z CSS) na PDF buffer."""
    result = io.BytesIO()
    # Dodajemy podstawowe kodowanie i czcionki jeśli potrzeba
    # xhtml2pdf obsługuje style wewnątrz <style> lub atrybuty style
    pisa_status = pisa.CreatePDF(html_content, dest=result, encoding='utf-8')
    
    if pisa_status.err:
        print(f"[DOCS] Błąd xhtml2pdf: {pisa_status.err}")
        return None
        
    result.seek(0)
    return result

# ─────────────────────────────────────────────────────────────────────────────
