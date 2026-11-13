import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from new_project import generate
from build_deployment import build, render
from check_dispatch import check


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'standalone project'
        generate('standalone-test', 'Standalone test', 'Salesforce', self.root)

    def save(self, path, value):
        (self.root / path).write_text(json.dumps(value))

    def test_generated_package_identity_and_every_referenced_source_exist(self):
        doc = json.loads((self.root / 'dispatch.bcl').read_text())
        manifest = doc['metadata']['manifest']
        self.assertEqual(doc['context'], 'solution-manifest')
        self.assertEqual(doc['provider'], 'box-dispatch')
        self.assertEqual(doc['scenario'], 'standalone-test')
        self.assertEqual(manifest['template_id'], 'standalone-test')
        settings = json.loads((self.root / manifest['deployment_config']).read_text())
        self.assertEqual(settings['context'], 'deployment-settings')
        self.assertEqual(settings['metadata']['settings']['box']['global_strategy'], 'reuse')
        for file in manifest['box']['sample_content']:
            self.assertTrue((self.root / file['source']).is_file())
            self.assertIn(file['target_folder'], manifest['box']['workspace']['children'])
        templates = json.loads((self.root / 'config/box/metadata-templates.bcl').read_text())
        self.assertEqual(templates['resources'][0]['config']['templates'][0]['templateKey'], 'agenticDocument')
        self.assertEqual({c['component_type'] for c in manifest['box']['capabilities']},
                         {'Folder Structure', 'Metadata Template', 'Sample Content'})
        self.assertTrue((self.root / 'salesforce-project/sfdx-project.json').exists())
        self.assertEqual(build(self.root, check=True), [])

    def test_standalone_walkthrough_and_render_checks_without_dispatch_git_or_go(self):
        env = {**os.environ, 'PATH': '', 'PYTHONPATH': str(self.root / 'src')}
        for script in ('demo.py', 'build_deployment.py', 'build_salesforce.py', 'build_deliverables.py'):
            args = [sys.executable, 'scripts/' + script]
            if script != 'demo.py': args.append('--check')
            result = subprocess.run(args, cwd=self.root, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_deployment_rebuild_restores_stale_source(self):
        (self.root / 'dispatch.bcl').write_text('stale')
        self.assertIn('dispatch.bcl', build(self.root, check=True))
        subprocess.run([sys.executable, 'scripts/build_deployment.py'], cwd=self.root, check=True, capture_output=True)
        subprocess.run([sys.executable, 'scripts/build_deployment.py', '--check'], cwd=self.root, check=True, capture_output=True)
        self.assertEqual(build(self.root, check=True), [])

    def test_rejects_non_synthetic_or_unsafe_sample_content(self):
        original = json.loads((self.root / 'fixtures/workflow.json').read_text())
        for mode in ('not-synthetic', 'path', 'duplicate'):
            fixture = copy.deepcopy(original)
            if mode == 'not-synthetic': fixture['synthetic'] = False
            elif mode == 'path': fixture['documents'][0]['file_id'] = '../outside'
            else: fixture['documents'].append(copy.deepcopy(fixture['documents'][0]))
            self.save('fixtures/workflow.json', fixture)
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                render(self.root)

    def test_rejects_undeclared_folder_and_nonportable_strategy(self):
        config = json.loads((self.root / 'config/deployment.json').read_text())
        original = copy.deepcopy(config)
        config['document_folders']['term_sheet'] = 'undeclared'
        self.save('config/deployment.json', config)
        with self.assertRaises(ValueError): render(self.root)
        original['box_strategy'] = 'create_new'
        self.save('config/deployment.json', original)
        with self.assertRaises(ValueError): render(self.root)

    def test_optional_dispatch_check_requires_explicit_valid_checkout(self):
        with self.assertRaisesRegex(ValueError, '--dispatch-root'):
            check(Path(self.tmp.name) / 'no-dispatch')
