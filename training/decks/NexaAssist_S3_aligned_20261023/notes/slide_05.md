python -m training.showcase --session 3 Tag escape retained; bad quote → abstention. Same cases: −0.25; changed dataset: refused. Allow 25 minutes. Also exercise the output PII rail. Inspect prompt version 1.1.0, the one-repair limit and dataset/judge identity checks. Scores and drafts are visibly synthetic.

Code walkthrough: app/evaluation/run.py
def case_fingerprint(case: GoldenCase) -> str:
    canonical = json.dumps(case.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode()).hexdigest()


Align reviewed cases and the judge contract. Inspect case flips alongside aggregate deltas. Regenerate reports that lack identity evidence. The application model or prompt may change deliberately. Dataset, judge model/prompt and metric versions must align. CLI exits 2 for incomparable evidence, 1 for regressions or newly failing cases. Live golden evaluation is still required before release.