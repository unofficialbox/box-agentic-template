# Acceptance checklist

These are required checks, not claims that a live test passed.

- [ ] The fixture walkthrough performs zero external writes.
- [ ] Every document finding names a file, version, and evidence location.
- [ ] Proposals cannot update a record or grant approval.
- [ ] The wrong generation job and unapproved records fail verification.
- [ ] Box remains the content authority and Salesforce remains the structured-record authority in code, configuration, and demo materials.

- [ ] Code, fixture fields, tool contracts, and storyboard describe the same domain.
- [ ] Mermaid source and rendered SVG depict the same ordered process and hold conditions.
- [ ] Storyboard opens without a server or network connection.
- [ ] Client-specific discovery and live acceptance gaps are explicitly reported.
