# Box brand guide for agents

These are the Box brand standards from the Box Corporate Template (Q3 FY27), converted to Markdown so agents can apply them. Every generated asset follows them: slides, HTML pages, diagrams, storyboards, briefs, runbooks, and UI mockups.

- **Tokens:** `config/brand.json` is the machine-readable source for colors, gradients, type, and shapes. Use the token, not a hand-typed value.
- **Icons:** `assets/brand/icons/` ([index](../../assets/brand/icons/README.md)).
- **Slide layouts:** [TEMPLATE-CATALOG.md](TEMPLATE-CATALOG.md) describes all 104 template slides.
- **Skill:** `.agents/skills/box-brand/SKILL.md` is the checklist agents run before and after making an asset.

When a rule here conflicts with a general design habit, the rule here wins.

## Writing style

| Rule | Avoid | Use |
|---|---|---|
| Sentence case everywhere, except product and team names (for example, Intelligent Content Management) | "Title Case Headline" | "Sentence case headline" |
| Spell out "and"; never use an ampersand | Automate & secure workflows | Automate and secure workflows |
| Let the presenter carry enthusiasm; avoid exclamation marks | Thank you!!! | Thank you |
| Emphasize with Inter Display SemiBold, never italics or underline | *increased 2x* | **increased 2x** |
| Use the Oxford comma | operations, legal and sales | operations, legal, and sales |
| Never write "Box's"; use "our" | Box's strategies | Our strategies |
| Never put the Box logo inside a line of text; type "Box" | Our mission at [logo] | Our mission at Box |

"Q&A" is the one ampersand the template itself uses; it stays as written.

`scripts/build_deliverables.py` rejects ampersands, repeated exclamation marks, and "Box's" in generated text. It cannot check sentence case, so check that yourself. A user's own words, quoted as a Markdown blockquote, are exempt.

### Numbers and captions

- **Uppercase, no space:** xxB, xxM, $xxx, $xxK, xxPB, xxTB, xxGB, xxMB.
- **Lowercase, with a space:** xx billion, xx million, xx calls, xx months, xx days.
- **Uppercase, with a space:** xx API, xx MAU, xx TAM.
- **Plus sign:** $xxK+, xxPB+, 39%+, xx+ API, xx+ days.
- **Trend:** ▴xx YoY / ▾xx YoY.
- **Captions:** start lowercase, keep them short, and end without a period ("pages processed in 2 days").
- **Japan and Korea:** use the circle ("maru") instead of a check mark.

## Audience and legibility

- **One message per slide.** Avoid too much information on one slide. The audience should focus on the presenter, not the slide.
- **Short bullets:** at most 2 lines and under 10 words each.
- **Three-second test:** a slide should be understood in 3 seconds.
- **Size:** never below 14 pt. Use 18–24 pt for body text where space allows.
- **Contrast:** keep strong contrast between text and background.
- **No run-on lists:** turn a comma-separated list of items into a bulleted list. Split a long list into two columns.
- **Quotes:** always include the source ("— Name, Title of Company"). Avoid long quotes, and color the key phrase with the text-highlight gradient.

## Color

| Role | Value |
|---|---|
| Box blue: section dividers, subtitles, lines, arrows, links | `#0061D3` |
| Slide title (gradient, left to right) | `#113053` → `#4B6E98` |
| Body copy | `#4B6E98` (`#3F628A` for dense bullet lists) |
| Text highlight (gradient) | `#FD56FF` → `#307CF2` |
| Big numbers (gradient) | `#EBAF83` → `#FD56FF` → `#00B0F0` |
| Pronouns and job title | `#91C1FC` on black, `#0061D3` on white |
| Standard container outline | `#D0D0D0` |
| Special or summary container outline (gradient) | `#BE65F4` → `#5189EE` |
| Screenshot and asset stroke | `#F2F2F2`, 0.75 pt |
| Charts, in order (each with a 25% tint) | `#0061D3`, `#ED3757`, `#F4B21A`, `#25C180`, `#9F3EEC`, plus `#91C1FC` |
| Status | pass `#25C180`, warning `#F4B21A`, fail `#ED3757` |

The PowerPoint theme ("Q2 FY27 Box") is in `config/brand.json` as `theme_scheme`. Use it when you write a `.pptx`.

### Backgrounds

| Slide type | Background |
|---|---|
| Content | White fading to a faint blue (`#FFFFFF` → `#F0F7FF`), sometimes with the thin rounded line pattern at one edge |
| Section divider | Solid Box blue `#0061D3`, white logo, white bold title |
| Cover, demo, panel, Q&A, thank you | Dark gradient: Box blue → navy `#01295C` → purple `#670BAA` |
| Negative topics (risks, threats) | Black `#000000`, with dark cards outlined in red `#ED3757` and a red warning icon |

Never use beige or cream backgrounds, and never use decorative color bars or accent stripes.

## Typography

