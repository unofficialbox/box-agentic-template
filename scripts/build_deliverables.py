"""Render a use-case definition into portable demo materials, without a model or network."""
import argparse
from html import escape
import json
from pathlib import Path
import textwrap
from jsonschema import Draft202012Validator
from box_agentic.platforms import validate_platforms
from box_agentic.intake import require_ready
from box_agentic.brand import lint, load_brand, visible_text

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("process.mmd", "process.svg", "storyboard.md", "storyboard.html", "solution-brief.md", "demo-runbook.md", "tool-matrix.md", "acceptance.md")


def load(root):
    if (root / "config/intake.local.json").exists():
        require_ready(root, root / "config/intake.local.json")
    validate_platforms(root)
    usecase = json.loads((root / "config/use-case.json").read_text())
    schema = json.loads((root / "config/use-case.schema.json").read_text())
    Draft202012Validator(schema).validate(usecase)
    tools = json.loads((root / "config/tools.json").read_text())["tools"]
    names = {t["name"] for t in tools}
    ids = [step["id"] for step in usecase["steps"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Process step IDs must be unique")
    if any(step["tool"] is not None and step["tool"] not in names for step in usecase["steps"]):
        raise ValueError("Process references a tool outside the registry")
    fixture = json.loads((root / "fixtures/workflow.json").read_text())
    if usecase["record_id"] not in {r["record_id"] for r in fixture["records"]}:
        raise ValueError("Use-case record is absent from fixtures")
    return usecase, tools


def label(value):
    # Mermaid quoted labels: escape syntax while retaining arbitrary business text.
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ").replace("[", "&#91;").replace("]", "&#93;").replace("`", "&#96;")


def stops(colors):
    return ''.join(f'<stop offset="{i / max(len(colors) - 1, 1):g}" stop-color="{c}"/>' for i, c in enumerate(colors))


def process_svg(usecase, brand):
    # Box brand: gradient titles, Box blue lines and arrows, outlined cards with a soft shadow.
    c, g, font = brand["colors"], brand["gradients"], brand["typography"]["web_stack"]
    steps = usecase["steps"]
    height = 126 + len(steps) * 124
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">' + escape(usecase["title"]) + ' process</title>',
             '<desc id="desc">Ordered workflow. Each step includes its stop condition. Synthetic demonstration.</desc>',
             f'<style>text{{font-family:{escape(font)}}}.t{{font-weight:500}}</style>',
             '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">'
             f'<path d="M0,0 L0,6 L9,3 z" fill="{c["rule"]}"/></marker>'
             f'<linearGradient id="page" x1="0" y1="0" x2="0" y2="1">{stops(g["light_background"])}</linearGradient>'
             f'<linearGradient id="title-ink" x1="0" y1="0" x2="1" y2="0">{stops(g["slide_title"])}</linearGradient>'
             f'<linearGradient id="card" x1="0" y1="0" x2="0" y2="1">{stops(g["container_fill"])}</linearGradient>'
             '<filter id="shadow" x="-5%" y="-10%" width="110%" height="140%"><feDropShadow dx="0" dy="3" stdDeviation="5" flood-color="#000000" flood-opacity="0.1"/></filter></defs>',
             f'<rect width="960" height="{height}" fill="url(#page)"/>',
             '<text class="t" x="40" y="44" font-size="26" fill="url(#title-ink)">Box + Salesforce · synthetic demo</text>']
    for index, step in enumerate(steps):
        y = 76 + index * 124
        if index:
            parts.append(f'<path d="M480,{y-26} V{y-5}" stroke="{c["rule"]}" stroke-width="1.5" marker-end="url(#arrow)"/>')
        parts.append(f'<rect x="40" y="{y}" width="880" height="98" rx="14" fill="url(#card)" stroke="{c["container_outline"]}" filter="url(#shadow)"/>')
        lines = [f'{index+1}. {step["title"]}', 'Owner: ' + step["actor"], 'Hold: ' + step['failure']]
        for row, line in enumerate(lines):
            chunks = textwrap.wrap(line, width=100 if row else 78)
            if len(chunks) > 1:
                # Full wording stays in Mermaid and storyboard; SVG summary remains bounded.
                line = chunks[0] + '…'
            style = f'class="t" font-size="18" fill="{c["title_start"]}"' if row == 0 else f'font-size="14" fill="{c["body"]}"'
            parts.append(f'<text x="62" y="{y+28+row*25}" {style}>{escape(line)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render(root=ROOT):
    u, tools = load(root)
    brand = load_brand(root)
    c, g, font = brand["colors"], brand["gradients"], brand["typography"]["web_stack"]
    steps = u["steps"]
    init = ("%%{init: {'theme': 'base', 'themeVariables': {'fontFamily': 'Inter Display, Inter, system-ui, sans-serif', "
            f"'primaryColor': '{c['white']}', 'primaryBorderColor': '{c['container_outline']}', 'primaryTextColor': '{c['title_start']}', "
            f"'lineColor': '{c['rule']}', 'textColor': '{c['body']}'}}}}}}%%")
    mmd = [init, 'flowchart TD', '  box["Box: governed content"]', '  salesforce["Salesforce: structured records"]', '  salesforce <-->|"record to folder mapping"| box']
    for step in steps:
        mmd.append(f'  {step["id"]}["{label(step["title"])}<br/>{label(step["actor"])}"]')
    for left, right in zip(steps, steps[1:]):
        mmd.append(f'  {left["id"]} --> {right["id"]}')
    mmd.append('  hold["Hold action and report missing evidence or authorization"]')
    for step in steps:
        mmd.append(f'  {step["id"]} -. "check fails" .-> hold')
    mmd.extend([f'  classDef platform fill:{c["box_blue"]},stroke:{c["box_blue"]},color:{c["white"]}',
                f'  classDef hold fill:{c["white"]},stroke:{c["alert"]},color:{c["title_start"]}',
                '  class box,salesforce platform', '  class hold hold'])
    story = [f'# {u["title"]}: demo storyboard', '', '**Platforms: Box + Salesforce. Evidence level: synthetic fixture.**', '', u['outcome'], '']
    cards = []
    for index, step in enumerate(steps, 1):
        story.extend([f'## Beat {index}: {step["title"]}', '', f'**Actor:** {step["actor"]}', '',
                      '**Say / ask:** ' + step['prompt'], '', '**Show:** ' + step['action'], '',
                      '**Expected evidence:** ' + step['expected'], '', '**Failure path:** ' + step['failure'], ''])
        cards.append('<article><span class="number">Beat ' + str(index) + '</span><h2>' + escape(step['title']) + '</h2>' +
                     ''.join('<p><strong>' + key + '</strong> ' + escape(value) + '</p>' for key, value in (
                         ('Actor', step['actor']), ('Prompt', step['prompt']), ('Show', step['action']),
                         ('Evidence', step['expected']), ('If blocked', step['failure']))) + '</article>')
    html = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>' + escape(u['title']) + ' — Demo storyboard</title><style>'
            # Box brand (docs/brand/BOX-BRAND.md): Inter Display, gradient title, Box blue subtitles, outlined containers.
            f'*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient({g["light_background"][0]},{g["light_background"][1]}) fixed;'
            f'color:{c["body"]};font:17px/1.55 {font}}}'
            'main{max-width:1080px;margin:auto;padding:48px 24px}header{text-align:center;margin-bottom:32px}'
            f'h1{{font-weight:500;font-size:clamp(32px,5vw,48px);line-height:1.05;margin:12px 0;color:{c["title_start"]};'
            f'background:linear-gradient(90deg,{",".join(g["slide_title"])});-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}'
            f'h2{{font-weight:500;color:{c["title_start"]};margin:6px 0 12px}}header p{{color:{c["subtitle"]};max-width:760px;margin:auto}}'
            f'.badge{{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:{c["subtitle"]}}}'
            f'.number{{font-size:13px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;'
            f'background:linear-gradient(90deg,{",".join(g["text_highlight"])});-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}}'
            f'article{{background:linear-gradient({",".join(g["container_fill"])});border:1px solid {c["container_outline"]};border-radius:14px;'
            f'box-shadow:{brand["shapes"]["shadow"]};padding:28px;margin:24px 0}}'
            '.diagram{overflow-x:auto;margin:24px 0}.diagram svg{width:100%;min-width:720px;height:auto}p{overflow-wrap:anywhere}'
            f'strong{{display:block;font-size:13px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;color:{c["subtitle"]}}}'
            '@media print{article{break-inside:avoid;box-shadow:none}main{padding:0}}</style><main><header><span class="badge">Box + Salesforce · synthetic demonstration · no live writes</span>'
            '<h1>' + escape(u['title']) + '</h1><p>' + escape(u['outcome']) + '</p></header><div class="diagram" tabindex="0" role="region" aria-label="Process diagram, scroll horizontally on small screens">' + process_svg(u, brand) + '</div>' + ''.join(cards) + '</main></html>\n')
    # The user's request is quoted verbatim; brand writing checks apply to everything else.
    brief = [f'# {u["title"]}: solution brief', '', '## Business request', '', *['> ' + line if line else '>' for line in u['business_prompt'].splitlines()], '', '## Intended outcome', '', u['outcome'], '',
             '## Authorities', '', f'- Governed content: {u["content_authority"]}', f'- Structured record: {u["system_of_record"]}', f'- Consequential decision: {u["decision_owner"]}', '',
             '## Assumptions', '', *['- ' + a for a in u['assumptions']], '', '## Not implemented', '', *['- ' + a for a in u['not_implemented']], '']
    authorities = validate_platforms(root)['tool_authorities']
    matrix = ['# Tool matrix', '', 'All included implementations are mock-only and read-only. Inspect config/tools.json for exact schemas.', '', '| Tool | Purpose | Platform authority | Implementation | External writes |', '|---|---|---|---|---|']
    for tool in tools:
        matrix.append('| ' + ' | '.join([tool['name'], tool['description'].replace('|', r'\|').replace('\n', ' '), ' + '.join({'box': 'Box', 'salesforce': 'Salesforce'}[owner] for owner in authorities[tool['name']]), tool['implementation'], 'None']) + ' |')
    runbook = ['# Presenter runbook', '', '1. Create a virtual environment and install `.[mcp,dev]` as documented in README.',
               '2. Run `python scripts/validate.py` and `python scripts/build_deliverables.py --check`.',
               '3. Open `docs/generated/storyboard.html` locally; it is self-contained and makes no network requests.',
               '4. Run `python scripts/demo.py` or connect the mock MCP server from docs/CLIENTS.md.',
               '5. Follow each storyboard prompt and verify its expected evidence.',
               '6. Explain each held action and name the human decision owner. Do not describe fixtures as live.',
               '7. Repeat the walkthrough: it has no external side effects and needs no tenant reset.',
               '8. Build any slides or extra pages with the box-brand skill and docs/brand/BOX-BRAND.md.', '',
               '## Deployment preparation', '', 'Read docs/DEPLOYMENT.md. Use included platform assets standalone, or the optional Dispatch BCL interface. Infrastructure deployment does not activate live workflow adapters.', '',
               '## Live rehearsal', '', 'Use docs/OPERATIONS.md after implementing live adapters. Keep live receipts outside the portable bundle.', '']
    acceptance = ['# Acceptance checklist', '', 'These are required checks, not claims that a live test passed.', '', *['- [ ] ' + a for a in u['acceptance']], '',
                  '- [ ] Code, fixture fields, tool contracts, and storyboard describe the same domain.',
                  '- [ ] Mermaid source and rendered SVG depict the same ordered process and hold conditions.',
                  '- [ ] Storyboard opens without a server or network connection.',
                  '- [ ] Client-specific discovery and live acceptance gaps are explicitly reported.', '']
    outputs = dict(zip(NAMES, ["\n".join(mmd)+"\n", process_svg(u, brand), "\n".join(story), html, "\n".join(brief), "\n".join(runbook), "\n".join(matrix)+"\n", "\n".join(acceptance)]))
    findings = [f'{name} {finding}' for name, content in outputs.items() for finding in lint(visible_text(name, content), brand)]
    if findings:
        raise ValueError('Generated materials break Box writing rules (docs/brand/BOX-BRAND.md): ' + '; '.join(findings))
    return outputs


def build(root=ROOT, *, check=False):
    rendered = render(root)
    target = root / "docs/generated"
    if target.is_symlink():
        raise ValueError("Generated output must not be a symlink")
    drift = []
    for name, content in rendered.items():
        path = target / name
        if path.is_symlink():
            raise ValueError("Generated output must not be a symlink")
        if not path.exists() or path.read_text() != content:
            drift.append(name)
            if not check:
                target.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
    return drift


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    drift = build(check=args.check)
    if args.check and drift:
        raise SystemExit("Stale demo materials: " + ", ".join(drift))
    print("Demo materials match" if args.check else "Built process diagram, storyboard, brief, runbook, tool matrix, and acceptance checklist")
