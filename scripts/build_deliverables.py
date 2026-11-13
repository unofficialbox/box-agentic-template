"""Render a use-case definition into portable demo materials, without a model or network."""
import argparse
from html import escape
import json
from pathlib import Path
import textwrap
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("process.mmd", "process.svg", "storyboard.md", "storyboard.html", "solution-brief.md", "demo-runbook.md", "tool-matrix.md", "acceptance.md")


def load(root):
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


def process_svg(usecase):
    steps = usecase["steps"]
    height = 126 + len(steps) * 124
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">' + escape(usecase["title"]) + ' process</title>',
             '<desc id="desc">Ordered workflow. Each step includes its stop condition. Synthetic demonstration.</desc>',
             '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#53657c"/></marker></defs>',
             f'<rect width="960" height="{height}" fill="#f4f7fb"/>',
             '<text x="40" y="42" font-family="sans-serif" font-size="24" fill="#172b4d">Business process · synthetic demo</text>']
    for index, step in enumerate(steps):
        y = 76 + index * 124
        if index:
            parts.append(f'<path d="M480,{y-26} V{y-5}" stroke="#53657c" marker-end="url(#arrow)"/>')
        parts.append(f'<rect x="40" y="{y}" width="880" height="98" rx="12" fill="white" stroke="#c5d1df"/>')
        lines = [f'{index+1}. {step["title"]}', 'Owner: ' + step["actor"], 'Hold: ' + step['failure']]
        for row, line in enumerate(lines):
            chunks = textwrap.wrap(line, width=100 if row else 78)
            if len(chunks) > 1:
                # Full wording stays in Mermaid and storyboard; SVG summary remains bounded.
                line = chunks[0] + '…'
            parts.append(f'<text x="62" y="{y+28+row*25}" font-family="sans-serif" font-size="{18 if row == 0 else 14}" fill="#172b4d">{escape(line)}</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def render(root=ROOT):
    u, tools = load(root)
    steps = u["steps"]
    mmd = ['flowchart TD']
    for step in steps:
        mmd.append(f'  {step["id"]}["{label(step["title"])}<br/>{label(step["actor"])}"]')
    for left, right in zip(steps, steps[1:]):
        mmd.append(f'  {left["id"]} --> {right["id"]}')
    mmd.append('  hold["Hold action and report missing evidence or authorization"]')
    for step in steps:
        mmd.append(f'  {step["id"]} -. "check fails" .-> hold')
    story = [f'# {u["title"]}: demo storyboard', '', '**Evidence level: synthetic fixture.**', '', u['outcome'], '']
    cards = []
    for index, step in enumerate(steps, 1):
        story.extend([f'## Beat {index}: {step["title"]}', '', f'**Actor:** {step["actor"]}', '',
                      '**Say / ask:** ' + step['prompt'], '', '**Show:** ' + step['action'], '',
                      '**Expected evidence:** ' + step['expected'], '', '**Failure path:** ' + step['failure'], ''])
        cards.append('<article><span class="number">BEAT ' + str(index) + '</span><h2>' + escape(step['title']) + '</h2>' +
                     ''.join('<p><strong>' + key + '</strong> ' + escape(value) + '</p>' for key, value in (
                         ('Actor', step['actor']), ('Prompt', step['prompt']), ('Show', step['action']),
                         ('Evidence', step['expected']), ('If blocked', step['failure']))) + '</article>')
    html = ('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>' + escape(u['title']) + ' — Demo storyboard</title><style>'
            '*{box-sizing:border-box}body{margin:0;background:#f4f7fb;color:#172b4d;font:17px/1.55 system-ui,sans-serif}'
            'main{max-width:1080px;margin:auto;padding:48px 24px}h1{font-size:clamp(32px,5vw,52px);line-height:1.1}'
            '.badge,.number{font-size:13px;letter-spacing:.08em;color:#31598c}article{background:white;border:1px solid #c5d1df;border-radius:14px;padding:28px;margin:24px 0}'
            '.diagram{overflow-x:auto;margin:24px 0}.diagram svg{width:100%;min-width:720px;height:auto}p{overflow-wrap:anywhere}strong{display:block;font-size:13px;text-transform:uppercase;color:#53657c}'
            '@media print{article{break-inside:avoid}main{padding:0}}</style><main><span class="badge">SYNTHETIC DEMONSTRATION · NO LIVE WRITES</span>'
            '<h1>' + escape(u['title']) + '</h1><p>' + escape(u['outcome']) + '</p><div class="diagram" tabindex="0" role="region" aria-label="Process diagram, scroll horizontally on small screens">' + process_svg(u) + '</div>' + ''.join(cards) + '</main></html>\n')
    brief = [f'# {u["title"]}: solution brief', '', '## Business request', '', u['business_prompt'], '', '## Intended outcome', '', u['outcome'], '',
             '## Authorities', '', f'- Governed content: {u["content_authority"]}', f'- Structured record: {u["system_of_record"]}', f'- Consequential decision: {u["decision_owner"]}', '',
             '## Assumptions', '', *['- ' + a for a in u['assumptions']], '', '## Not implemented', '', *['- ' + a for a in u['not_implemented']], '']
    matrix = ['# Tool matrix', '', 'All included implementations are mock-only and read-only. Inspect config/tools.json for exact schemas.', '', '| Tool | Purpose | Implementation | External writes |', '|---|---|---|---|']
    for tool in tools:
        matrix.append('| ' + ' | '.join([tool['name'], tool['description'].replace('|', r'\|').replace('\n', ' '), tool['implementation'], 'None']) + ' |')
    runbook = ['# Presenter runbook', '', '1. Create a virtual environment and install `.[mcp,dev]` as documented in README.',
               '2. Run `python scripts/validate.py` and `python scripts/build_deliverables.py --check`.',
               '3. Open `docs/generated/storyboard.html` locally; it is self-contained and makes no network requests.',
               '4. Run `python scripts/demo.py` or connect the mock MCP server from docs/CLIENTS.md.',
               '5. Follow each storyboard prompt and verify its expected evidence.',
               '6. Explain each held action and name the human decision owner. Do not describe fixtures as live.',
               '7. Repeat the walkthrough: it has no external side effects and needs no tenant reset.', '',
               '## Live rehearsal', '', 'Use docs/OPERATIONS.md after implementing live adapters. Keep live receipts outside the portable bundle.', '']
    acceptance = ['# Acceptance checklist', '', 'These are required checks, not claims that a live test passed.', '', *['- [ ] ' + a for a in u['acceptance']], '',
                  '- [ ] Code, fixture fields, tool contracts, and storyboard describe the same domain.',
                  '- [ ] Mermaid source and rendered SVG depict the same ordered process and hold conditions.',
                  '- [ ] Storyboard opens without a server or network connection.',
                  '- [ ] Client-specific discovery and live acceptance gaps are explicitly reported.', '']
    return dict(zip(NAMES, ["\n".join(mmd)+"\n", process_svg(u), "\n".join(story), html, "\n".join(brief), "\n".join(runbook), "\n".join(matrix)+"\n", "\n".join(acceptance)]))


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
