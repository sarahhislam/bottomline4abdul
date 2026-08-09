#!/usr/bin/env python3
"""
Fix language selector integration across all pages.
Adds #lang-selector-wrap div and language-selector.js script
to any page that's missing them.
"""
import os
import re

PAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logic_modules', 'frontend', 'pages')
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')

def fix_page(filepath):
    """Add lang-selector-wrap div and language-selector.js script to a page."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changed = False
    
    # 1. Add #lang-selector-wrap div if missing
    if 'lang-selector-wrap' not in content:
        # Pattern: translate-widget-container div followed by back link
        # Add lang-selector-wrap between them
        pattern = re.compile(
            r'(<div class="translate-widget-container">\s*<div id="google_translate_element"></div>\s*</div>)'
        )
        if pattern.search(content):
            content = pattern.sub(
                r'\1\n    <div id="lang-selector-wrap"></div>',
                content
            )
            changed = True
    
    # 2. Add language-selector.js script if missing
    if 'language-selector.js' not in content:
        # Add after main.js script tag
        pattern = re.compile(
            r'(<script src="\.\./js/main\.js"></script>)'
        )
        if pattern.search(content):
            content = pattern.sub(
                r'\1\n<script src="../js/language-selector.js"></script>',
                content
            )
            changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  FIXED: {os.path.basename(filepath)}")
    else:
        print(f"  OK: {os.path.basename(filepath)} (no changes needed)")

def fix_template(filepath):
    """Add lang-selector-wrap div and language-selector.js script to a template."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    changed = False
    
    # 1. Add #lang-selector-wrap div if missing
    if 'lang-selector-wrap' not in content:
        # Pattern: translate-widget-container div
        pattern = re.compile(
            r'(<div class="translate-widget-container">\s*<div id="google_translate_element"></div>\s*</div>)'
        )
        if pattern.search(content):
            content = pattern.sub(
                r'\1\n    <div id="lang-selector-wrap"></div>',
                content
            )
            changed = True
    
    # 2. Add language-selector.js script if missing
    if 'language-selector.js' not in content:
        # Add before Google Translate scripts
        pattern = re.compile(
            r'(<!-- Google Translate Element Scripts -->)'
        )
        if pattern.search(content):
            content = pattern.sub(
                r'<script src="{{ url_for(\'static\', filename=\'js/language-selector.js\') }}"></script>\n\n\1',
                content
            )
            changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  FIXED: {os.path.basename(filepath)}")
    else:
        print(f"  OK: {os.path.basename(filepath)} (no changes needed)")

print("=== Fixing pages ===")
for fname in sorted(os.listdir(PAGES_DIR)):
    if fname.endswith('.html'):
        fix_page(os.path.join(PAGES_DIR, fname))

print("\n=== Fixing templates ===")
for fname in sorted(os.listdir(TEMPLATES_DIR)):
    if fname.endswith('.html'):
        fix_template(os.path.join(TEMPLATES_DIR, fname))

print("\nDone!")