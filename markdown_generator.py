pip install markdownify


from markdownify import markdownify
print(markdownify("<h1>Hello</h1><p>This is a test</p>"))


import os
import re
import csv
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from markdownify import markdownify as md
from concurrent.futures import ThreadPoolExecutor, as_completed

# ================= CONFIG =================
CSV_FILE = "links.csv"
URL_COLUMN = "url"
OUTPUT_FILE = "combined_data.md"
IMAGES_DIR = "images"
SKIPPED_FILE = "skipped_links.txt"
MAX_WORKERS = 10                    # Number of parallel threads
SLEEP_BETWEEN_REQUESTS = 0.2        # Slight delay to avoid rate limits
# ==========================================


def sanitize_text(text):
    return re.sub(r'\s+', ' ', text).strip()


def download_image(img_url):
    """Download image and return relative Markdown path."""
    try:
        os.makedirs(IMAGES_DIR, exist_ok=True)
        filename = os.path.basename(urlparse(img_url).path)
        if not filename:
            filename = hashlib.md5(img_url.encode()).hexdigest()[:8] + ".jpg"

        filepath = os.path.join(IMAGES_DIR, filename)
        if not os.path.exists(filepath):
            resp = requests.get(img_url, timeout=10)
            if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                with open(filepath, "wb") as f:
                    f.write(resp.content)
        return filepath
    except Exception:
        return None


def replace_and_download_images(markdown_content, base_url):
    """Find all image links in Markdown and download them locally."""
    pattern = re.compile(r'!\[(.*?)\]\((.*?)\)')
    new_content = markdown_content

    for match in pattern.findall(markdown_content):
        alt_text, img_src = match
        img_url = urljoin(base_url, img_src)
        local_path = download_image(img_url)
        if local_path:
            rel_path = os.path.relpath(local_path, os.path.dirname(OUTPUT_FILE))
            new_tag = f"![{alt_text}]({rel_path})"
            old_tag = f"![{alt_text}]({img_src})"
            new_content = new_content.replace(old_tag, new_tag)

    return new_content


def extract_to_markdown(url):
    """Extract the <body> content and convert it to Markdown."""
    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except Exception as e:
        with open(SKIPPED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{url} | FetchError: {e}\n")
        return None

    content_type = response.headers.get("content-type", "")
    if not content_type.startswith("text/html"):
        with open(SKIPPED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{url} | NonHTML: {content_type}\n")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "footer", "header", "nav", "form", "aside"]):
        tag.decompose()

    title = soup.title.string.strip() if soup.title and soup.title.string else "Untitled Page"
    body = soup.body
    if not body:
        with open(SKIPPED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{url} | MissingBody\n")
        return None

    markdown_content = md(str(body), heading_style="ATX", strip=["script", "style"])
    markdown_content = sanitize_text(markdown_content)
    markdown_content = replace_and_download_images(markdown_content, url)

    return f"""
---

# {title}

**Source:** {url}

## Content
{markdown_content}
"""


def load_urls_from_csv(csv_path, url_column):
    """Read URLs from a CSV file."""
    urls = []
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        if url_column not in reader.fieldnames:
            raise ValueError(f"❌ Column '{url_column}' not found in CSV headers: {reader.fieldnames}")
        for row in reader:
            url = row[url_column].strip()
            if url:
                urls.append(url)
    return urls


def main():
    if not os.path.exists(CSV_FILE):
        print(f"❌ '{CSV_FILE}' not found!")
        return

    try:
        urls = load_urls_from_csv(CSV_FILE, URL_COLUMN)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    print(f"🌐 Starting crawl for {len(urls)} URLs using {MAX_WORKERS} threads...\n")
    os.makedirs(os.path.dirname(OUTPUT_FILE) or ".", exist_ok=True)

    all_markdowns = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(extract_to_markdown, url): url for url in urls}

        for i, future in enumerate(as_completed(futures), start=1):
            url = futures[future]
            try:
                md_content = future.result()
                if md_content:
                    all_markdowns.append(md_content)
                print(f"✅ [{i}/{len(urls)}] Done: {url}")
            except Exception as e:
                print(f"⚠️ Error processing {url}: {e}")
                with open(SKIPPED_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{url} | ThreadError: {e}\n")
            time.sleep(SLEEP_BETWEEN_REQUESTS)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write(f"# Combined Web Data ({len(all_markdowns)} Successful)\n\n")
        out.write("\n".join(all_markdowns))

    print(f"\n✅ Completed {len(all_markdowns)} pages successfully!")
    print(f"📄 Output saved to: {OUTPUT_FILE}")
    print(f"🧾 Skipped URLs logged in: {SKIPPED_FILE}")


if __name__ == "__main__":
    main()