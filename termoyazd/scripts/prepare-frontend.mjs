// Restore pinned scientific assets on a fresh clone; no Python needed on the frontend host.
import {copyFile,mkdir,readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(new URL('../frontend/package.json',import.meta.url));
const {fetch,EnvHttpProxyAgent}=require('undici');
const dispatcher=new EnvHttpProxyAgent();
const root=new URL('../',import.meta.url);
const manifest=JSON.parse(await readFile(new URL('scripts/browser-runtime-manifest.json',root),'utf8'));
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
for(const [relative,entry] of Object.entries(manifest)){
  const target=new URL('frontend/public/'+relative,root);
  const existing=await readFile(target).catch(()=>null);
  if(existing && digest(existing)===entry.sha256)continue;
  let url=entry.url;
  if(!url){
    const response=await fetch(`https://pypi.org/pypi/${entry.pypi_package}/${entry.version}/json`,{dispatcher,signal:AbortSignal.timeout(120000)});
    if(!response.ok)throw Error('Cannot load iapws distribution metadata');
    const metadata=await response.json();
    const release=metadata.urls.find(file=>file.filename===entry.filename);
    if(!release || release.digests.sha256!==entry.sha256)throw Error('iapws distribution checksum changed');
    url=release.url;
  }
  const response=await fetch(url,{dispatcher,signal:AbortSignal.timeout(120000)});
  if(!response.ok)throw Error(`Cannot download scientific runtime: ${relative}`);
  const bytes=new Uint8Array(await response.arrayBuffer());
  if(digest(bytes)!==entry.sha256)throw Error(`Scientific runtime checksum mismatch: ${relative}`);
  await mkdir(new URL('./',target),{recursive:true});
  await writeFile(target,bytes);
  console.log('Verified scientific runtime:',relative);
}
await mkdir(new URL('frontend/public/python/',root),{recursive:true});
for(const name of ['__init__.py','engine.py','thermo.py','plotting.py']) {
  await copyFile(new URL('backend/app/'+name,root),new URL('frontend/public/python/'+name,root));
}
console.log('termoyazd: browser Python sources synchronized');

await dispatcher.close();
