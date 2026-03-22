import os
import sys
import io
from datetime import datetime

# Add current dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pdf_generator

def verify():
    print("--- BACKEND ASSET VERIFICATION ---")
    print(f"FRONTEND_ASSETS: {pdf_generator.FRONTEND_ASSETS}")
    print(f"BACKEND_DATA: {pdf_generator.BACKEND_DATA}\n")
    
    # Check core assets
    required_assets = [
        "logo.png", "ls.png", "flspd.png", "l-lspd.png",
        "podpis.ttf", "segoeuibold.ttf", "segoeuiregular.ttf"
    ]
    
    missing = []
    for asset in required_assets:
        path = os.path.join(pdf_generator.FRONTEND_ASSETS, asset)
        exists = os.path.exists(path)
        print(f"[{'OK' if exists else '!!'}] {asset}: {path if not exists else 'Found'}")
        if not exists: missing.append(asset)
        
    if missing:
        print("\nERROR: Missing critical assets!")
        return False
        
    print("\nAttempting to generate a dummy document...")
    try:
        data = {
            "template": "official_statement",
            "org_name": "VERIFICATION LSPD",
            "org_subtitle": "San Andreas",
            "doc_type": "Verification Test",
            "doc_number": "VERIFY-001",
            "title": "Backend Asset Verification Report",
            "content": "# SUCCESS\nAll core assets were found and the generator is stable."
        }
        # Inject ordinal date
        pdf_generator._ordinal_date = lambda dt: dt.strftime("%B %d, %Y")
        
        buf = pdf_generator.generate_document_pdf(data)
        if buf and len(buf.getvalue()) > 0:
            print(f"SUCCESS: Generated PDF ({len(buf.getvalue())} bytes)")
            return True
        else:
            print("ERROR: Generated an empty buffer.")
            return False
    except Exception as e:
        print(f"CRITICAL ERROR during generation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if verify():
        print("\nVerification Passed.")
        sys.exit(0)
    else:
        print("\nVerification Failed.")
        sys.exit(1)
