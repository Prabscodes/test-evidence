import hashlib, json, re, uuid, subprocess, sys, os
from pathlib import Path
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Annotated
import provider
from prompts import messages, PROMPT_VERSION
from consistency import acknowledges_missing_authority
from errors import UserInputError

ARTIFACTS=('requirement','source_before','source_after','tests_before','tests_after','clarification')
DISCLAIMER='Evidence review, not a proof of correctness. Uploaded code is never executed. Supported means limited visible evidence only.'
class AnalysisInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    requirement: str=Field(default='',max_length=12000)
    source_before: str=Field(default='',max_length=16000)
    source_after: str=Field(default='',max_length=16000)
    tests_before: str=Field(default='',max_length=16000)
    tests_after: str=Field(default='',max_length=16000)
    clarification: str=Field(default='',max_length=4000)
    mode: Literal['demo','llm']='demo'
    previous_analysis: dict|None=None

class Evidence(BaseModel):
    model_config=ConfigDict(extra='forbid')
    artifact: Literal['requirement','source_before','source_after','tests_before','tests_after','clarification']
    line_start: int=Field(ge=1)
    line_end: int=Field(ge=1)
    quote: str=Field(max_length=16000)
class Obligation(BaseModel):
    model_config=ConfigDict(extra='ignore')
    id: str=Field(max_length=40)
    description: str=Field(max_length=2000)
    test_support: Literal['checked','gap','unknown']
    rationale: str=Field(max_length=4000)
    evidence_ids: list[Annotated[str, Field(max_length=80)]]=Field(default_factory=list,max_length=20)
class ModelResult(BaseModel):
    model_config=ConfigDict(extra='ignore')
    obligations: list[Obligation]=Field(min_length=1,max_length=20)
    questions: list[str]=Field(default_factory=list,max_length=20)

def cite(data,key):
    lines=data.get(key,'').splitlines()
    return {'artifact':key,'line_start':1,'line_end':len(lines),'quote':'\n'.join(lines)} if lines else None

def observations(data):
    out=[]
    for key in ('source_before','source_after','tests_before','tests_after'):
        try:
            result=subprocess.run([sys.executable,'-I',str(Path(__file__).parent/'ast_check.py')],input=data[key],capture_output=True,text=True,timeout=3,env={'PATH':os.defpath})
            counts=json.loads(result.stdout)
            asserts=counts['asserts']; unittest_asserts=counts['assert_methods']
            out.append({'kind':'deterministic_static','detail':f'{key}: valid Python syntax; {asserts} assert statements; {unittest_asserts} assert-prefixed method calls. Counts do not establish behavior coverage.'})
        except (ValueError,KeyError,subprocess.TimeoutExpired):
            out.append({'kind':'deterministic_static','detail':f'{key}: Python syntax could not be parsed. No code was executed.'})
    return out

def demo(data):
    from samples import SAMPLES
    match=next((s for s in SAMPLES if all(data.get(k,'')==s.get(k,'') for k in ARTIFACTS[:-1]) and not data['clarification']),None)
    status='unresolved'; rationale='Custom input requires LLM review or human assessment. This deterministic demo does not infer semantic test adequacy.'
    questions=['What exact expected outputs and boundary behavior are authoritative?']
    if match:
        sid=match['id']
        if sid=='missing_regression': status='potentially_missing'; rationale='Hand-authored demonstration: the after-tests omit the required boundary behavior. Run the bundled fixture to see a controlled witness.'; questions=[]
        elif sid in ('legitimate_refactor','supported_boundary'): status='supported'; rationale='Hand-authored demonstration: explicit checks of the specified behavior remain visible. This is not a general correctness guarantee.'; questions=[]
        else: rationale='No authoritative requirement was supplied. Old tests alone do not establish intended behavior.'
    ev=[x for k in ('requirement','tests_before','tests_after') if (x:=cite(data,k))]
    return {'obligations':[{'id':'O1','description':data['requirement'] or 'Intended behavior requires an explicit requirement','status':status,'rationale':rationale,'evidence':ev}],'questions':questions}

class DuplicateJSONKey(ValueError):
    """The model supplied ambiguous object members, including nested objects."""


