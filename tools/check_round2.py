"""Check published count witnesses without rebuilding large native indexes."""
from pathlib import Path
import json, time
from verify_count import check
ROOT=Path(__file__).resolve().parents[1]
def main():
    start=time.perf_counter();queries=0
    for path in json.loads((ROOT/'research/round2/cases.json').read_text()):
        result=check(ROOT/path);queries+=result['queries']
    trial=json.loads((ROOT/'research/round2/trial.json').read_text())
    runs=0
    for dataset in trial['datasets']:
        for row in dataset['fresh_process']:
            assert row['mismatches']==0 and row['peak_rss_bytes']>0
            assert row['count'] in [100,10000,100000];runs+=1
        for group in dataset['warm'].values():
            assert all(len(v)==7 and all(t>0 for t in v) for v in group['samples_us'].values())
    confirmation=json.loads((ROOT/'research/round2/confirmation/results.json').read_text())
    assert confirmation['retuned'] is False and confirmation['new_holdout'] is False
    confirmation_runs=0
    for dataset in confirmation['datasets']:
        for row in dataset['fresh_process']:
            assert row['mismatches']==0 and row['count']==100000
            assert row['peak_rss_bytes']>0;confirmation_runs+=1
        for group in dataset['warm'].values():
            assert all(len(v)==7 and all(t>0 for t in v) for v in group['samples_us'].values())
    assert confirmation_runs==24
    print(json.dumps({'passed':True,'direct_witness_queries':queries,'fresh_process_records':runs,
                      'confirmation_process_records':confirmation_runs,
                      'elapsed_seconds':time.perf_counter()-start,'note':'Witness checks validate counts; timings remain observations'}))
if __name__=='__main__':main()
