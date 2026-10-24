import json
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app import app
from consistency import acknowledges_missing_authority

class ConsistencyTests(unittest.TestCase):
    def test_positive_domains(self):
        for rationale in [
            'The requirement does not specify whether overnight delivery is included.',
            'The specification is ambiguous about retry delays.',
            'The contract leaves the maximum image size undefined.',
            'The cache replacement policy is unspecified.',
            'The expected outcome remains unclear for overlapping bookings.',
        ]:
            with self.subTest(rationale=rationale):self.assertTrue(acknowledges_missing_authority(rationale))

    def test_negative_domains_and_negation(self):
        for rationale in [
            'The tests do not specify the delivery boundary.',
            'The requirement explicitly specifies a maximum size of ten.',
            'The requirement is not ambiguous about retry delays.',
            'The specification does not require background retries.',
            'The explicit policy is checked by the after-test assertion.',
        ]:
            with self.subTest(rationale=rationale):self.assertFalse(acknowledges_missing_authority(rationale))

    def test_api_withholds_contradictory_claim_and_retains_raw(self):
        data={'mode':'llm','requirement':'Retry a transient failure. Delay policy is not specified.', 'tests_after':'assert retry_delay() == 1'}
        for support in ['checked','gap','unknown']:
            raw=json.dumps({'obligations':[{'id':'O1','description':'Retry delay is one second','test_support':support,'rationale':'The requirement does not specify the retry delay.','evidence_ids':['requirement:L1','tests_after:L1']}],'questions':[]})
            with self.subTest(support=support),patch('analysis.provider.infer',return_value=(raw,{'actual_inference':True})):
                result=TestClient(app).post('/api/analyze',json=data).json()
                self.assertEqual(result['obligations'][0]['status'],'unresolved')
                self.assertEqual(result['obligations'][0]['origin'],'deterministic_consistency_guard')
                self.assertEqual(result['obligations'][0]['description'],'Expected policy requires authoritative clarification')
                self.assertTrue(result['questions'])
                self.assertEqual(result['provider']['raw_response'],raw)
