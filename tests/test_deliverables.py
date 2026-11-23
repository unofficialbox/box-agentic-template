import copy
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from new_project import generate
from build_deliverables import build, render


class DeliverableTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest = Path(self.tmp.name) / 'project with spaces'
        generate('test-case', 'Test Case', 'Salesforce', self.dest, scaffold_only=True)
        self.usecase = json.loads((self.dest / 'config/use-case.json').read_text())

    def save(self):
        (self.dest / 'config/use-case.json').write_text(json.dumps(self.usecase))

    def test_complete_deterministic_bundle_and_valid_svg(self):
        outputs = render(self.dest)
        self.assertEqual(len(outputs), 8)
        self.assertEqual(outputs, render(self.dest))
        svg = ET.fromstring(outputs['process.svg'])
        self.assertEqual(svg.tag, '{http://www.w3.org/2000/svg}svg')
        for step in self.usecase['steps']:
            self.assertIn(step['title'], outputs['storyboard.md'])
            self.assertIn(step['expected'], outputs['storyboard.html'])
        self.assertTrue(all('> ' + line in outputs['solution-brief.md'] for line in self.usecase['business_prompt'].splitlines() if line))
        self.assertNotIn('<script', outputs['storyboard.html'])
        self.assertNotIn('src="http', outputs['storyboard.html'])
        build(self.dest)
        self.assertEqual(build(self.dest, check=True), [])
        (self.dest / 'docs/generated/process.svg').write_text('stale')
        self.assertEqual(build(self.dest, check=True), ['process.svg'])
        build(self.dest)
        self.assertEqual(build(self.dest, check=True), [])

    def test_business_text_is_escaped_in_html_svg_and_mermaid(self):
        self.usecase['title'] = '<script>alert("test")</script>'
        self.usecase['steps'][0]['title'] = 'Review [supplier] "A" <certificate>'
        self.save()
        outputs = render(self.dest)
        self.assertNotIn('<script>', outputs['storyboard.html'])
        self.assertIn('&lt;script&gt;', outputs['storyboard.html'])
        self.assertIn('&quot;A&quot;', outputs['process.mmd'])
        ET.fromstring(outputs['process.svg'])

    def test_rejects_invalid_schema_duplicate_ids_missing_tools_and_records(self):
        original = copy.deepcopy(self.usecase)
        self.usecase['steps'][1]['id'] = self.usecase['steps'][0]['id']
        self.save()
        with self.assertRaises(ValueError):
            render(self.dest)
        self.usecase = copy.deepcopy(original)
        self.usecase['steps'][0]['tool'] = 'invented_provider_tool'
        self.save()
        with self.assertRaises(ValueError):
            render(self.dest)
        self.usecase = copy.deepcopy(original)
        self.usecase['record_id'] = 'absent'
        self.save()
        with self.assertRaises(ValueError):
            render(self.dest)
        self.usecase = copy.deepcopy(original)
        del self.usecase['business_prompt']
        self.save()
        with self.assertRaises(ValidationError):
            render(self.dest)

    def test_alternative_business_definition_changes_all_narrative_outputs(self):
        self.usecase.update(title='Supplier onboarding', business_prompt='Review supplier certificates.',
                            outcome='Route expired insurance to procurement.', decision_owner='Procurement manager')
        self.usecase['steps'] = [dict(id='intake', title='Find supplier package', actor='Specialist',
            action='Read supplier record', tool='get_record', prompt='Find the supplier.',
            expected='Supplier package resolved.', failure='Hold when supplier missing.'),
            dict(id='review', title='Manager exception review', actor='Procurement manager',
            action='Review expired insurance evidence', tool=None, prompt='Who owns the exception?',
            expected='Manager owns approval.', failure='Hold pending approval.')]
        self.save()
        outputs = render(self.dest)
        for name in ('process.svg', 'process.mmd', 'storyboard.md', 'storyboard.html', 'solution-brief.md'):
            self.assertNotIn('Loan officer', outputs[name])
        self.assertIn('Manager exception review', outputs['storyboard.html'])
        self.assertIn('Procurement manager', outputs['solution-brief.md'])

    def test_renderer_cli_rebuild_and_stale_check(self):
        args = [sys.executable, 'scripts/build_deliverables.py']
        subprocess.run(args, cwd=self.dest, check=True, capture_output=True)
        subprocess.run(args + ['--check'], cwd=self.dest, check=True, capture_output=True)
        (self.dest / 'docs/generated/process.svg').write_text('stale')
        failure = subprocess.run(args + ['--check'], cwd=self.dest, capture_output=True, text=True)
        self.assertNotEqual(failure.returncode, 0)
