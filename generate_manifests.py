import os
import json

base_dir = r"c:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\frontend\data\paperwork-generators"

for root, dirs, files in os.walk(base_dir):
    json_files = [f for f in files if f.endswith('.json') and f != 'manifest.json']
    if json_files or 'manifest.json' in files:
        manifest_path = os.path.join(root, 'manifest.json')
        
        # Load existing if available to keep metadata
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except:
                    data = {}
        else:
            folder_name = os.path.basename(root)
            if folder_name == "paperwork-generators": continue
            data = {"group_name": folder_name.upper(), "group_id": folder_name}
            
        data['files'] = json_files
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Updated {manifest_path}")
