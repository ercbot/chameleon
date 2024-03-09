import os

readme_path = "README.md"

hf_space_metadata="""
---
title: Chameleon
emoji: 🦎
colorFrom: green
colorTo: yellow
sdk: streamlit
sdk_version: 1.31.1
app_file: src/app.py
pinned: true
---
"""

# Open the README file
with open(readme_path, 'r') as original:
    data = original.read()
# Rewrite the README file, with metadata prepended
with open(readme_path, 'w') as modified:
    modified.write(hf_space_metadata + data)
