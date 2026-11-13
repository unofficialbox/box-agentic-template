import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from box_agentic.intake import (answer, confirm, fingerprint, load_catalog, new_state,
                               next_batch, question_map, require_ready, review, validate_state)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from new_project import generate
from build_deliverables import render as render_materials


class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.catalog = load_catalog(ROOT)
        self.state = new_state('Onboard suppliers using Box documents and Salesforce records.')

    def complete(self, mode='offline'):
        state = answer(self.catalog, self.state, 'implementation_depth', mode)
        while next_batch(self.catalog, state)['stage'] == 'questions':
            for question in next_batch(self.catalog, state)['questions']:
                state = answer(self.catalog, state, question['id'],
                               'Concrete test decision for ' + question['id'])
        return state

    def save(self, state, path=None):
        path = path or self.base / 'intake.json'
        path.write_text(json.dumps(state))
        return path

    def test_fixed_order_small_batches_and_skip_known_facts(self):
        first = next_batch(self.catalog, self.state)
        self.assertEqual([q['id'] for q in first['questions']],
                         ['project_identity', 'business_outcome', 'scope'])
        self.assertLessEqual(len(first['questions']), 3)
        state = answer(self.catalog, self.state, 'project_identity', 'Supplier; supplier-onboarding', source='brief')
        self.assertEqual([q['id'] for q in next_batch(self.catalog, state)['questions']], ['business_outcome', 'scope'])
        self.assertEqual(next_batch(self.catalog, state), next_batch(self.catalog, state))
        self.assertEqual(state['answers']['project_identity']['source'], 'brief')

    def test_offline_and_live_branches_have_exact_question_coverage(self):
        initial = review(self.catalog, self.state)
        self.assertEqual(len(initial['conditional_pending']), 3)
        self.assertEqual(initial['deferred_by_scope'], [])
        offline = self.complete()
        result = review(self.catalog, offline)
        self.assertEqual(len(result['answers']), 27)
        self.assertEqual(len(result['deferred_by_scope']), 3)
        self.assertEqual(result['missing'], [])
        scoped = answer(self.catalog, offline, 'live_targets', 'Previously supplied test org alias, kept outside active build scope')
        self.assertEqual(review(self.catalog, scoped)['inactive_answers'][0]['id'], 'live_targets')
        live = answer(self.catalog, offline, 'implementation_depth', 'live_adapters')
        self.assertEqual(set(review(self.catalog, live)['missing']), {'live_targets', 'live_capabilities', 'live_verification'})
        self.assertEqual(len(review(self.catalog, self.complete('live_adapters'))['answers']), 30)

    def test_recommendations_remain_visible_until_user_confirms_brief(self):
        state = self.complete()
        state = answer(self.catalog, state, 'technical_constraints', 'Keep Python and no hosted services',
                       source='agent', status='proposed')
        self.assertEqual(next_batch(self.catalog, state)['stage'], 'confirm_brief')
        confirmed = confirm(self.catalog, state, fingerprint(self.catalog, state))
        self.assertEqual(next_batch(self.catalog, confirmed)['stage'], 'ready')
        self.assertEqual(confirmed['answers']['technical_constraints']['status'], 'proposed')
        self.assertTrue(require_ready(ROOT, self.save(confirmed))['confirmed'])

    def test_missing_and_stale_confirmation_refuse(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            confirm(self.catalog, self.state, fingerprint(self.catalog, self.state))
        state = self.complete()
        with self.assertRaisesRegex(ValueError, 'changed'):
            confirm(self.catalog, state, 'old-hash')
        state = confirm(self.catalog, state, fingerprint(self.catalog, state))
        updated = answer(self.catalog, state, 'scope', 'Revised supplier scope')
        self.assertFalse(review(self.catalog, updated)['confirmed'])
        with self.assertRaises(ValueError): require_ready(ROOT, self.save(updated))
        changed_catalog = copy.deepcopy(self.catalog)
        changed_catalog['groups'][0]['questions'][0]['prompt'] += ' Additional identity requirement.'
        self.assertFalse(review(changed_catalog, state)['confirmed'])
        reordered = copy.deepcopy(state)
        reordered['answers'] = dict(reversed(list(state['answers'].items())))
        self.assertEqual(fingerprint(self.catalog, state), fingerprint(self.catalog, reordered))

    def test_invalid_answers_and_misattributed_recommendations_refuse(self):
        cases = [('unknown_id', 'Concrete', {}), ('scope', 'TBD', {}), ('scope', '  ', {}),
                 ('implementation_depth', 'maybe', {}), ('scope', 'Concrete', {'source': 'agent'}),
                 ('scope', 'Concrete', {'status': 'deferred'}), ('scope', 'Concrete', {'source': 'invented'})]
        for question_id, value, kwargs in cases:
            with self.subTest(case=(question_id, value, kwargs)), self.assertRaises(ValueError):
                answer(self.catalog, self.state, question_id, value, **kwargs)
        with self.assertRaises(ValueError): new_state(' ')
        with self.assertRaises(ValueError): validate_state(self.catalog, {'version': 9})
        malformed = copy.deepcopy(self.state); malformed['answers']['scope'] = 'malformed'
        with self.assertRaises(ValueError): validate_state(self.catalog, malformed)
        invalid = copy.deepcopy(self.state); invalid['answers']['unknown'] = {'value': 'test'}
        with self.assertRaises(ValueError): validate_state(self.catalog, invalid)

    def test_normal_generation_requires_confirmation_and_copies_only_explicit_state(self):
        destination = self.base / 'tailored'
        with self.assertRaisesRegex(ValueError, 'confirmed --intake-state'):
            generate('supplier', 'Supplier', 'Salesforce', destination)
        pending = self.save(self.state)
        with self.assertRaises(ValueError):
            generate('supplier', 'Supplier', 'Salesforce', destination, intake_state=pending)
        self.assertFalse(destination.exists())
        state = self.complete()
        confirmed = confirm(self.catalog, state, fingerprint(self.catalog, state))
        path = self.save(confirmed)
        with self.assertRaises(ValueError):
            generate('supplier', 'Supplier', 'Salesforce', destination, intake_state=path, scaffold_only=True)
        generate('supplier', 'Supplier', 'Salesforce', destination, intake_state=path)
        self.assertTrue(require_ready(destination, destination / 'config/intake.local.json')['confirmed'])
        self.assertEqual((destination / 'config/intake.local.json').stat().st_mode & 0o777, 0o600)
        scaffold = self.base / 'reference'
        generate('reference', 'Reference', 'Salesforce', scaffold, scaffold_only=True)
        self.assertFalse((scaffold / 'config/intake.local.json').exists())

    def test_material_rendering_refuses_pending_intake(self):
        root = self.base / 'reference'
        generate('reference', 'Reference', 'Salesforce', root, scaffold_only=True)
        self.save(self.state, root / 'config/intake.local.json')
        with self.assertRaises(ValueError): render_materials(root)

    def test_catalog_rejects_duplicate_ids_and_forward_conditions(self):
        root = self.base / 'catalog'; (root / 'config/intake').mkdir(parents=True)
        catalog = copy.deepcopy(self.catalog)
        catalog['groups'][0]['questions'][1]['id'] = 'project_identity'
        self.save(catalog, root / 'config/intake/questions.json')
        with self.assertRaises(ValueError): load_catalog(root)
        catalog = copy.deepcopy(self.catalog)
        catalog['groups'][0]['questions'][0]['when'] = {'question': 'later', 'equals': 'yes'}
        self.save(catalog, root / 'config/intake/questions.json')
        with self.assertRaises(ValueError): load_catalog(root)

    def test_cli_resume_confirmation_and_refusal(self):
        state_path = self.base / 'session.json'
        args = [sys.executable, 'scripts/intake.py', '--state', str(state_path)]
        def call(*extra, success=True):
            result = subprocess.run(args + list(extra), cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode == 0, success, result.stderr)
            return result
        call('start', '--brief', 'Supplier onboarding')
        self.assertEqual(state_path.stat().st_mode & 0o777, 0o600)
        call('start', '--brief', 'Another session', success=False)
        self.assertEqual(json.loads(call('next').stdout)['stage'], 'questions')
        call('answer', '--id', 'scope', '--value', 'Review supplier certificates')
        call('answer', '--id', 'scope', '--value', 'unknown', success=False)
        call('check', success=False)
        complete = self.complete(); self.save(complete, state_path)
        digest = json.loads(call('review').stdout)['fingerprint']
        call('confirm', '--fingerprint', 'stale', success=False)
        call('confirm', '--fingerprint', digest)
        self.assertEqual(json.loads(call('check').stdout),
                         {'ready_for_implementation': True, 'external_writes_authorized': False})
