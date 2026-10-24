import unittest
from unittest.mock import patch

from fixtures import run_fixture, _run
from samples import SAMPLES


class FixtureTests(unittest.TestCase):
    def test_all_samples_have_expected_outcomes(self):
        expected = {
            'missing_regression': [0, 0, 1, 0, 1],
            'legitimate_refactor': [0, 0, 0, 0],
            'missing_spec': [0, 0, 1, 1],
            'supported_boundary': [0, 0, 0, 0],
        }
        for sample_id, returncodes in expected.items():
            with self.subTest(sample_id=sample_id):
                result = run_fixture(sample_id)
                self.assertEqual([run['returncode'] for run in result['results']], returncodes)
                self.assertEqual(result['origin'], 'actual_execution')
                self.assertTrue(result['baseline_valid'])
                for run in result['results']:
                    self.assertEqual(len(run['revision']['combined_sha256']), 64)
                    self.assertTrue(run['command'])
                    self.assertFalse(run['timed_out'])

    def test_oracle_failure_is_assertion_not_harness_error(self):
        result = run_fixture('missing_regression')
        oracle = result['results'][-1]
        self.assertEqual(oracle['label'], 'independent_requirement_oracle')
        self.assertEqual(oracle['outcome'], 'assertion_failure')
        self.assertGreater(oracle['counts']['assertion_failures'], 0)
        self.assertEqual(oracle['counts']['errors'], 0)
        self.assertFalse(oracle['harness_error'])
        self.assertGreater(oracle['counts']['tests_run'], 0)

    def test_unknown_ids_rejected_before_execution(self):
        for value in ('../subject.py', '__import__("os")', '', None, {}, ['missing_regression']):
            with self.subTest(value=value), patch('fixtures.subprocess.run') as run:
                with self.assertRaises(ValueError):
                    run_fixture(value)
                run.assert_not_called()

    def test_executable_snapshot_not_mutable_through_samples(self):
        sample = SAMPLES[0]
        old = sample['source_after']
        try:
            sample['source_after'] = 'raise RuntimeError("injected")'
            result = run_fixture(sample['id'])
            self.assertEqual(result['results'][1]['returncode'], 0)
            self.assertNotIn('injected', result['results'][1]['stderr'])
        finally:
            sample['source_after'] = old

    def test_subprocess_environment_contains_no_inherited_secret(self):
        import subprocess
        original = subprocess.run
        observed = []
        def capture(*args, **kwargs):
            observed.append(kwargs['env'])
            return original(*args, **kwargs)
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'secret-do-not-inherit'}), patch('fixtures.subprocess.run', side_effect=capture):
            run_fixture('supported_boundary')
        self.assertTrue(observed)
        self.assertTrue(all('OPENAI_API_KEY' not in env for env in observed))

    def test_harness_errors_are_not_assertion_failures(self):
        import json
        import subprocess
        counts = {'tests_run':1, 'assertion_failures':0, 'errors':1, 'successful':False}
        fake = subprocess.CompletedProcess([], 1, json.dumps(counts), 'ImportError')
        with patch('fixtures.subprocess.run', return_value=fake):
            result = _run('mock_harness_error', '', '')
        self.assertEqual(result['outcome'], 'harness_error')
        self.assertFalse(result['observed_failure'])
        self.assertTrue(result['harness_error'])

    def test_timeout_is_not_assertion_failure(self):
        import subprocess
        with patch('fixtures.subprocess.run', side_effect=subprocess.TimeoutExpired('mock', 5)):
            result = _run('mock_timeout', '', '')
        self.assertEqual(result['outcome'], 'timeout')
        self.assertIsNone(result['observed_failure'])

    def test_zero_tests_is_not_passing_evidence(self):
        import json
        import subprocess
        counts = {'tests_run':0, 'assertion_failures':0, 'errors':0, 'successful':True}
        fake = subprocess.CompletedProcess([], 0, json.dumps(counts), '')
        with patch('fixtures.subprocess.run', return_value=fake):
            result = _run('mock_empty_suite', '', '')
        self.assertEqual(result['outcome'], 'no_tests')

    def test_hashes_are_reproducible(self):
        first = run_fixture('supported_boundary')
        second = run_fixture('supported_boundary')
        self.assertEqual(first['revision'], second['revision'])

if __name__ == '__main__':
    unittest.main()
