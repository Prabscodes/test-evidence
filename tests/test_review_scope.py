"""Scope disclosure contracts. Mocked inference is not model-quality evidence."""
import json,re,unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app
from prompts import SYSTEM
from tests.test_api import payload

class ReviewScopeTests(unittest.TestCase):
    def test_demo_export_discloses_hand_authored_partial_scope(self):
        result=TestClient(app).post('/api/analyze',json=payload()).json()
        self.assertIn('review_scope',result,'Every review response/export must disclose partial scope');scope=result['review_scope']
        self.assertEqual(scope['coverage'],'partial')
        self.assertFalse(scope['complete_requirement_coverage'])
        self.assertIsNone(scope['prompt_obligation_limit'])
        self.assertEqual(scope['listed_obligation_count'],len(result['obligations']))
        self.assertIn('hand-authored',scope['note'])
        self.assertIn('unlisted',scope['note'])
    def test_llm_scope_limit_matches_actual_prompt_and_never_claims_all_requirements(self):
        raw={'obligations':[{'id':'O1','description':'Explicit boundary','test_support':'gap','rationale':'Missing equality assertion.','evidence_ids':['requirement:L1','tests_after:L6']}],'questions':[]}
        data=payload(mode='llm',requirement='Age eighteen is eligible. Age seventeen is ineligible. Invalid ages must raise. Negative ages must raise. Noninteger ages must raise.')
        with patch('analysis.provider.infer',return_value=(json.dumps(raw),{'actual_inference':True,'backend':'synthetic-scope-test'})):
            response=TestClient(app).post('/api/analyze',json=data)
        self.assertEqual(response.status_code,200);result=response.json();self.assertIn('review_scope',result,'Every review response/export must disclose partial scope');scope=result['review_scope']
        self.assertEqual(scope['prompt_obligation_limit'],int(re.search(r'at most (\d+) obligations',SYSTEM).group(1)))
        self.assertEqual(scope['prompt_obligation_limit'],3)
        self.assertFalse(scope['complete_requirement_coverage'])
        self.assertEqual(scope['listed_obligation_count'],1)
        self.assertIn('unlisted',scope['note'])
        self.assertIn('at most 3',scope['note'])
    def test_disobedient_extra_output_is_counted_honestly_not_silently_truncated(self):
        raw={'obligations':[{'id':f'O{i}','description':f'Case {i}','test_support':'unknown','rationale':'Needs inspection.','evidence_ids':[]} for i in range(1,5)],'questions':[]}
        with patch('analysis.provider.infer',return_value=(json.dumps(raw),{'actual_inference':True,'backend':'synthetic-scope-test'})):
            result=TestClient(app).post('/api/analyze',json=payload(mode='llm')).json()
        self.assertEqual(len(result['obligations']),4)
        self.assertIn('review_scope',result,'Every review response/export must disclose partial scope')
        self.assertEqual(result['review_scope']['listed_obligation_count'],4)
        self.assertEqual(result['review_scope']['prompt_obligation_limit'],3)
        self.assertFalse(result['review_scope']['complete_requirement_coverage'])