def _unique_json_object(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise DuplicateJSONKey('Duplicate JSON object keys are not allowed.')
        result[key]=value
    return result


def analyze(request):
    data=request.model_dump(); warnings=[]
    if request.previous_analysis and len(json.dumps(request.previous_analysis))>24000:
        raise UserInputError('Previous analysis exceeds 24000 characters.')
    if request.mode=='llm':
        raw,meta=provider.infer(data)
        clean=raw.strip()
        if clean.startswith('```'): clean=re.sub(r'^```(?:json)?\s*|\s*```$','',clean)
        try:
            # Decode keys recursively before the unchanged schema validation.
            # This also catches escaped-equivalent keys and ignored extensions.
            json.loads(clean,object_pairs_hook=_unique_json_object)
            parsed=ModelResult.model_validate_json(clean).model_dump()
            for ob in parsed['obligations']:
                ob['status']={'checked':'supported','gap':'potentially_missing','unknown':'unresolved'}[ob.pop('test_support')]
        except Exception as exc:
            duplicate=isinstance(exc,DuplicateJSONKey)
            reason='The model returned duplicate JSON object keys, making its output ambiguous. No model claim has been accepted.' if duplicate else 'The model ran but did not return valid structured evidence. No model claim has been accepted.'
            parsed={'obligations':[{'id':'O1','description':'Model output needs human review','status':'unresolved','rationale':reason,'evidence':[]}],'questions':['Please refine the requirement or use a stronger configured model.']}
            warnings.append('Model response contains duplicate JSON object keys; all conclusions remain unresolved.' if duplicate else 'Model response failed schema validation; all conclusions remain unresolved.')
        # Keep the exact untrusted output, including rejected duplicates, for audit/export.
        meta['raw_response']=raw
        meta['raw_response_sha256']=hashlib.sha256(raw.encode()).hexdigest()
    else:
        parsed=demo(data); meta={'backend':'deterministic-demo','actual_inference':False,'model':'Hand-authored fixture examples only'}
    missing_authority=not (data['requirement'].strip() or data['clarification'].strip())
    if request.mode=='llm' and missing_authority:
        parsed={'obligations':[{'id':'O1','description':'Expected behavior not specified','status':'unresolved','rationale':'No authoritative requirement or clarification was supplied. Model-proposed behavior is not accepted as a specification; the original response remains available for inspection.','evidence_ids':[]}],'questions':['What exact behavior and expected outcomes should these tests enforce?']}
        warnings.append('Authority guard: model-proposed requirements withheld until you supply or confirm the intended behavior.')
    for ob in parsed['obligations']:
        accepted=[]; rejected=0
        if request.mode=='llm':
            for ref in ob.pop('evidence_ids',[]):
                match=re.fullmatch(r'(requirement|source_before|source_after|tests_before|tests_after|clarification):L([1-9][0-9]*)',ref)
                if not match:
                    rejected+=1; continue
                artifact,line_number=match.group(1),int(match.group(2))
                lines=data[artifact].splitlines()
                if line_number>len(lines) or not lines[line_number-1].strip():
                    rejected+=1; continue
                ev={'artifact':artifact,'line_start':line_number,'line_end':line_number,'quote':lines[line_number-1]}
                if ev not in accepted: accepted.append(ev)
        else:
            accepted=ob.get('evidence',[])
        ob['evidence']=accepted
        authority=any(x['artifact'] in ('requirement','clarification') and x['quote'].strip() for x in accepted)
        after=any(x['artifact']=='tests_after' and any(line.strip() and not re.match(r'^(?:import\s|from\s|#)',line.lstrip()) for line in x['quote'].splitlines()) for x in accepted)
        explicit_check=any(x['artifact']=='tests_after' and re.search(r'\bassert\b|\.assert[A-Za-z_]*\s*\(|\bpytest\.(?:raises|warns)\s*\(',x['quote']) for x in accepted)
        if ob['status']=='supported' and not explicit_check:
            ob['status']='unresolved'
            ob['rationale']+=' Evidence guard: no explicit assertion/expected-exception check was cited. Helper or implicit oracles may be valid but require further evidence.'
            warnings.append(f"{ob['id']}: no cited explicit after-test check; this is an evidence limitation, not a finding of weakness.")
        if rejected or (ob['status']!='unresolved' and (not authority or not after)):
            ob['status']='unresolved'; ob['rationale']+=' Evidence guard: invalid or insufficient authoritative/after-test citations (imports/comments alone are not test evidence); human review required.'
            warnings.append(f"{ob['id']}: downgraded to unresolved by evidence validation.")
        ob['origin']='deterministic_authority_guard' if request.mode=='llm' and missing_authority else ('llm_inference' if request.mode=='llm' else 'labelled_demo')
        if request.mode=='llm' and not missing_authority and acknowledges_missing_authority(ob['rationale']):
            ob['status']='unresolved'
            ob['description']='Expected policy requires authoritative clarification'
            ob['rationale']="Consistency guard: the model's own explanation explicitly acknowledges unspecified or ambiguous authority. Any unsupported policy claim is withheld. Original model output remains available for inspection; this wording check is not semantic proof."
            ob['origin']='deterministic_consistency_guard'
            question='What authoritative expected outcome applies to this unspecified or ambiguous behavior?'
            if question not in parsed['questions']: parsed['questions'].append(question)
            warnings.append(f"{ob['id']}: model acknowledged insufficient authority; clarification required by consistency guard.")
    hashes={k:hashlib.sha256(data[k].encode()).hexdigest() for k in ARTIFACTS}
    canonical_prompt=json.dumps(messages(data),ensure_ascii=False,sort_keys=True,separators=(',',':'))
    prompt_provenance={'version':PROMPT_VERSION,'sha256':hashlib.sha256(canonical_prompt.encode()).hexdigest(),'canonicalization':'UTF-8 JSON sorted keys, no insignificant whitespace','previous_analysis_supplied':bool(data.get('previous_analysis')),'previous_analysis_sha256':hashlib.sha256(json.dumps(data.get('previous_analysis'),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'used_by_model':request.mode=='llm'}
    return {'analysis_id':str(uuid.uuid4()),'created_at':datetime.now(timezone.utc).isoformat(),'mode':request.mode,'disclaimer':DISCLAIMER,'obligations':parsed['obligations'],'questions':parsed['questions'],'observations':observations(data),'warnings':warnings,'provider':meta,'artifact_sha256':hashes,'prompt_provenance':prompt_provenance,'review_context':{'previous_analysis':data.get('previous_analysis')},'artifacts':{k:data[k] for k in ARTIFACTS},'execution':{'performed':False,'note':'Analysis does not execute code. Fixture runs are separate, immutable demonstrations.'}}
