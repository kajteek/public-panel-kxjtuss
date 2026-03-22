from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import io
import traceback
import sys
import pdf_generator
import fitz
from PIL import Image
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure Database connection
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    try:
        engine = create_engine(DATABASE_URL)
        db_session = scoped_session(sessionmaker(bind=engine))
        # Testing connection
        with engine.connect() as conn:
            print("[DB] Successfully connected to PostgeSQL database via SQLAlchemy.")
    except SQLAlchemyError as e:
        print(f"[DB ERROR]: Database connection error: {e}")
        db_session = None
else:
    print("WARNING: DATABASE_URL not set in environment.")

app = Flask(__name__)
CORS(app)

def pdf_to_png(pdf_buf: io.BytesIO) -> io.BytesIO:
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
            
    combined = Image.new("RGB", (max_w, total_h), (0, 0, 0)) # black background
    y_off = 0
    for img in images:
        combined.paste(img, (0, y_off))
        y_off += img.height
        
    out = io.BytesIO()
    combined.save(out, format="PNG")
    out.seek(0)
    return out


@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    template = data.get("template", "official_statement")
    format_type = data.get("format", "pdf")
    
    # Inject ordinal_date fallback if needed
    from datetime import datetime
    now = datetime.now()
    def _ordinal_date(dt):
        suffix = "th" if 11 <= dt.day <= 13 else {1:"st", 2:"nd", 3:"rd"}.get(dt.day % 10, "th")
        return dt.strftime(f"%B {dt.day}{suffix}, %Y")
    data["date"] = data.get("date", _ordinal_date(now))
    
    # Setup doc number
    doc_number = data.get("doc_number", "NR-000")
    if not doc_number or doc_number == "NR-000":
        if template == "missing_person":
            data["doc_number"] = "DR# 2026021"
        elif template == "wanted":
            data["doc_number"] = "HR-26012"
        elif template == "personnel_change":
            data["doc_number"] = "PC-26006"
        elif template == "disciplinary_action":
            data["doc_number"] = "DA-26002"
        elif template == "official_letter":
            data["doc_number"] = "OL-26002"
        elif template == "division_letter":
            data["doc_number"] = "DL-26002-js"
        elif template == "tweet":
            data["doc_number"] = "TW-26002"
        else:
            data["doc_number"] = "NR003-3js"

    try:
        pdf_buf = None
        if data.get("type") == "mdc":
            html_content = data.get("html", "<h1>No Content</h1>")
            pdf_buf = pdf_generator.generate_html_pdf(html_content)
        elif template == "missing_person":
            pdf_buf = pdf_generator.generate_missing_person_pdf(data)
        elif template == "wanted":
            pdf_buf = pdf_generator.generate_wanted_pdf(data)
        elif template == "internal_memo":
            pdf_buf = pdf_generator.generate_internal_memo_pdf(data)
        elif template == "personnel_change":
            pdf_buf = pdf_generator.generate_personnel_change_pdf(data)
        elif template == "disciplinary_action":
            pdf_buf = pdf_generator.generate_disciplinary_action_pdf(data)
        elif template == "official_letter":
            pdf_buf = pdf_generator.generate_official_letter_pdf(data)
        elif template == "division_letter":
            pdf_buf = pdf_generator.generate_division_letter_pdf(data)
        elif template == "tweet":
            pdf_buf = pdf_generator.generate_tweet_pdf(data)
        else:
            # Fallback for News Release / Official Statement
            # Make sure missing data is filled
            data["org_name"] = data.get("org_name", "Los Santos Police Department")
            data["org_subtitle"] = data.get("org_subtitle", "Los Santos, San Andreas")
            data["doc_type"] = data.get("doc_type", "News Release")
            pdf_buf = pdf_generator.generate_document_pdf(data)

        if not pdf_buf:
            return jsonify({"error": "Failed to generate PDF"}), 500
            
        if format_type == "png":
            png_buf = pdf_to_png(pdf_buf)
            if not png_buf:
                return jsonify({"error": "Failed to convert PDF to PNG"}), 500
            return send_file(
                png_buf,
                as_attachment=True if request.args.get('download') else False,
                download_name=f"document_{template}.png",
                mimetype='image/png'
            )
        else:
            pdf_buf.seek(0)
            return send_file(
                pdf_buf, 
                as_attachment=True if request.args.get('download') else False, 
                download_name=f"document_{template}.pdf",
                mimetype='application/pdf'
            )

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/legal-search', methods=['POST'])
def legal_search():
    data = request.json
    query = data.get("query", "")
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Load Penal Code
        penal_code_path = os.path.join(os.path.dirname(__file__), '..', '..', 'client', 'data', 'devg-data', 'devg_penal_code.json')
        with open(penal_code_path, 'r', encoding='utf-8') as f:
            penal_code_data = json.load(f)

        # Load Caselaws
        caselaws_path = os.path.join(os.path.dirname(__file__), '..', '..', 'client', 'data', 'caselaws.json')
        with open(caselaws_path, 'r', encoding='utf-8') as f:
            caselaws_data = json.load(f)

        # Prepare Prompt
        model = genai.GenerativeModel('gemini-flash-latest')
        
        prompt = f"""You are a helpful legal assistant for Law Enforcement Officers in San Andreas.
The user will provide a question related to penal code charges or caselaw.

1. Review the provided San Andreas Penal Code data to find up to five relevant charges that directly answer the user's query.
2. Review the provided local caselaw data to determine the single most relevant case, if any.
3. Produce a concise explanation (in Polish) that ties together the penal code citations and/or caselaw you found.
4. IMPORTANT LINGUISTIC RULES:
   - NEVER use the word "artykuł" or "art.". Instead, refer to laws as "punkt P.C [ID] [Nazwa]".
   - ALWAYS wrap the entire law reference in square brackets with a "PC: " prefix.
   - Example: "narusza przede wszystkim [PC: punkt P.C 137 Ucieczka przed organami ścigania]".
   - NEVER use the word "policja". Use "departament" instead.
   - NEVER use the word "funkcjonariusz". Use "oficer" instead.
5. If the user would benefit from additional precedent, suggest similar US Supreme Court cases (like from Oyez).

SAN ANDREAS PENAL CODE (subset relevant to mapping):
{json.dumps(list(penal_code_data.values())[:100], indent=2)} # Truncated for token limit in testing, ideally we'd search first

LOCAL CASELAWS:
{json.dumps(caselaws_data.get('caselaws', []), indent=2)}

User Query: {query}

Your response must be a JSON object with the following structure:
{{
  "explanation": "Brief summary",
  "penal_code_results": [
    {{ "id": "101", "name": "Charge Name", "type": "F/M/I", "definition": "..." }}
  ],
  "caselaw_result": {{ "case": "Name", "summary": "...", "implication": "...", "year": "..." }},
  "oyez_cases": [
    {{ "name": "Case Name", "href": "url", "summary": "Krótki opis sprawy i precedensu w języku polskim" }}
  ]
}}
Do NOT include any markdown formatting like ```json ... ```, just the raw JSON object.
"""

        response = model.generate_content(prompt)
        # Attempt to parse JSON from response
        try:
            result = json.loads(response.text.strip())
            return jsonify(result)
        except json.JSONDecodeError:
            # Fallback if AI included markdown or extra text
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return jsonify(json.loads(text))

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if 'db_session' in globals() and db_session is not None:
            db_session.remove()

    # Patch pdf_generator to have _ordinal_date

    from datetime import datetime
    def _ordinal_date(dt):
        suffix = "th" if 11 <= dt.day <= 13 else {1:"st", 2:"nd", 3:"rd"}.get(dt.day % 10, "th")
        return dt.strftime(f"%B {dt.day}{suffix}, %Y")
    pdf_generator._ordinal_date = _ordinal_date
    app.run(debug=True, port=5000)
