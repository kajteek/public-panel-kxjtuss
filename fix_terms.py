import json
import re

def replace_terms(text):
    if not text: return text
    
    replacements = [
        (r'\b[Ff]unkcjonariusz policji\b', lambda m: 'Oficer departamentu' if m.group()[0].isupper() else 'oficer departamentu'),
        (r'\b[Ff]unkcjonariusze policji\b', lambda m: 'Oficerowie departamentu' if m.group()[0].isupper() else 'oficerowie departamentu'),
        
        (r'\b[Ff]unkcjonariusza\b', lambda m: 'Oficera' if m.group()[0].isupper() else 'oficera'),
        (r'\b[Ff]unkcjonariuszy\b', lambda m: 'Oficerów' if m.group()[0].isupper() else 'oficerów'),
        (r'\b[Ff]unkcjonarzom\b', lambda m: 'Oficerom' if m.group()[0].isupper() else 'oficerom'),
        (r'\b[Ff]unkcjonariuszom\b', lambda m: 'Oficerom' if m.group()[0].isupper() else 'oficerom'),
        (r'\b[Ff]unkcjonariuszowi\b', lambda m: 'Oficerowi' if m.group()[0].isupper() else 'oficerowi'),
        (r'\b[Ff]unkcjonariusze\b', lambda m: 'Oficerowie' if m.group()[0].isupper() else 'oficerowie'),
        (r'\b[Ff]unkcjonariusz\b', lambda m: 'Oficer' if m.group()[0].isupper() else 'oficer'),
        
        (r'\b[Pp]olicji\b', lambda m: 'Departamentu' if m.group()[0].isupper() else 'departamentu'),
        (r'\b[Pp]olicję\b', lambda m: 'Departament' if m.group()[0].isupper() else 'departament'),
        (r'\b[Pp]olicja\b', lambda m: 'Departament' if m.group()[0].isupper() else 'departament'),
        (r'\b[Pp]olicją\b', lambda m: 'Departamentem' if m.group()[0].isupper() else 'departamentem'),
        
        (r'\b[Pp]olicjant\b', lambda m: 'Oficer' if m.group()[0].isupper() else 'oficer'),
        (r'\b[Pp]olicjanta\b', lambda m: 'Oficera' if m.group()[0].isupper() else 'oficera'),
        (r'\b[Pp]olicjanci\b', lambda m: 'Oficerowie' if m.group()[0].isupper() else 'oficerowie'),
    ]
    
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text)
        
    return text

files = [
    r"c:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\client\data\caselaws.json",
    r"c:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\data\caselaws.json"
]

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for case in data.get('caselaws', []):
            if 'summary' in case:
                case['summary'] = replace_terms(case['summary'])
            if 'implication' in case:
                case['implication'] = replace_terms(case['implication'])
                
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Successfully updated terminology in {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
