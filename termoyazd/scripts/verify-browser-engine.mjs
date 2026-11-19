// Real WebAssembly/Python verification in Node. This is not browser UI testing.
import {fileURLToPath} from 'node:url';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
const root=new URL('../',import.meta.url);
const {loadPyodide}=await import(new URL('frontend/public/pyodide/pyodide.mjs',root));
const py=await loadPyodide({indexURL:fileURLToPath(new URL('frontend/public/pyodide/',root))});
await py.loadPackage(['numpy','scipy']);
py.FS.mkdirTree('/home/pyodide/app');
for(const name of ['__init__.py','engine.py','thermo.py','plotting.py'])py.FS.writeFile('/home/pyodide/app/'+name,await readFile(new URL('frontend/public/python/'+name,root),'utf8'));
const wheel=new Uint8Array(await readFile(new URL('frontend/public/python/iapws-1.5.5-py3-none-any.whl',root)));
py.unpackArchive(wheel.buffer,'zip',{extractDir:'/home/pyodide'});
const result=await py.runPythonAsync(`
import sys,json
sys.path.insert(0,'/home/pyodide')
from app.engine import solve,PAIRS
from app.thermo import StateError
from app.plotting import saturation_data
source=solve('P_x',{'P':500,'x':.35})['full_state']|{'x':.35}
checks=[]
for pair in PAIRS:
    values={k:source[k] for k in pair.split('_')}
    if pair=='T_P':values={'T':300,'P':500}
    answer=solve(pair,values)
    assert answer['convergence']['converged']
    assert len(answer['calculated_properties'])==4
    assert all(abs(r)<=answer['convergence']['tolerances'][k] for k,r in answer['convergence']['residuals'].items())
    checks.append({'pair':pair,'passed':True,'method':answer['solver_method']})
curve=saturation_data()
assert len(curve['points'])==161
assert curve['critical']['included'] is False
try:
    solve('P_x',{'P':500,'x':1.2})
    raise AssertionError('Invalid quality accepted')
except StateError as e:
    assert e.code=='invalid_quality'
json.dumps({'runtime':'Pyodide 0.27.7 / real IF97', 'checks':checks,'saturation_samples':len(curve['points']),'invalid_quality_rejected':True})
`);
await mkdir(new URL('deployment/',root),{recursive:true});
await writeFile(new URL('deployment/wasm-verification.json',root),JSON.stringify(JSON.parse(result),null,2)+'\n');
console.log('termoyazd: all 11 pairs, real saturation data and invalid quality passed in WebAssembly/Python');
