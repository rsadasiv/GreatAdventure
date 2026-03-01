
import os
import re
import zipfile

def convert_emphasis(text):
    # Convert bold (**text**) first
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Then italics (*text*)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text

def is_poetry_block(lines, idx):
    # Heuristic: 2+ consecutive short lines (<=60 chars), not headings, not blockquote, not empty
    count = 0
    for i in range(idx, len(lines)):
        l = lines[i].strip()
        if not l or l.startswith('##') or l.startswith('###') or l.startswith('>'):
            break
        if len(l) <= 60:
            count += 1
        else:
            break
    return count >= 2

def markdown_to_html(input_txt, output_html, output_css, images_dir):
    with open(input_txt, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # First pass: collect chapter titles for TOC
    chapters = []
    for line in lines:
        if line.startswith("## "):
            title = re.sub(r"\*", "", line.replace("##", "").strip())
            chapters.append(title)
    # HTML header and TOC
    html = [
        "<!DOCTYPE html>",
        "<html lang='en'>",
        "<head>",
        "<meta charset='UTF-8'>",
        "<title>Harald Hardrada: Saga of the Northlands</title>",
        "<link rel='stylesheet' href='harald.css'>",
        "</head>",
        "<body>",
        "<div class='container'>",
        "<h1 class='book-title'>Harald Hardrada: Saga of the Northlands</h1>",
        "<nav class='toc'>",
        "<h2>Table of Contents</h2>",
        "<ul>"
    ]
    for i, title in enumerate(chapters, 1):
        html.append(f"<li><a href='#chapter-{i}'>{title}</a></li>")
    html += ["</ul>", "</nav>"]

    # Second pass: content
    chapter_idx = 0
    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")
        if line.startswith("## "):
            if chapter_idx > 0:
                html.append("</section>")
            chapter_idx += 1
            title = re.sub(r"\*", "", line.replace("##", "").strip())
            html.append(f"<section class='chapter' id='chapter-{chapter_idx}'>")
            html.append(f"<figure><img src='images/{chapter_idx}.jpg' alt='Chapter {chapter_idx}'><figcaption>Chapter {chapter_idx} Illustration</figcaption></figure>")
            html.append(f"<div class='chapter-title'>{title}</div>")
            # Check for gloss
            if i+1 < len(lines):
                gloss_line = lines[i+1].strip()
                if (gloss_line.startswith("*(") and gloss_line.endswith(")*")) or (gloss_line.startswith("(") and gloss_line.endswith(")")):
                    gloss = gloss_line.lstrip("*(").rstrip(")*").lstrip("(").rstrip(")")
                    html.append(f"<div class='chapter-gloss'>{convert_emphasis(gloss)}</div>")
                    i += 1
        elif line.startswith("### "):
            subtitle = re.sub(r"\*", "", line.replace("###", "").strip())
            html.append(f"<h3>{subtitle}</h3>")
        elif line.startswith("> "):
            html.append(f"<blockquote>{convert_emphasis(line[2:].strip())}</blockquote>")
        elif line.strip() == "---":
            html.append("<hr>")
        elif re.match(r"^(\*|\-|\+) ", line):
            # Start of a list
            html.append("<ul>")
            while i < len(lines) and re.match(r"^(\*|\-|\+) ", lines[i]):
                item = convert_emphasis(re.sub(r"^(\*|\-|\+) ", "", lines[i].strip()))
                html.append(f"<li>{item}</li>")
                i += 1
            html.append("</ul>")
            i -= 1
        elif is_poetry_block(lines, i):
            html.append("<div class='poetry'>")
            while i < len(lines):
                l = lines[i].strip()
                if not l or l.startswith('##') or l.startswith('###') or l.startswith('>'):
                    break
                if len(l) <= 60:
                    html.append(convert_emphasis(l))
                    i += 1
                else:
                    break
            html.append("</div>")
            i -= 1
        elif line.strip():
            html.append(f"<p>{convert_emphasis(line.strip())}</p>")
        i += 1
    if chapter_idx > 0:
        html.append("</section>")
    html += ["</div>", "</body>", "</html>"]

    with open(output_html, "w", encoding="utf-8") as f:
        f.write("\n".join(html))

    css = """
body {
  font-family: 'Georgia', serif;
  background: #f9f7f3;
  color: #222;
  margin: 0;
  padding: 0;
  line-height: 1.7;
}
.container {
  max-width: 900px;
  margin: 2em auto;
  padding: 2em;
  background: #fff;
  box-shadow: 0 0 10px rgba(0,0,0,0.07);
  border-radius: 8px;
}
.book-title {
  font-size: 2.5em;
  text-align: center;
  margin-bottom: 1em;
  color: #2a3a4a;
}
.toc {
  background: #f4ecd8;
  padding: 1em;
  margin-bottom: 2em;
  border-radius: 6px;
}
.toc h2 {
  margin-top: 0;
}
.toc ul {
  list-style: none;
  padding-left: 0;
}
.toc li {
  margin: 0.5em 0;
}
.toc a {
  text-decoration: none;
  color: #2a3a4a;
}
.chapter-title {
  font-size: 2em;
  font-weight: bold;
  margin-top: 1em;
  color: #3a3a3a;
}
.chapter-gloss {
  font-style: italic;
  color: #666;
  margin-bottom: 1em;
}
h3 {
  font-size: 1.4em;
  color: #4a5a6a;
  margin-top: 1em;
}
p {
  margin: 1em 0;
  text-align: justify;
}
blockquote {
  margin: 1em 2em;
  padding: 0.5em 1em;
  background: #f4ecd8;
  border-left: 4px solid #e2c275;
  font-style: italic;
}
.poetry {
  font-style: italic;
  margin-left: 2em;
  color: #3a3a3a;
  white-space: pre-line;
}
figure {
  text-align: center;
  margin: 1em 0;
}
figure img {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
}
figcaption {
  font-size: 0.9em;
  color: #555;
  margin-top: 0.5em;
}
ul {
  margin: 1em 0 1em 2em;
}
li {
  margin-bottom: 0.5em;
}
"""
    with open(output_css, "w", encoding="utf-8") as f:
        f.write(css)

    # Create images
    os.makedirs(images_dir, exist_ok=True)
    for idx in range(1, len(chapters)+1):
        img_path = os.path.join(images_dir, f"{idx}.jpg")
        with open(img_path, "wb") as img_file:
            img_file.write(b"\xff\xd8\xff\xd9")  # Minimal JPEG

def make_zip(html_file, css_file, images_dir, zip_file):
    with zipfile.ZipFile(zip_file, 'w') as zipf:
        zipf.write(html_file)
        zipf.write(css_file)
        for img in sorted(os.listdir(images_dir)):
            zipf.write(os.path.join(images_dir, img), os.path.join('images', img))

if __name__ == "__main__":
    # Input and output filenames
    input_txt = "Harald_Generated.txt"
    output_html = "harald.html"
    output_css = "harald.css"
    images_dir = "images"
    zip_file = "harald_ebook.zip"

    markdown_to_html(input_txt, output_html, output_css, images_dir)
    make_zip(output_html, output_css, images_dir, zip_file)
    print(f"Created {zip_file} with harald.html, harald.css, and images/")
