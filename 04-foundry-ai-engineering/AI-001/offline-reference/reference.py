"""Portable, network-free replay of five saved development cases."""
import argparse,hashlib,json
from pathlib import Path

def load(root,case_id):
    index=json.loads((root/'inputs/index.json').read_text(encoding='utf-8'))
    if case_id not in index['cases']:raise ValueError('Unknown or unavailable case; only packaged development cases are supported')
    entry=index['cases'][case_id]
    p=(root/entry['file']).resolve()
    if not p.is_relative_to((root/'inputs').resolve()):raise ValueError('Input path outside package')
    if hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Input hash mismatch')
    data=json.loads(p.read_text(encoding='utf-8'))
    if data['case_id']!=case_id or data['split']!='development':raise ValueError('Case identity or split mismatch')
    if len(data['passages'])>5:raise ValueError('Saved retrieval limit exceeded')
    if any(e['runtime_eligible']is not False for e in data['passages']):raise ValueError('Package is restricted to false-eligibility lab snapshots')
    return data

def response(data):
    # Replay the frozen development decision; do not pretend to classify new questions.
    if data['route']=='evidence_only':
        return {'case_id':data['case_id'],'original_question':data['original_question'],'mode':'evidence_only','passages':data['passages'],'generated_procedural_claims':False}
    return {'case_id':data['case_id'],'original_question':data['original_question'],'mode':data['route'],'message':data['message'],'passages':[],'generated_procedural_claims':False}

def markdown(data):
    r=response(data)
    lines=['# '+r['case_id'],'',r['original_question'],'','Saved development input: '+data['variant']+'.','']
    if r['mode']!='evidence_only':return '\n'.join(lines+[r['message'],''])
    lines+=['**Evidence reference, not a generated procedural answer.** All five saved passages follow in their original order. No live-state assessment or permission to act is provided.','','## Passage index','', '| Passage | Source section | Document |','|---|---|---|']
    documents={}
    for p in r['passages']:
        key=(p['document_id'],p['source_url'],p['source_commit'])
        if key not in documents:documents[key]='D'+str(len(documents)+1)
        doc=documents[key]
        lines.append('| ['+p['id']+'](#'+p['id'].lower()+') | '+p['heading_h2'].replace('|','\\|')+' | ['+doc+'](#'+doc.lower()+') |')
    lines+=['','Use the section links to navigate. Each excerpt is complete; headings and ordering come from the saved retrieval.','']
    for p in r['passages']:
        doc=documents[(p['document_id'],p['source_url'],p['source_commit'])]
        lines+=['<a id="'+p['id'].lower()+'"></a>','## '+p['id']+' — '+p['heading_h2'],'','Source: ['+doc+'](#'+doc.lower()+')','']
        lines+=['> '+line for line in p['text'].splitlines()]+['']
    lines+=['## Source documents','']
    for (document_id,url,commit),label in documents.items():
        lines+=['<a id="'+label.lower()+'"></a>','### '+label+' — '+document_id,'','[Open pinned source]('+url+')','', 'Revision: '+commit,'']
    return '\n'.join(lines)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',required=True)
    parser.add_argument('--format',choices=['json','markdown'],default='markdown')
    args=parser.parse_args();data=load(Path(__file__).resolve().parent,args.case)
    print(json.dumps(response(data),ensure_ascii=True,indent=2)if args.format=='json'else markdown(data))
if __name__=='__main__':main()
