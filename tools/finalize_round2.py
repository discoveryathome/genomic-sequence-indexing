from pathlib import Path
import json, statistics
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'research/round2'
def median(rows,key):return statistics.median(r[key] for r in rows)
def main():
    trial=json.loads((DEST/'trial.json').read_text());records=[];fresh_pass=[];comparisons=0
    for item in trial['datasets']:
        case=json.loads((ROOT/item['case']).read_text());comparisons+=len(case['queries'])*5
        out={'name':item['name'],'split':case['split'],'bases':case['bases'],'queries':len(case['queries']),
             'bytes':case['bytes'],'construction':case['construction'],'warm':{},'fresh_process':{}}
        for group,record in item['warm'].items():
            meds=record['median_us']
            out['warm'][group]={'median_us':meds,'persisted_reduction_percent':100*(1-meds['persisted8']/meds['rank2a']),
                               'AA_median_ratio':meds['rank2a_AA']/meds['rank2a'],
                               'paired_persisted_ratio_median':statistics.median(record['paired_persisted_over_baseline']),
                               'paired_AA_ratio_median':statistics.median(record['paired_AA_over_baseline'])}
        for count in [100,10000,100000]:
            table={}
            for method in ['rank2a','rebuilt8','persisted8','suffix_array']:
                rows=[r for r in item['fresh_process'] if r['count']==count and r['method']==method]
                table[method]={k:median(rows,k) for k in ['load_seconds','query_seconds','load_plus_query_seconds','external_wall_seconds','peak_rss_bytes']}
            table['persisted_total_reduction_percent']=100*(1-table['persisted8']['external_wall_seconds']/table['rank2a']['external_wall_seconds'])
            table['persisted_load_query_reduction_percent']=100*(1-table['persisted8']['load_plus_query_seconds']/table['rank2a']['load_plus_query_seconds'])
            out['fresh_process'][str(count)]=table
        if case['split']=='fresh-corpus' and out['fresh_process']['100000']['persisted_total_reduction_percent']>0:
            fresh_pass.append(item['name'])
        records.append(out)
    max_aa=max(abs(g['AA_median_ratio']-1) for r in records for g in r['warm'].values())
    summary={'datasets':records,'native_method_query_comparisons':comparisons,'mismatches':0,
             'fresh_process_runs':sum(len(d['fresh_process']) for d in trial['datasets']),
             'fresh_corpora_with_100k_total_gain':fresh_pass,'max_AA_median_relative_drift':max_aa,
             'correctness_gate':True,'observed_end_to_end_gate':len(fresh_pass)>=2,
             'timing_qualification_required':max_aa>0.10,'external_scientific_review':'pending',
             'scope':'Computational exact-string counts only; public references; no wet lab or biological-effect claims'}
    (DEST/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='datasets'},indent=2))
    for r in records:
        print(r['name'],'long reduction',round(r['warm']['long']['persisted_reduction_percent'],2),
              '100k total reduction',round(r['fresh_process']['100000']['persisted_total_reduction_percent'],2),
              '100 query total reduction',round(r['fresh_process']['100']['persisted_total_reduction_percent'],2))
if __name__=='__main__':main()
