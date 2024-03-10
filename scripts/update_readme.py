"""
Script to update the README file with the metadata required by Hugging Face Spaces.
"""

# Get Streamlit Version
requirements_path = "requirements.txt"

with open(requirements_path, 'r', encoding='utf-16') as requirements:
    for line in requirements:
        if line.strip().startswith("streamlit=="):
            streamlit_version = line.strip().split('==')[1]
            break

# Update README
readme_path = "README.md"

hf_space_metadata = f"""\
---
title: Chameleon
emoji: 🦎
colorFrom: green
colorTo: yellow
sdk: streamlit
sdk_version: {streamlit_version}
app_file: src/app.py
pinned: true
---
"""

# Open the README file
with open(readme_path, 'r') as original_readme:
    data = original_readme.read()
# Rewrite the README file, with metadata prepended
with open(readme_path, 'w', encoding="utf-8") as modified_readme:
    modified_readme.write(hf_space_metadata + data)