- **Typeface:** Inter Display. Headings use Inter Display SemiBold, titles use Inter Display Medium, and body text uses Inter Display Regular. On the web, use the font stack in `config/brand.json` (`typography.web_stack`), which falls back to Inter and then system sans-serif. Do not load fonts from the network in self-contained pages.
- **Slide title:** 32 pt Inter Display Medium, 0.9 leading, centered near the top. Fill it with the title gradient.
- **Subtitle:** 16 pt Inter Display Regular, 0.9 leading, centered under the title, in `#0061D3`.
- **Side title** (left-aligned title beside content): 32 pt Inter Display Medium, single leading, title gradient.
- **Body:** 16 pt Inter Display Regular, single leading, 12 pt before each bullet, in `#4B6E98`.
- **Eyebrow:** a small uppercase label above a card title, in `#0061D3`. It is optional.
- **Big numbers:** Inter Display Medium with the big-number gradient, and a short lowercase caption below.

## Shapes and containers

- **Standard container:** a rounded rectangle about 6% corner radius, filled with a vertical gradient from white to `#F5F9FD`. It has a 0.75 pt outline in `#D0D0D0` and a soft drop shadow (black at 10%, about 11 pt blur, 3 pt down). Use it for topics, frameworks, and cards.
- **Summary or special container:** the same shape with the pink-to-blue gradient outline. Use it sparingly, for the one card that matters most.
- **Key-points list:** pill-shaped rows with a white fill and a light outline, each with an optional icon or numbered circle on the left.
- **Screenshots and assets:** 0.75 pt `#F2F2F2` stroke and a soft shadow (black, 90% transparency, 10 pt blur, 3 pt distance, 90°).
- **Flow charts:** rounded boxes filled with chart colors and connected with thin `#0061D3` elbow lines.
- **Timelines:** a thin `#0061D3` line with pill-shaped date nodes and milestone ticks above and below.
- **Tables:** no fill, thin blue rules between row groups, and colored dots for status.
- **Product status pills:** "Available now", "In Beta", and "Coming soon", as small rounded pills with a pastel fill above the title.

## Layouts

The template is 16:9 (13.333 × 7.5 in). Pick from these layouts ([full catalog](TEMPLATE-CATALOG.md)):

| Need | Layout |
|---|---|
| Open a deck | Cover: Box logo top center, two-line title, optional partner lockup ("box + Partner logo") and speaker. "Box Confidential" goes bottom left and the date bottom right |
| Start a section | Section divider on Box blue |
| Agenda | Pink "Agenda" title with sections and speakers; optional time column |
| Demo or panel | Dark gradient, title at left, speaker headshots with name, pronouns, title, and company |
| One idea | Key statement: large sentence with the highlight phrase in gradient |
| Compare or explain | Columns (bullets, paragraphs, or lists), or a framework of 2, 3, 4, or 6 cards |
| Content plus evidence | Side by side: bullets with a quote, image, or stat |
| Numbers | Standalone or side-by-side big numbers; bar, line, or pie (donut) charts with a source line |
| Process | Flow chart, timeline, or table |
| Product | Status pill, product title, short benefit list, and a UI screenshot |
| Customer story | Problem, Solution, Outcomes, Next steps, with a partner logo and photo |
| Close | Q&A or Thank you on the dark gradient, with optional follow-up info |

Every chart and stat carries a "Source:" line. Customer logo walls go in a table grid in alphabetical order.

## Logos and imagery

- **Logo use:** use only the supplied files in `assets/brand/icons/logos/`. The template uses the white logo on blue or dark backgrounds and the blue logo on white. By general logo practice (not stated in the template), never recolor, stretch, or outline it. The repo has the blue wordmark, the white wordmark (the same shape in white, for blue and dark backgrounds), and the app icon.
- **Partner lockup:** "box + [partner logo]", with the partner logo at the same visual height.
- **Icons:** use the gradient line icons from `assets/brand/icons/line/` as the default. Use product icons only to name a product. Do not mix in icons from other libraries.
- **Personas and headshots:** use brand-approved images only, and be mindful of diversity. Headshots should be well framed, in color, looking at the camera, against a background that contrasts with the subject, without logos or other people, and not pixelated or artsy.
- **Third-party logos:** use a customer or AI-vendor logo only when approved and current. They are not included here.

## Applying the brand to generated assets

| Asset | Requirement |
|---|---|
| `docs/generated/storyboard.html`, `process.svg` | Already branded by `scripts/build_deliverables.py` from `config/brand.json`; change tokens, not literals |
| `process.mmd` | Mermaid `base` theme with brand variables; Box and Salesforce nodes in Box blue, the hold node outlined in alert red |
| Markdown briefs and runbooks | Writing rules only: sentence case, no ampersands or exclamation marks, Oxford comma |
| New HTML pages and portal mockups | Brand tokens, the web font stack, the container style, and icons from `assets/brand/icons/` |
| Slide decks (`.pptx`) | Theme from `theme_scheme`, Inter Display fonts, the layouts above, and the slide checks in the `box-brand` skill |
| Charts | Series colors in order from `chart_series`, a source line, and no 3D or heavy gridlines |

Demo materials stay labeled as synthetic. Branding does not make a demo look live.
