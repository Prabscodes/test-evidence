"""Synthetic parser contract tests; mocked inference is not model accuracy evidence."""
import json,unittest,hashlib
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app

DATA={'mode':'llm','requirement':'f(1) must return 2.','source_before':'def f(x):\n    return x+1\n','source_after':'def f(x):\n    return x+1\n','tests_before':'def test_f():\n    assert f(1)==2\n','tests_after':'def test_f():\n    assert f(1)==2\n'}
OB='"id":"O1","description":"Required value","rationale":"The explicit case is checked.","evidence_ids":["requirement:L1","tests_after:L2"]'
def wrapped(members):return '{"obligations":[{'+OB+','+members+'}],"questions":[]}'

class DuplicateModelJsonTests(unittest.TestCase):
    def review(self,raw):
        with patch('analysis.provider.infer',return_value=(raw,{'actual_inference':True,'backend':'mock-parser-test','model':'synthetic-parser-contract'})) as infer:
            response=TestClient(app).post('/api/analyze',json=DATA)
            infer.assert_called_once()
        self.assertEqual(response.status_code,200);return response.json()
    def rejected_duplicate(self,raw):
        result=self.review(raw)
        self.assertTrue(all(o['status']=='unresolved' for o in result['obligations']))
        self.assertTrue(any('duplicate' in w.lower() for w in result['warnings']))
        self.assertIn('duplicate',result['obligations'][0]['rationale'].lower())
        self.assertEqual(result['provider']['raw_response'],raw)
        self.assertEqual(result['provider']['raw_response_sha256'],hashlib.sha256(raw.encode()).hexdigest())
        self.assertTrue(result['provider']['actual_inference'])
        self.assertTrue(result['prompt_provenance']['used_by_model']);self.assertFalse(result['execution']['performed'])
        self.assertEqual(result['obligations'][0]['evidence'],[])
    def test_contradictory_status_duplicates_rejected_in_either_order(self):
        for a,b in [('checked','gap'),('gap','checked')]:
            with self.subTest(last=b):self.rejected_duplicate(wrapped(f'"test_support":"{a}","test_support":"{b}"'))
    def test_nested_citation_duplicate_rejected_even_in_ignored_extension(self):
        self.rejected_duplicate(wrapped('"test_support":"checked","citations":[{"span":{"artifact":"tests_after","line":2,"line":9}}]'))
    def test_escaped_equivalent_keys_rejected(self):
        self.rejected_duplicate(wrapped(r'"test_support":"gap","test_\u0073upport":"checked"'))
    def test_duplicate_top_level_obligations_rejected(self):
        raw=wrapped('"test_support":"checked"');self.rejected_duplicate(raw[:-1]+',"obligations":'+json.dumps(json.loads(wrapped('"test_support":"gap"'))['obligations'])+'}')
    def test_identical_duplicate_values_still_rejected(self):
        self.rejected_duplicate(wrapped('"test_support":"checked","extra":{"quote":"same","quote":"same"}'))
    def test_valid_json_with_repeated_names_in_distinct_objects_preserved(self):
        obj=json.loads(wrapped('"test_support":"checked","extra":{"line":2}'));second=dict(obj['obligations'][0],id='O2');obj['obligations'].append(second)
        result=self.review(json.dumps(obj))
        self.assertEqual([o['status'] for o in result['obligations']],['supported','supported']);self.assertEqual(result['warnings'],[])
    def test_existing_fenced_json_path_remains_valid(self):
        raw='```json\n'+wrapped('"test_support":"checked"')+'\n```';result=self.review(raw)
        self.assertEqual(result['obligations'][0]['status'],'supported');self.assertEqual(result['provider']['raw_response'],raw)
    def test_invalid_json_does_not_get_permissive_repair(self):
        result=self.review(wrapped('"test_support":"checked"')[:-1]+',}')
        self.assertEqual(result['obligations'][0]['status'],'unresolved');self.assertTrue(result['warnings'])
    def test_long_duplicate_output_preserved_without_silent_truncation(self):
        self.rejected_duplicate(wrapped('"test_support":"gap","test_support":"checked","padding":'+json.dumps('x'*20001)))
