---
name: box-brand
description: Apply and check Box brand standards (writing style, colors, Inter Display type, containers, layouts, icons) on any generated slide, page, diagram, storyboard, brief, or mockup.
---

# Box Brand

Use this skill before you create or change any asset a person will see: decks, HTML pages, portal mockups, diagrams, storyboards, briefs, runbooks, and README copy. Branding is required for every generated asset, not a finishing touch.

## Read first

- `docs/brand/BOX-BRAND.md`: the rules. Read the sections for the asset you are making.
- `config/brand.json`: exact colors, gradients, type sizes, shapes, and theme. Take values from here, never from memory.
- `docs/brand/TEMPLATE-CATALOG.md`: pick a layout from the 104 template slides before designing your own.
- `assets/brand/icons/README.md`: the icon groups. Search `assets/brand/icons/index.json` by name, or view `assets/brand/icons/catalog/<group>.png` to choose visually.

## Make

1. **Choose the layout.** Map each message to a catalog layout: cover, section divider, key statement, columns, framework cards, side by side, big number, chart, flow chart, timeline, table, product, customer story, or closing. One message per slide or section.
2. **Write the copy.**
   - **Case and punctuation:** sentence case, except product and team names. Write "and", never an ampersand. No exclamation marks. Use the Oxford comma.
   - **No "Box's":** write "our" instead.
   - **Size:** bullets of at most 2 lines and under 10 words.
   - **Numbers and captions:** follow the formats in the guide. Captions start lowercase and have no period.
3. **Apply the tokens.**
   - **Titles:** title gradient, Inter Display Medium.
   - **Subtitles, lines, and arrows:** Box blue `#0061D3`.
   - **Body:** `#4B6E98`.
   - **Highlights and big numbers:** their gradients, used sparingly.
   - **Charts:** series colors in token order, with a source line.
4. **Use brand shapes.** Use the standard container (rounded, white-to-`#F5F9FD`, 0.75 pt `#D0D0D0` outline, soft shadow). Use the gradient-outline container for the single most important card. Use the backgrounds in the guide: light for content, Box blue for dividers, the dark gradient for covers and closings, black for negative topics.
5. **Use brand icons only.** Use the gradient line icons by default, product icons only to name a product, and file-type icons for files. Do not draw substitutes or import other icon sets.
6. **Keep the demo honest.** Synthetic materials stay labeled synthetic. Do not add customer logos, personas, or third-party marks that are not in the repo or approved by the user.

For `.pptx` output, set the theme colors from `theme_scheme`, use Inter Display for headings and body, use 16:9, and keep the footer "Box Confidential" bottom left with the date bottom right on covers. Inter Display may render with a substitute font in local previews, so leave about 10% slack in text boxes.

For HTML, use `typography.web_stack` with no network font loading, keep the page self-contained, and meet WCAG AA contrast. Gradient text needs a solid-color fallback.

## Check

- **Generated deliverables:** run `python scripts/build_deliverables.py --check`. The renderer refuses ampersands, repeated exclamation marks, and "Box's" in generated text. A user's quoted request, written as a Markdown blockquote, is exempt.
- **Other assets:** run `python -c "from box_agentic.brand import lint; import sys; print(lint(open(sys.argv[1]).read()))" <file>` on any other Markdown or text you wrote.
- **Visual review:** render the asset and look at it.
  - **Text:** title casing, no italics or underline, no text below 14 pt on slides.
  - **Color and contrast:** contrast is strong, and colors come from the tokens.
  - **Containers and icons:** containers are consistent, and icons are brand icons.
  - **Logo:** never inside a sentence, and the white or blue version matches the background.
  - **Never present:** decorative color bars, beige backgrounds, or Title Case headings.
- **Reporting:** report which checks ran. A lint pass does not prove sentence case or visual compliance.
