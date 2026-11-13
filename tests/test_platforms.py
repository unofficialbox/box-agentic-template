import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from jsonschema import ValidationError
from box_agentic.platforms import validate_platforms

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from new_project import generate
from build_salesforce import build, render
from build_deliverables import render as render_materials


class PlatformTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'generated project'
        generate('platform-test', 'Platform test', 'Salesforce', self.root)
        self.config = json.loads((self.root / 'config/platforms.json').read_text())

    def save(self, path, value):
        (self.root / path).write_text(json.dumps(value))

    def test_both_platforms_and_mapping_survive_generation(self):
        config = validate_platforms(self.root)
        self.assertEqual(config['required_platforms'], ['box', 'salesforce'])
        self.assertEqual(config['box']['folder_binding'], 'salesforce.' + config['salesforce']['folder_id_field'])
        self.assertEqual(config['tool_authorities']['get_record'], ['salesforce'])
        self.assertEqual(config['tool_authorities']['analyze_document'], ['box'])
        self.assertEqual(config['tool_authorities']['verify_generated_document'], ['box', 'salesforce'])
        runtime = json.loads((self.root / 'config/runtime.example.json').read_text())
        self.assertIn('box', runtime)
        self.assertIn('salesforce', runtime)
        materials = render_materials(self.root)
        for name in ('process.mmd', 'process.svg', 'storyboard.html', 'storyboard.md', 'solution-brief.md', 'tool-matrix.md'):
            self.assertIn('Box', materials[name])
            self.assertIn('Salesforce', materials[name])

    def test_generator_defaults_to_salesforce_and_rejects_other_crm(self):
        dest = Path(self.tmp.name) / 'cli'
        subprocess.run([sys.executable, str(ROOT / 'scripts/new_project.py'), '--slug', 'cli-case',
                        '--name', 'CLI Case', '--destination', str(dest)], check=True, capture_output=True)
        self.assertEqual(json.loads((dest / 'config/project.json').read_text())['system_of_record'], 'Salesforce')
        with self.assertRaisesRegex(ValueError, 'requires Salesforce'):
            generate('wrong-crm', 'Wrong CRM', 'Other CRM', Path(self.tmp.name) / 'other')

    def test_invalid_platform_contracts_refuse(self):
        original = copy.deepcopy(self.config)
        variants = []
        config = copy.deepcopy(original); config['required_platforms'] = ['box']; variants.append(config)
        config = copy.deepcopy(original); config['box']['role'] = 'structured_record'; variants.append(config)
        config = copy.deepcopy(original); config['salesforce']['object_api_name'] = '../escape'; variants.append(config)
        config = copy.deepcopy(original); config['box']['folder_binding'] = 'caller.folder'; variants.append(config)
        config = copy.deepcopy(original); del config['tool_authorities']['get_record']; variants.append(config)
        config = copy.deepcopy(original); config['tool_authorities']['get_record'] = ['unknown']; variants.append(config)
        config = copy.deepcopy(original); del config['salesforce']['field_mapping']['rate']; variants.append(config)
        config = copy.deepcopy(original); config['tool_authorities']['get_record'] = ['box']; variants.append(config)
        for config in variants:
            self.save('config/platforms.json', config)
            with self.subTest(config=config), self.assertRaises(ValueError):
                validate_platforms(self.root)
        self.save('config/platforms.json', original)
        project = json.loads((self.root / 'config/project.json').read_text())
        project['system_of_record'] = 'Other CRM'
        self.save('config/project.json', project)
        with self.assertRaises(ValueError):
            validate_platforms(self.root)

    def test_narrative_cannot_remove_box_or_salesforce(self):
        original = json.loads((self.root / 'config/use-case.json').read_text())
        for field, value in [('system_of_record', 'Other CRM'), ('content_authority', 'Local disk')]:
            usecase = copy.deepcopy(original)
            usecase[field] = value
            self.save('config/use-case.json', usecase)
            with self.assertRaises(ValidationError):
                render_materials(self.root)

    def test_salesforce_metadata_matches_mapping_and_regenerates(self):
        outputs = render(self.root)
        namespace = {'m': 'http://soap.sforce.com/2006/04/metadata'}
        fields = set()
        for name, content in outputs.items():
            if name.endswith('.xml'):
                xml = ET.fromstring(content)
                if '/fields/' in name:
                    fields.add(xml.find('m:fullName', namespace).text)
                else:
                    self.assertEqual(xml.find('m:sharingModel', namespace).text, 'Private')
        sf = self.config['salesforce']
        self.assertTrue(set(sf['field_mapping'].values()).issubset(fields))
        self.assertIn(sf['folder_id_field'], fields)
        self.assertEqual(build(self.root, check=True), [])
        path = self.root / 'salesforce-project' / next(name for name in outputs if name.endswith('object-meta.xml'))
        path.write_text('stale')
        self.assertTrue(build(self.root, check=True))
        build(self.root)
        self.assertEqual(build(self.root, check=True), [])
        subprocess.run([sys.executable, 'scripts/build_salesforce.py', '--check'], cwd=self.root, check=True, capture_output=True)

    def test_metadata_missing_mapped_field_unsupported_type_and_unsafe_name_refuse(self):
        original = json.loads((self.root / 'config/salesforce/object.json').read_text())
        for mode in ('missing', 'type', 'unsafe'):
            spec = copy.deepcopy(original)
            if mode == 'missing': spec['fields'].pop()
            elif mode == 'type': spec['fields'][0]['type'] = 'Unimplemented'
            else: spec['fields'].append({'api_name': '../escape', 'label': 'Unsafe', 'type': 'Text', 'length': 10})
            self.save('config/salesforce/object.json', spec)
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                render(self.root)
