"""Build an explicit, audited source candidate. No uploads or network calls.
Never package the full development tree: its local evidence includes private paths.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,re,shutil,zipfile
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    base=ROOT/'release'/stamp;dest=base/'test-evidence';dest.mkdir(parents=True,exist_ok=False)
    selected=list(ROOT.glob('*.py'))+list((ROOT/'static').glob('*'))+list((ROOT/'tests').glob('test_*.py'))
    selected += [ROOT/p for p in ['README.md','RELEASE_CHECKLIST.md','THIRD_PARTY_NOTICES.md','.gitignore','requirements.txt','requirements-local.txt','docs/ARCHITECTURE.md','docs/PROMPT_PATTERNS.md','docs/SETUP.md','docs/DEMO.md','docs/SUBMISSION_VALIDATION.md','docs/IMPROVEMENT_PLAN.md','docs/REQUEST_UX_VALIDATION.md','docs/JSON_OUTPUT_VALIDATION.md','docs/PUBLISH_PLAN.md','scripts/durable_request.py','tests/scripts/duplicate-json-browser.py','tests/__init__.py','tests/acceptance_cases.json','scripts/package.py','scripts/evaluate.py','scripts/qwen35_eval.py','scripts/popos_eval.py','tests/scripts/submission-smoke.py','tests/scripts/dom-smoke.js','tests/scripts/clarification-regression.js','tests/scripts/request-lifecycle.js','tests/scripts/request-ux-browser.py','tests/scripts/request-ux-actual.py']]
    selected += [ROOT/'tests/popos_frozen_v1'/n for n in ['inputs.json','labels.json','manifest.json']]
    for pattern in ['llm_*.json','actual_model_acceptance*.json','critic_experiment.json','final_guard_replay.json','reasoning_run_manifest.json']:
        selected += list((ROOT/'tests/results').glob(pattern))
    for folder in [ROOT/'tests/results/popos/frozen_v1',ROOT/'tests/results/popos/qwen35_4b/frozen_v1']:
        selected += list(folder.glob('*.json'))
    q=ROOT/'tests/results/popos/qwen35_4b'
    selected += [q/'actual_smoke.json',q/'profile_comparison.json',q/'outcome_native_recovery.json']
    selected += [q/'browser_v1'/n for n in ['summary.json','actual_gpu_review.json','actual_gpu_refinement.json','actual_gpu_analyze_with_clarification.json','actual_review_export.json','desktop.png','mobile.png']]
    check=ROOT/'tests/results/submission_preparation_v1'
    selected += [check/n for n in ['unittest.txt','clarification.txt','dom.txt']]
    selected += [check/'browser'/n for n in ['summary.json','desktop.png','mobile.png']]
    ux=ROOT/'tests/results/request_ux_v1'
    selected += [ux/n for n in ['source_before.json','source_after.json','backend_red.txt','backend_green.txt','backend_disconnect.txt','frontend_red.txt','frontend_green.txt','unittest_final.txt','frontend_final.txt','clarification_final.txt','dom_final.txt','run_summary.json']]
    for folder,names in [('browser_mock',['summary.json','desktop_waiting.png','mobile_interrupted.png','mobile_reloaded_active.png']),('browser_actual',['summary.json','actual_result.json','review_export.json','active_status.json','desktop_waiting.png','mobile_waiting.png','desktop_result.png','mobile_result.png']),('browser_demo',['summary.json'])]:
        selected += [ux/folder/n for n in names]
    duplicate=ROOT/'tests/results/duplicate_json_v1'
    selected += [duplicate/n for n in ['red.txt','green.txt','full_tests_final.txt','clarification.txt','dom.txt','lifecycle.txt','experimental_regressions.txt','durability_red.txt','durability_green.txt','source_before.json']]
    selected += [duplicate/'browser'/n for n in ['summary.json','durable_worker_summary.json','rejected_export.json','rejected_export.md','desktop_duplicate.png','mobile_duplicate.png']]
    selected += [ROOT/n for n in ['Dockerfile','.dockerignore','render.yaml','docs/PUBLIC_DEPLOYMENT.md','docs/QWEN27_VALIDATION.md','docs/DEMO_NARRATION.md','docs/DEMO_STORYBOARD.md','tests/scripts/public-mode-browser.py','tests/scripts/qwen27-browser.py','scripts/qwen27_frozen_eval.py']]
    public=ROOT/'tests/results/public_mode_v1'
    selected += [public/n for n in ['red.txt','green_final.txt','secret_echo_red.txt','admission_final.txt','full_tests_final.txt','clarification_final.txt','dom_final.txt','lifecycle_final.txt']]
    selected += [public/'browser'/n for n in ['summary.json','own_review_export.json']]
    selected += [public/'container'/n for n in ['summary.json','container.log']]
    q27=ROOT/'tests/results/qwen27_v1'
    selected += [q27/'model_public.json',q27/'development_summary.json',q27/'browser_harness_note.json']
    selected += [q27/'browser_recovery'/n for n in ['summary.json','review.json','refinement.json','review_export.json','review_export.md','refinement_export.json','execution_public.json','events.json']]
    selected += [ROOT/'tests/qwen27_frozen_v2'/n for n in ['inputs.json','labels.json','manifest.json']]
    fresh=ROOT/'tests/results/qwen27_v2'
    selected += [fresh/'score_final.json',fresh/'manual_audit.json']+list((fresh/'public_responses').glob('*.json'))
    # Browser stills are internal QA evidence, not requested Library deliverables.
    selected=[p for p in selected if p.suffix.lower() not in {'.png','.jpg','.jpeg','.webp'}]
    for source in sorted(set(selected)):
        if not source.is_file() or source.is_symlink():raise RuntimeError('Missing/unsafe selected file: '+str(source.relative_to(ROOT)))
        rel=source.relative_to(ROOT);target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
        if rel.as_posix()=='docs/SETUP.md':
            # Local launcher section is operational context, not portable release code.
            text=source.read_text();a=text.index('## Existing PC Qwen profile');b=text.index('## Portable equivalent',a)
            target.write_text(text[:a]+text[b:])
        elif source.suffix=='.txt' and (source.parent==check or source.parent==ux or source.parent==duplicate or source.parent==public):
            target.write_text(re.sub(r'/(?:home/[A-Za-z0-9_.-]+|mnt/[A-Za-z0-9_.-]+|tmp)/[^\s:]+','<LOCAL_PATH>',source.read_text()))
        else:shutil.copy2(source,target)
    model=json.loads((q/'model_provenance.json').read_text());model.pop('local_model',None)
    model['scope']='Public metadata copy: local model directory removed; original privately retained.'
    (dest/'tests/results/popos/qwen35_4b/model_public.json').write_text(json.dumps(model,indent=2)+chr(10))
    included={p.relative_to(dest).as_posix():digest(p) for p in dest.rglob('*') if p.is_file()}
    notices={'scope':'Preparation source candidate, not final freeze or published artifact','files':included,'app_sources_unchanged_from_local':{p.relative_to(ROOT).as_posix():digest(p) for p in list(ROOT.glob('*.py'))+list((ROOT/'static').glob('*'))},'omissions':['weights, runtimes, virtualenv, caches, credentials, assignment/research PDFs, original archive','SSH/account/hardware metadata and machine-specific launch scripts','full private startup/protocol manifests and execution logs containing local paths','internal browser screenshots retained locally; requested video delivered separately'],'transformations':['docs/SETUP.md local-launcher section omitted in public copy','submission test logs replace private absolute paths with <LOCAL_PATH>','model_public.json omits local directory; raw model judgments remain unaltered'],'sealed_experiment_note':'Raw frozen outputs and source snapshots are unchanged. Original seals also reference full private runtime/launch protocols omitted here. Do not treat redacted/omitted metadata as matching original protocol hashes.'}
    (dest/'SOURCE_MANIFEST.json').write_text(json.dumps(notices,indent=2)+chr(10))
    problems=[]
    sensitive=re.compile(r'/(?:home/[A-Za-z0-9_.-]+|mnt/[A-Za-z0-9_.-]+)/|-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----|https?://[^\s\"<>]+[?&](?:sig|X-Amz-Signature)=',re.I)
    for p in dest.rglob('*'):
        if not p.is_file():continue
        if p.stat().st_size>2*1024*1024:problems.append(str(p.relative_to(dest))+': too large')
        try:
            if sensitive.search(p.read_text()):problems.append(str(p.relative_to(dest))+': private metadata pattern')
        except UnicodeError:pass
        if p.suffix.lower() in {'.pdf','.gguf','.safetensors','.pem','.key','.pyc'}:problems.append(str(p.relative_to(dest))+': excluded asset type')
    if problems:raise RuntimeError('Candidate audit failed (values not printed): '+str(problems))
    archive=base/'test-evidence-source.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(dest.rglob('*')):
            if p.is_file():z.write(p,Path('test-evidence')/p.relative_to(dest))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
    receipt={'candidate':str(dest),'archive':str(archive),'bytes':archive.stat().st_size,'sha256':digest(archive),'entries':len(included)+1,'status':'LOCAL PREPARATION CANDIDATE; not published; gitleaks and extracted tests still required'}
    (base/'BUILD_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+chr(10));print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
