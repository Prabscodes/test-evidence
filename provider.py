"""No credentials are returned, logged, or embedded in exports."""
import os, json, time, threading, math, re, ipaddress
from urllib.parse import urlparse
import httpx
from prompts import messages, PROMPT_VERSION
from errors import UserInputError, ProviderFailure
_lock=threading.Lock()
_model=None
_tokenizer=None

def _http_timeout_seconds():
    try:
        value=int(os.getenv('TE_TIMEOUT_SECONDS','90'))
    except (ValueError,TypeError):
        raise UserInputError('TE_TIMEOUT_SECONDS must be an integer from 30 to 300 seconds.') from None
    if os.getenv('TE_PUBLIC')=='1' and value>90:
        raise UserInputError('Public provider timeout must be from30 to90 seconds.')
    if not 30<=value<=300:
        raise UserInputError('TE_TIMEOUT_SECONDS must be an integer from 30 to 300 seconds.')
    return value

def _http_temperature():
    try:
        value=float(os.getenv('TE_TEMPERATURE','0'))
    except (ValueError,TypeError):
        raise UserInputError('TE_TEMPERATURE must be a finite number from 0 to 2.') from None
    if not math.isfinite(value) or not 0<=value<=2:
        raise UserInputError('TE_TEMPERATURE must be a finite number from 0 to 2.')
    return value

def _validate_api_base(value):
    """Validate parsed authority, never a trusted-looking textual URL prefix."""
    message='Provider URL must have a valid host/port, no userinfo/query/fragment, and HTTPS or exact loopback HTTP.'
    try:
        if not isinstance(value,str) or not value or any(ord(c)<=32 or ord(c)==127 for c in value):
            raise ValueError()
        parsed=urlparse(value)
        host=parsed.hostname
        port=parsed.port  # Validates malformed/out-of-range port syntax.
        if parsed.scheme not in ('http','https') or not host or parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
            raise ValueError()
        if parsed.netloc.endswith(':') or (port is not None and not 1<=port<=65535):
            raise ValueError()
        if ':' in host:
            ipaddress.IPv6Address(host)
        elif not all(re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?',label) for label in host.split('.')):
            raise ValueError()
        loopback=host in ('localhost','127.0.0.1','::1')
        if parsed.scheme=='http' and not loopback:
            raise ValueError()
    except (ValueError,TypeError):
        raise UserInputError(message) from None
    return value.rstrip('/'),loopback

def status():
    backend=os.getenv('TE_PROVIDER','none')
    try: timeout=_http_timeout_seconds()
    except UserInputError: timeout=None
    try: temperature=_http_temperature()
    except UserInputError: temperature=None
    try: _,is_loopback=_validate_api_base(os.getenv('TE_API_BASE','')); endpoint_valid=True
    except UserInputError: is_loopback=False; endpoint_valid=False
    enabled=os.getenv('TE_ALLOW_REMOTE')=='1'
    return {'endpoint_config_valid':endpoint_valid if backend=='openai-compatible' else None,'http_temperature':temperature,'temperature_config_valid':temperature is not None,'http_timeout_seconds':timeout,'timeout_config_valid':timeout is not None,'backend':backend,'configured':backend=='local' or (backend=='openai-compatible' and bool(os.getenv('TE_API_BASE'))),'model':os.getenv('TE_MODEL','Qwen/Qwen2.5-0.5B-Instruct') if backend=='local' else os.getenv('TE_MODEL','not configured'),'processing_location':'local_model' if backend=='local' else ('loopback_endpoint' if is_loopback else 'external_endpoint' if backend=='openai-compatible' else 'none'),'endpoint_calls_enabled':backend=='local' or enabled,'remote_processing_enabled':backend=='openai-compatible' and not is_loopback and enabled,'execution':'Only explicitly selected bundled fixtures can run.'}


def infer(data):
    global _model,_tokenizer
    config=status(); started=time.monotonic(); msgs=messages(data)
    if config['backend']=='local':
        with _lock:
            import torch
            from transformers import AutoTokenizer, AutoModelForCausalLM
            torch.set_num_threads(min(4,os.cpu_count() or 1))
            if _model is None:
                name=config['model']
                _tokenizer=AutoTokenizer.from_pretrained(name,trust_remote_code=False)
                _model=AutoModelForCausalLM.from_pretrained(name,trust_remote_code=False,torch_dtype=torch.float32)
                _model.eval()
            prompt=_tokenizer.apply_chat_template(msgs,tokenize=False,add_generation_prompt=True)
            inputs=_tokenizer(prompt,return_tensors='pt')
            if inputs.input_ids.shape[1]>7000:
                raise UserInputError('Local model input exceeds 7000 tokens; shorten the artifacts.')
            with torch.inference_mode():
                output=_model.generate(**inputs,max_new_tokens=min(1800,max(128,int(os.getenv('TE_MAX_TOKENS','768')))),max_time=90,do_sample=False,pad_token_id=_tokenizer.eos_token_id)
            raw=_tokenizer.decode(output[0][inputs.input_ids.shape[1]:],skip_special_tokens=True)
    elif config['backend']=='openai-compatible' and config['configured']:
        if os.getenv('TE_ALLOW_REMOTE')!='1':
            raise UserInputError('Remote calls are disabled. Explicitly authorize remote processing and possible cost, then set TE_ALLOW_REMOTE=1 on the server.')
        base,is_loopback=_validate_api_base(os.environ['TE_API_BASE'])
        headers={}
        if os.getenv('TE_API_KEY'): headers['Authorization']='Bearer '+os.environ['TE_API_KEY']
        with httpx.Client(timeout=_http_timeout_seconds(),follow_redirects=False,trust_env=not is_loopback) as client:
            try:
                response=client.post(base+'/chat/completions',headers=headers,json={'model':config['model'],'messages':msgs,'temperature':_http_temperature(),'max_tokens':min(1024 if os.getenv('TE_PUBLIC')=='1' else 1800,max(128,int(os.getenv('TE_MAX_TOKENS','768')))), 'response_format':{'type':'json_object'}})
                response.raise_for_status()
            except httpx.TimeoutException:
                raise ProviderFailure('timeout') from None
            except httpx.HTTPStatusError as exc:
                code = {400:'input_rejected', 413:'input_rejected', 422:'input_rejected', 401:'access_denied', 403:'access_denied', 404:'model_not_loaded', 503:'unavailable'}.get(exc.response.status_code, 'http_failure')
                raise ProviderFailure(code) from None
            except httpx.RequestError:
                raise ProviderFailure('unavailable') from None
            raw=response.json()['choices'][0]['message']['content']
            # Never expose a server credential echoed by an untrusted upstream.
            key=os.getenv('TE_API_KEY')
            if key and isinstance(raw,str) and key in raw:
                raise ProviderFailure('http_failure')
    else:
        raise UserInputError('No LLM configured. Select labelled demo mode, or configure a local model. No inference has run.')
    return raw, {'http_temperature':config['http_temperature'] if config['backend']=='openai-compatible' else None,'http_timeout_seconds':config['http_timeout_seconds'] if config['backend']=='openai-compatible' else None,'backend':config['backend'],'model':config['model'],'elapsed_seconds':round(time.monotonic()-started,3),'actual_inference':True,'prompt_version':PROMPT_VERSION,'prompt_patterns':['persona','few-shot','iterative refinement']}
