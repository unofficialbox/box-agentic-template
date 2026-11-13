"""Render the Salesforce metadata starter from the platform and object blueprints."""
import argparse
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape
from box_agentic.platforms import validate_platforms

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://soap.sforce.com/2006/04/metadata'


def render(root=ROOT):
    sf = validate_platforms(root)['salesforce']
    spec = json.loads((root / 'config/salesforce/object.json').read_text())
    object_name = sf['object_api_name']
    fields = {f['api_name']: f for f in spec['fields']}
    required = {sf['external_id_field'], sf['folder_id_field'], sf['status_field'], *sf['field_mapping'].values()}
    if len(fields) != len(spec['fields']) or not required.issubset(fields):
        raise ValueError('Salesforce metadata must define every mapped custom field exactly once')
    prefix = f'force-app/main/default/objects/{object_name}'
    outputs = {'sfdx-project.json': json.dumps({'packageDirectories': [{'path': 'force-app', 'default': True}],
               'namespace': '', 'sourceApiVersion': spec['api_version']}, indent=2) + '\n'}
    outputs[f'{prefix}/{object_name}.object-meta.xml'] = f'''<?xml version="1.0" encoding="UTF-8"?>
<CustomObject xmlns="{NS}">
    <deploymentStatus>Deployed</deploymentStatus>
    <label>{escape(spec['label'])}</label>
    <nameField><label>Name</label><type>Text</type></nameField>
    <pluralLabel>{escape(spec['plural_label'])}</pluralLabel>
    <sharingModel>Private</sharingModel>
</CustomObject>
'''
    for field in spec['fields']:
        name = field['api_name']
        # Names become filenames as well as metadata identifiers.
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*__c', name):
            raise ValueError('Invalid Salesforce field API name')
        body = [f'<fullName>{name}</fullName>']
        if field.get('external_id'):
            body.append('<externalId>true</externalId>')
        body.append(f'<label>{escape(field["label"])}</label>')
        if field['type'] == 'Text':
            body.append(f'<length>{int(field["length"])}</length>')
        elif field['type'] in {'Currency', 'Number'}:
            body.extend([f'<precision>{int(field["precision"])}</precision>', f'<scale>{int(field["scale"])}</scale>'])
        else:
            raise ValueError('Unsupported starter field type; extend the renderer and tests for this domain')
        body.append(f'<type>{field["type"]}</type>')
        if field.get('external_id'):
            body.append('<unique>true</unique>')
        outputs[f'{prefix}/fields/{name}.field-meta.xml'] = (
            '<?xml version="1.0" encoding="UTF-8"?>\n' + f'<CustomField xmlns="{NS}">\n    ' +
            '\n    '.join(body) + '\n</CustomField>\n')
    return outputs


def build(root=ROOT, *, check=False):
    outputs = render(root)
    target = root / 'salesforce-project'
    drift = []
    for name, content in outputs.items():
        path = target / name
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p.is_relative_to(root)):
            raise ValueError('Salesforce metadata output must not be a symlink')
        if not path.exists() or path.read_text() != content:
            drift.append(name)
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
    return drift


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    drift = build(check=args.check)
    if args.check and drift:
        raise SystemExit('Stale Salesforce metadata: ' + ', '.join(drift))
    print('Salesforce metadata matches' if args.check else 'Built Salesforce metadata starter')
