"""Restore exact scientific runtime assets on CI from official distributions."""
from pathlib import Path
import hashlib
import json
import urllib.request

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'scripts/browser-runtime-manifest.json').read_text())
for relative,entry in manifest.items():
    target=root/'frontend/public'/relative
    if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest()==entry['sha256']:
        continue
    url=entry.get('url')
    if not url:
        with urllib.request.urlopen(f"https://pypi.org/pypi/{entry['pypi_package']}/{entry['version']}/json",timeout=60) as response:
            metadata=json.load(response)
        release=next(f for f in metadata['urls'] if f['filename']==entry['filename'])
        assert release['digests']['sha256']==entry['sha256']
        url=release['url']
    with urllib.request.urlopen(url,timeout=120) as response:
        content=response.read()
    if hashlib.sha256(content).hexdigest()!=entry['sha256']:
        raise ValueError('Scientific runtime checksum mismatch: '+relative)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(content)
    print('Verified runtime:',relative)
