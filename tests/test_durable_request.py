import json,tempfile,threading,unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from scripts.durable_request import run

class DurableRequestTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.calls=0;owner=self
        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                owner.calls+=1;owner.state_at_dispatch=json.loads((owner.root/'attempt/state.json').read_text())['status']
                self.rfile.read(int(self.headers['Content-Length']));body=getattr(owner,'response_body',b'{"model_output":"raw duplicate: a,a"}')
                self.send_response(200);self.end_headers();self.wfile.write(body)
            def log_message(self,*args):pass
        self.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
        self.spec=self.root/'spec.json';self.spec.write_text(json.dumps({'url':f'http://127.0.0.1:{self.server.server_port}/review','body':{'synthetic':'no labels'},'timeout_seconds':2}))
    def tearDown(self):self.server.shutdown();self.server.server_close();self.thread.join();self.tmp.cleanup()
    def test_response_saved_exactly_before_receipt_commits(self):
        receipt=run(self.spec,self.root/'attempt')
        self.assertEqual(self.state_at_dispatch,'dispatched');self.assertEqual(self.calls,1)
        self.assertEqual((self.root/'attempt/response.body').read_bytes(),b'{"model_output":"raw duplicate: a,a"}')
        self.assertEqual(json.loads((self.root/'attempt/state.json').read_text())['status'],'response_saved')
        self.assertEqual(receipt['http_status'],200)
        self.assertEqual((self.root/'attempt/request.json').read_bytes(),self.spec.read_bytes())
    def test_existing_dispatched_attempt_never_sends_again(self):
        target=self.root/'attempt';target.mkdir();(target/'state.json').write_text('{"status":"dispatched"}')
        with self.assertRaises(FileExistsError):run(self.spec,target)
        self.assertEqual(self.calls,0)
    def test_existing_completed_attempt_never_sends_again(self):
        run(self.spec,self.root/'attempt')
        with self.assertRaises(FileExistsError):run(self.spec,self.root/'attempt')
        self.assertEqual(self.calls,1)
    def test_external_destination_rejected_before_dispatch(self):
        self.spec.write_text('{"url":"https://example.com/review","body":{}}')
        with self.assertRaises(ValueError):run(self.spec,self.root/'attempt')
        self.assertEqual(self.calls,0);self.assertFalse((self.root/'attempt').exists())
    def test_transport_failure_retains_uncertain_intent(self):
        self.server.shutdown();self.server.server_close()
        with self.assertRaises(Exception):run(self.spec,self.root/'attempt')
        state=json.loads((self.root/'attempt/state.json').read_text());self.assertEqual(state['status'],'uncertain');self.assertTrue((self.root/'attempt/request.json').is_file());self.assertFalse((self.root/'attempt/response.body').exists())

    def test_non_json_response_bytes_are_preserved_without_parsing(self):
        self.response_body=b'not JSON\n'
        receipt=run(self.spec,self.root/'attempt')
        self.assertEqual((self.root/'attempt/response.body').read_bytes(),self.response_body)
        self.assertEqual(receipt['status'],'response_saved')
    def test_journal_is_private(self):
        run(self.spec,self.root/'attempt')
        self.assertEqual((self.root/'attempt').stat().st_mode & 0o777,0o700)
        for name in ['state.json','request.json','response.body']:
            self.assertEqual((self.root/'attempt'/name).stat().st_mode & 0o777,0o600)
