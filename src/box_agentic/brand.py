"""Box brand tokens and a writing-rule check for generated materials (config/brand.json)."""
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def load_brand(root=ROOT):
    brand = json.loads((Path(root) / "config/brand.json").read_text())
    for name, value in brand["colors"].items():
        if not re.fullmatch(r"#[0-9A-F]{6}", value):
            raise ValueError(f"Brand color {name} must be an uppercase #RRGGBB value")
    return brand


class _Text(HTMLParser):
    """Collect visible text from HTML or SVG, skipping style and script bodies."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        self._skip += tag in {"style", "script"}

    def handle_endtag(self, tag):
        self._skip -= tag in {"style", "script"} and self._skip > 0

    def handle_data(self, data):
        if not self._skip:
            self.parts.append(data)


def visible_text(name, content):
    """Return the reader-visible text of a generated file; quoted user input (Markdown blockquotes) is exempt."""
    if name.endswith((".html", ".svg")):
        parser = _Text()
        parser.feed(content)
        return "\n".join(parser.parts)
    if name.endswith(".mmd"):
        # Only quoted node and edge labels are visible; decode the entity escapes Mermaid renders.
        return unescape("\n".join(re.findall(r'"([^"]*)"', content)))
    # Markdown: code blocks, inline code, and quoted user input are not brand copy.
    lines, fenced = [], False
    for line in content.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            lines.append("")
            continue
        lines.append("" if fenced or line.lstrip().startswith(">") else re.sub(r"`[^`]*`", "", line))
    return "\n".join(lines)


def lint(text, brand=None):
    """List writing-rule violations in visible text. An empty list means the text follows the checked rules."""
    brand = brand or load_brand()
    findings = []
    allowed = brand["writing"].get("allowed_terms", [])
    for number, line in enumerate(text.splitlines(), 1):
        for term in allowed:
            line = line.replace(term, "")
        for rule in brand["writing"]["forbidden_patterns"]:
            if rule["pattern"] in line:
                findings.append(f"line {number}: {rule['rule']}: {line.strip()[:80]}")
    return findings
