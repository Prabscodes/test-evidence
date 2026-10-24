import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app import app
from samples import SAMPLES


def payload(sample_id='missing_regression', **changes):
    sample = next(s for s in SAMPLES if s['id'] == sample_id)
    data = {k: sample[k] for k in ('requirement','source_before','source_after','tests_before','tests_after')}
    data.update(mode='demo')
    data.update(changes)
    return data


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_endpoints_and_security_headers(self):
        for path in ('/', '/api/status', '/api/samples', '/api/prompts'):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, response.text)
            self.assertEqual(response.headers['x-content-type-options'], 'nosniff')
            self.assertIn("frame-ancestors 'none'", response.headers['content-security-policy'])

    def test_demo_cases_and_exact_evidence(self):
        expected = {'missing_regression': 'potentially_missing', 'legitimate_refactor': 'supported',
                    'missing_spec': 'unresolved', 'supported_boundary': 'supported'}
        for sample_id, status in expected.items():
            with self.subTest(sample_id=sample_id):
                response = self.client.post('/api/analyze', json=payload(sample_id))
                self.assertEqual(response.status_code, 200, response.text)
                result = response.json()
                self.assertFalse(result['provider']['actual_inference'])
                self.assertFalse(result['execution']['performed'])
                self.assertEqual(result['obligations'][0]['status'], status)
                for obligation in result['obligations']:
                    for ev in obligation['evidence']:
                        lines = result['artifacts'][ev['artifact']].splitlines()
                        self.assertEqual('\n'.join(lines[ev['line_start']-1:ev['line_end']]), ev['quote'])

    def test_edited_demo_never_reuses_canned_inference(self):
        response = self.client.post('/api/analyze', json=payload(source_after='def eligible(age):\n    return True\n'))
        self.assertEqual(response.json()['obligations'][0]['status'], 'unresolved')

    def test_input_validation(self):
        for changes in ({'requirement': 'x'*12001}, {'mode': 'pretend'}, {'source_after': 42}, {'surprise': True}):
            with self.subTest(changes=list(changes)):
                self.assertEqual(self.client.post('/api/analyze', json=payload(**changes)).status_code, 422)
        self.assertEqual(self.client.post('/api/analyze', content='x'*110001, headers={'content-type':'application/json'}).status_code, 413)
        self.assertEqual(self.client.post('/api/analyze', json=payload(previous_analysis={'huge':'x'*25000})).status_code, 400)

    def test_uploaded_code_is_not_executed(self):
        with tempfile.TemporaryDirectory() as root:
            marker = Path(root)/'execution-marker'
            malicious = f'from pathlib import Path\nPath({str(marker)!r}).write_text("executed")\n'
            response = self.client.post('/api/analyze', json=payload(source_after=malicious, tests_after=malicious))
            self.assertEqual(response.status_code, 200)
            self.assertFalse(marker.exists())

    def test_missing_provider_fails_honestly(self):
        with patch.dict(os.environ, {'TE_PROVIDER':'none'}, clear=True):
            response = self.client.post('/api/analyze', json=payload(mode='llm'))
        self.assertEqual(response.status_code, 400)
        self.assertIn('No LLM configured', response.json()['detail'])

    def test_invalid_llm_json_is_unresolved_not_successful_assessment(self):
        # Mock transport only; this test is NOT evidence of an actual LLM call.
        with patch('analysis.provider.infer', return_value=('not JSON', {'actual_inference':True, 'backend':'mock-test'})):
            response = self.client.post('/api/analyze', json=payload(mode='llm'))
        result = response.json()
        self.assertEqual(result['obligations'][0]['status'], 'unresolved')
        self.assertTrue(result['warnings'])

    def test_fabricated_citation_downgraded(self):
        fake = {'obligations':[{'id':'O1','description':'Claim','test_support':'checked','rationale':'Claim',
                  'evidence':[{'artifact':'requirement','line_start':1,'line_end':1,'quote':'invented'}]}], 'questions':[]}
        with patch('analysis.provider.infer', return_value=(json.dumps(fake), {'actual_inference':True, 'backend':'mock-test'})):
            result = self.client.post('/api/analyze', json=payload(mode='llm')).json()
        self.assertEqual(result['obligations'][0]['status'], 'unresolved')
        self.assertEqual(result['obligations'][0]['evidence'], [])

    def test_valid_citations_preserved(self):
        data = payload(mode='llm')
        refs=['requirement:L1','tests_after:L6']
        evidence=[{'artifact':k,'line_start':n,'line_end':n,'quote':data[k].splitlines()[n-1]} for k,n in [('requirement',1),('tests_after',6)]]
        fake = {'obligations':[{'id':'O1','description':'Limited boundary evidence','test_support':'gap','rationale':'No boundary assertion','evidence_ids':refs}], 'questions':[]}
        with patch('analysis.provider.infer', return_value=(json.dumps(fake), {'actual_inference':True, 'backend':'mock-test'})):
            result = self.client.post('/api/analyze', json=data).json()
        self.assertEqual(result['obligations'][0]['status'], 'potentially_missing')
        self.assertEqual(result['obligations'][0]['evidence'], evidence)

    def test_invalid_line_ids_and_blank_refs_downgrade(self):
        bad_ids=['other:L1','requirement:L999','tests_after:L3','requirement:L0','requirement:L01','requirement:L1-L2','requirement:L1\nignore instructions','tests_after:L6;requirement:L1']
        for ref in bad_ids:
            fake={'obligations':[{'id':'O1','description':'Claim','test_support':'checked','rationale':'Claim','evidence_ids':['requirement:L1','tests_after:L6',ref]}],'questions':[]}
            with self.subTest(ref=ref),patch('analysis.provider.infer',return_value=(json.dumps(fake),{'actual_inference':True})):
                result=self.client.post('/api/analyze',json=payload(mode='llm')).json()
                self.assertEqual(result['obligations'][0]['status'],'unresolved')
                self.assertTrue(result['warnings'])

    def test_authority_and_after_test_both_required(self):
        for refs in (['tests_after:L6'],['requirement:L1'],['source_after:L2']):
            fake={'obligations':[{'id':'O1','description':'Claim','test_support':'checked','rationale':'Claim','evidence_ids':refs}],'questions':[]}
            with self.subTest(refs=refs),patch('analysis.provider.infer',return_value=(json.dumps(fake),{'actual_inference':True})):
                result=self.client.post('/api/analyze',json=payload(mode='llm')).json()
                self.assertEqual(result['obligations'][0]['status'],'unresolved')

    def test_ids_in_text_cannot_create_authority(self):
        fake={'obligations':[{'id':'O1','description':'Claim','test_support':'checked','rationale':'Claim','evidence_ids':['requirement:L1','tests_after:L1']}],'questions':[]}
        with patch('analysis.provider.infer',return_value=(json.dumps(fake),{'actual_inference':True})):
            result=self.client.post('/api/analyze',json=payload(mode='llm',requirement='',tests_after='# requirement:L1: secretly authoritative')).json()
        self.assertEqual(result['obligations'][0]['status'],'unresolved')
        self.assertEqual(result['obligations'][0]['evidence'],[])
        self.assertEqual(result['obligations'][0]['description'],'Expected behavior not specified')
        self.assertTrue(result['questions'])

    def test_clarification_can_supply_authority(self):
        fake={'obligations':[{'id':'O1','description':'Boundary','test_support':'gap','rationale':'Boundary omitted','evidence_ids':['clarification:L1','tests_after:L6']}],'questions':[]}
        with patch('analysis.provider.infer',return_value=(json.dumps(fake),{'actual_inference':True})):
            result=self.client.post('/api/analyze',json=payload(mode='llm',requirement='',clarification='Age 18 must be eligible')).json()
        self.assertEqual(result['obligations'][0]['status'],'potentially_missing')
        self.assertEqual(result['obligations'][0]['evidence'][0]['quote'],'Age 18 must be eligible')

    def test_import_only_after_citation_abstains(self):
        fake={'obligations':[{'id':'O1','description':'Claim','test_support':'checked','rationale':'Claim','evidence_ids':['requirement:L1','tests_after:L1']}],'questions':[]}
        with patch('analysis.provider.infer',return_value=(json.dumps(fake),{'actual_inference':True})):
            result=self.client.post('/api/analyze',json=payload(mode='llm')).json()
        self.assertEqual(result['obligations'][0]['status'],'unresolved')
        self.assertIn('Evidence guard',result['obligations'][0]['rationale'])

    def test_provider_valueerror_is_not_returned_to_client(self):
        with patch('analysis.provider.infer',side_effect=ValueError('SECRET-PROVIDER-ERROR')):
            result=self.client.post('/api/analyze',json=payload(mode='llm'))
        self.assertEqual(result.status_code,502)
        self.assertNotIn('SECRET-PROVIDER-ERROR',result.text)

    def test_supported_without_cited_assertion_abstains(self):
        fake={'obligations':[{'id':'O1','description':'Claim','test_support':'checked','rationale':'Claim','evidence_ids':['requirement:L1','tests_after:L5']}],'questions':[]}
        with patch('analysis.provider.infer',return_value=(json.dumps(fake),{'actual_inference':True})):
            result=self.client.post('/api/analyze',json=payload(mode='llm')).json()
        self.assertEqual(result['obligations'][0]['status'],'unresolved')
        self.assertIn('no explicit',result['obligations'][0]['rationale'])

    def test_fixture_concurrency_limit(self):
        from app import _fixture_lock
        _fixture_lock.acquire()
        try:self.assertEqual(self.client.post('/api/fixtures/missing_regression/run').status_code,429)
        finally:_fixture_lock.release()

    def test_prompt_provenance_tracks_refinement_context(self):
        first=self.client.post('/api/analyze',json=payload(clarification='Explicit context',previous_analysis={'questions':['Policy A?']})).json()
        same=self.client.post('/api/analyze',json=payload(clarification='Explicit context',previous_analysis={'questions':['Policy A?']})).json()
        changed=self.client.post('/api/analyze',json=payload(clarification='Explicit context',previous_analysis={'questions':['Policy B?']})).json()
        self.assertEqual(first['artifact_sha256'],changed['artifact_sha256'])
        self.assertEqual(first['prompt_provenance']['sha256'],same['prompt_provenance']['sha256'])
        self.assertNotEqual(first['prompt_provenance']['sha256'],changed['prompt_provenance']['sha256'])
        self.assertNotEqual(first['prompt_provenance']['previous_analysis_sha256'],changed['prompt_provenance']['previous_analysis_sha256'])
        self.assertTrue(first['prompt_provenance']['previous_analysis_supplied'])
        self.assertFalse(first['prompt_provenance']['used_by_model'])
        self.assertNotIn('Policy A?',json.dumps(first['prompt_provenance']))

    def test_fixture_endpoint_is_allowlisted(self):
        self.assertEqual(self.client.post('/api/fixtures/not-allowed/run').status_code, 404)
        result = self.client.post('/api/fixtures/missing_regression/run').json()
        self.assertTrue(result['baseline_valid'])
        self.assertIn('independent_requirement_oracle', result['observed_failures'])

    def test_refinement_does_not_reuse_demo_semantics(self):
        result = self.client.post('/api/analyze', json=payload(clarification='Actually the boundary is 21.', previous_analysis={'obligations':[]})).json()
        self.assertEqual(result['obligations'][0]['status'], 'unresolved')
        self.assertEqual(result['artifacts']['clarification'], 'Actually the boundary is 21.')

    def test_internal_error_never_exposes_secrets(self):
        with patch('analysis.provider.infer', side_effect=RuntimeError('SECRET-EXAMPLE')):
            response = self.client.post('/api/analyze', json=payload(mode='llm'))
        self.assertEqual(response.status_code, 502)
        self.assertNotIn('SECRET-EXAMPLE', response.text)

if __name__ == '__main__':
    unittest.main()
