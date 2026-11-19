let worker:Worker|null=null;
let counter=0;
const pending=new Map<number,{resolve:(value:Response)=>void;reject:(error:Error)=>void;cleanup:()=>void}>();
export function browserFetch(path:string,init?:RequestInit):Promise<Response>{
 if(pending.size>=8) return Promise.reject(Error('Scientific engine queue is full. Please wait. صف محاسبه پر است.'));
 if(typeof init?.body === 'string' && new TextEncoder().encode(init.body).length>16384) return Promise.reject(Error('Scientific request is too large. حجم درخواست بیش از حد مجاز است.'));
 if(!worker){
  worker=new Worker(import.meta.env.BASE_URL+'python/engine-worker.js',{type:'module'});
  worker.onmessage=({data})=>{const task=pending.get(data.id);if(task){task.cleanup();pending.delete(data.id);task.resolve(new Response(JSON.stringify(data.body),{status:data.status,headers:{'Content-Type':'application/json'}}));}};
  worker.onerror=()=>{for(const task of pending.values()){task.cleanup();task.reject(Error('Scientific worker failed. Reload to retry.'));}pending.clear();worker?.terminate();worker=null;};
 }
 return new Promise((resolve,reject)=>{
  const id=++counter;
  const abort=()=>{pending.get(id)?.cleanup();pending.delete(id);reject(new DOMException('Aborted','AbortError'));};
  if(init?.signal?.aborted){abort();return;}
  init?.signal?.addEventListener('abort',abort,{once:true});
  pending.set(id,{resolve,reject,cleanup:()=>init?.signal?.removeEventListener('abort',abort)});
  worker!.postMessage({id,path,payload:init?.body?JSON.parse(String(init.body)):{}});
 });
}
