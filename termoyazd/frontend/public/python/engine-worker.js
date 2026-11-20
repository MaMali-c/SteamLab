let ready;
const assetRoot=new URL('../',import.meta.url);
async function initialize(){
  const {loadPyodide}=await import(new URL('pyodide/pyodide.mjs',assetRoot).href);
  const py=await loadPyodide({indexURL:new URL('pyodide/',assetRoot).href});
  await py.loadPackage(['numpy','scipy']);
  py.FS.mkdirTree('/home/pyodide/app');
  for(const name of ['__init__.py','engine.py','thermo.py','plotting.py']){
    const r=await fetch(new URL('python/'+name,assetRoot));if(!r.ok)throw Error('Python source unavailable');
    py.FS.writeFile('/home/pyodide/app/'+name,await r.text());
  }
  const wheel=await fetch(new URL('python/iapws-1.5.5-py3-none-any.whl',assetRoot));
  if(!wheel.ok)throw Error('IF97 library unavailable');
  py.unpackArchive(await wheel.arrayBuffer(),'zip',{extractDir:'/home/pyodide'});
  await py.runPythonAsync(`import sys,json\nsys.path.insert(0,'/home/pyodide')\nfrom app.engine import solve\nfrom app.thermo import StateError\nfrom app.plotting import saturation_data\ndef dispatch(path,payload):\n    try:\n        if path == '/api/health': return json.dumps({'status':200,'body':{'app':'termoyazd','status':'ok'}})\n        if path == '/api/diagrams/saturation': body=saturation_data()\n        elif path == '/api/calculate': body=solve(payload['input_pair'],payload['values'])\n        else: return json.dumps({'status':404,'body':{'error':{'message':'Unknown route'}}})\n        return json.dumps({'status':200,'body':body})\n    except StateError as e:\n        return json.dumps({'status':422,'body':{'error':{'code':e.code,'message':str(e),'candidates':getattr(e,'candidates',[])}}})\n    except Exception as e:\n        return json.dumps({'status':422,'body':{'error':{'code':'numerical_failure','message':str(e)}}})`);
  return py;
}
let queue=Promise.resolve();
let queued=0;
self.onmessage=({data})=>{
 if(queued>=8 || new TextEncoder().encode(JSON.stringify(data)).length>16384){self.postMessage({id:data.id,status:429,body:{error:{code:'worker_busy',message:'Scientific request or queue limit exceeded.'}}});return;}
 queued++;
 queue=queue.then(async()=>{
  try{
    if(!ready)ready=initialize().catch(error=>{ready=null;throw error;});
    const py=await ready;
    py.globals.set('_request',JSON.stringify(data));
    const result=await py.runPythonAsync("_parsed=json.loads(_request)\ndispatch(_parsed['path'],_parsed.get('payload',{}))");
    self.postMessage({id:data.id,...JSON.parse(result)});
  }catch(error){self.postMessage({id:data.id,status:503,body:{error:{message:'Scientific engine could not initialize: '+error.message}}});}
}).finally(()=>{queued--;});};
