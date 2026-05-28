#!/usr/bin/env python3
"""
Save a follow-builders digest to INSIGHT and push to GitHub.

Usage:
  python scripts/save_digest.py --file /path/to/digest.txt
  cat digest.txt | python scripts/save_digest.py
  python scripts/save_digest.py --date 2026-05-28 --file digest.txt
"""

import sys, os, re, subprocess, argparse
from pathlib import Path
from datetime import datetime

REPO = Path(__file__).resolve().parent.parent

KNOWN_TAGS = [
    'Anthropic', 'OpenAI', 'Google', 'Meta', 'Microsoft', 'Mistral',
    'Every', 'xAI', 'DeepMind', 'Perplexity', 'Cohere', 'Stability',
]

def extract_tags(text):
    return [t for t in KNOWN_TAGS if t in text]

def clean_digest(text):
    text = text.strip()
    # Remove "AI Builders Digest — DATE" header line
    text = re.sub(r'^AI Builders Digest[^\n]*\n+', '', text, flags=re.MULTILINE)
    # Remove "Generated through the Follow Builders skill" footer
    text = re.sub(r'\n*Generated through the Follow Builders skill[^\n]*\n?', '', text)
    return text.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'),
                        help='Date in YYYY-MM-DD format (default: today)')
    parser.add_argument('--file', default=None,
                        help='Input file path (default: stdin)')
    args = parser.parse_args()

    date = args.date
    y, m, d = date.split('-')

    # Read content
    if args.file:
        content = Path(args.file).read_text(encoding='utf-8')
    else:
        print('Reading from stdin (Ctrl+D to finish)...')
        content = sys.stdin.read()

    content = clean_digest(content)
    if not content:
        print('Error: digest content is empty'); return

    tags = extract_tags(content)
    frontmatter = (
        f"---\n"
        f"title: {y}年{m}月{d}日 AI 摘要\n"
        f"date: {date}\n"
        f"tags: {', '.join(tags) if tags else 'AI'}\n"
        f"---\n\n"
    )

    # Save to content/YYYY/MM/YYYY-MM-DD.md
    out_dir = REPO / 'content' / y / m
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f'{date}.md'
    out_file.write_text(frontmatter + content, encoding='utf-8')
    print(f'Saved: content/{y}/{m}/{date}.md')

    # Build site
    result = subprocess.run(
        ['python', 'build.py'], cwd=REPO, capture_output=True, text=True
    )
    if result.returncode != 0:
        print('Build error:', result.stderr); return
    print(result.stdout.strip())

    # Git commit and push
    rel_path = f'content/{y}/{m}/{date}.md'
    subprocess.run(['git', 'add', rel_path], cwd=REPO)
    r = subprocess.run(
        ['git', 'commit', '-m', f'content: {date} AI digest'],
        cwd=REPO, capture_output=True, text=True
    )
    if 'nothing to commit' in r.stdout:
        print('No changes to commit'); return

    r = subprocess.run(['git', 'push'], cwd=REPO, capture_output=True, text=True)
    if r.returncode == 0:
        print(f'Published: https://wangboroy.github.io/insight/')
    else:
        print('Push failed:', r.stderr)

if __name__ == '__main__':
    main()
