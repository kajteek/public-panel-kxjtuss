import os
import re

with open(r"X:\strona\docs.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if "# DISCORD UI" in line or "get_edit_modal" in line:
        break
    if "import discord" in line or "from discord" in line:
        continue
    new_lines.append(line)

content = "".join(new_lines)

# mock discord classes so log_action doesn't crash if called (though we won't call it)
mock = """
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
    
"""
content = mock + content
content = content.replace("discord.User", "dict")
# Also the _ordinal_date missing in docs.py ? Let's check if _ordinal_date is defined.
# If not, let's fix it just in case.

with open(r"C:\Users\kaketan\.gemini\antigravity\scratch\lspd_web_app\backend\pdf_generator.py", "w", encoding="utf-8") as f:
    f.write(content)
