from pathlib import Path
import threading, time, asyncio
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.staticfiles import StaticFiles
from analysis import AnalysisInput, analyze
from samples import SAMPLES
from fixtures import run_fixture
import provider, prompts
from public_runtime import PublicGuard
public_guard=PublicGuard()
PUBLIC_BODY_TIMEOUT_SECONDS=10
from errors import UserInputError, ProviderFailure

app=FastAPI(title='Test Evidence',version='0.1.0')
_lock=threading.Lock()
_analysis_started=None
_fixture_lock=threading.Lock()
@app.exception_handler(RequestValidationError)
async def input_validation_error(request:Request,exc:RequestValidationError):
    if public_guard.enabled():
        return JSONResponse({'detail':'Review inputs are invalid or exceed their limits. Check field types and lengths; no review was sent.'},status_code=422)
    return await request_validation_exception_handler(request,exc)
@app.middleware('http')
async def limits(request:Request,call_next):
    if request.method=='POST':
        if not public_guard.allow_post(request.client.host if request.client else 'unknown'):
            return JSONResponse({'detail':'Public request limit reached. Wait one minute; no inference was queued.'},status_code=429,headers={'Retry-After':'60'})
        length=request.headers.get('content-length')
        if length and (not length.isdigit() or int(length)>110000): return JSONResponse({'detail':'Request exceeds 110 KB.'},status_code=413)
        body=bytearray()
        try:
            async with asyncio.timeout(PUBLIC_BODY_TIMEOUT_SECONDS if public_guard.enabled() else None):
                async for chunk in request.stream():
                    body.extend(chunk)
                    if len(body)>110000:return JSONResponse({'detail':'Request exceeds 110 KB.'},status_code=413)
        except TimeoutError:
            return JSONResponse({'detail':'Request body timed out. No review was started.'},status_code=408)
        request._body=bytes(body)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    response.headers['Cache-Control']='no-store'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'"
    return response
@app.get('/')
def index():return FileResponse(Path(__file__).parent/'static'/'index.html')
@app.get('/healthz')
def health():return {'status':'ok','live_provider_configured':public_guard.status()['public_live_ready']}
@app.get('/api/status')
def status():
    running=_lock.locked()
    elapsed=round(max(0,time.monotonic()-_analysis_started),1) if running and _analysis_started is not None else None
    return {**provider.status(),**public_guard.status(),'analysis_running':running,'analysis_elapsed_seconds':elapsed}
@app.get('/api/samples')
def samples():return {'samples':SAMPLES}
@app.get('/api/prompts')
def prompt():return {'version':prompts.PROMPT_VERSION,'system':prompts.SYSTEM,'refinement':prompts.REFINEMENT,'patterns':['Persona','Few-shot','Iterative refinement']}
@app.post('/api/analyze')
def analysis(req:AnalysisInput,request:Request):
    global _analysis_started
    with public_guard.work():
        if req.mode=='llm':public_guard.require_live(request.headers.get('X-Provider-Consent'))
        if not _lock.acquire(blocking=False): raise HTTPException(429,'An analysis is running. Please retry when it finishes.')
        _analysis_started=time.monotonic()
        try:return analyze(req)
        except UserInputError as e:raise HTTPException(400,str(e))
        except ProviderFailure as e:return JSONResponse({'detail':e.message,'error_code':e.code},status_code=e.http_status)
        except Exception:raise HTTPException(502,'Inference failed. Check server provider configuration. No conclusion was accepted; secrets and provider responses are not logged.')
        finally:
            _analysis_started=None
            _lock.release()
@app.post('/api/fixtures/{sample_id}/run')
def fixture(sample_id:str):
    with public_guard.work():
        if not _fixture_lock.acquire(blocking=False):raise HTTPException(429,'A trusted fixture is already running. Please retry when it finishes.')
        try:return run_fixture(sample_id)
        except ValueError:raise HTTPException(404,'Unknown bundled fixture. Uploaded code cannot be executed.')
        finally:_fixture_lock.release()
app.mount('/static',StaticFiles(directory=Path(__file__).parent/'static'),name='static')
