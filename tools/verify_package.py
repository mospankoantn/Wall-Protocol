from pathlib import Path
import zipfile,struct,json,hashlib
root=Path(__file__).resolve().parents[1]
package=root/'build/package'
expected=['Wall Protocol.exe','data.win','options.ini','PLAY.md','ART.md']
with zipfile.ZipFile(root/'build/WallProtocol.zip') as archive:
    assert sorted(archive.namelist())==sorted(expected),archive.namelist()
    assert archive.testzip() is None
    for name in expected:assert archive.read(name)==(package/name).read_bytes(),name
ico=(root/'options/windows/icons/icon.ico').read_bytes()
exe=(package/'Wall Protocol.exe').read_bytes()
count=struct.unpack_from('<H',ico,4)[0]
embedded=0
for i in range(count):
    size,offset=struct.unpack_from('<II',ico,6+i*16+8)
    if ico[offset:offset+size] in exe:embedded+=1
assert embedded==count, f'Custom icon payloads in EXE: {embedded}/{count}'
result=json.loads((root/'build/verification/runtime-results.json').read_text())
assert result['passed'] and result['checks']>=64
metadata=json.loads((root/'build/metadata-check.json').read_text())
assert metadata['passed']
report={'passed':True,'zip_entries':expected,'custom_icon_sizes_embedded':embedded,'runtime_checks':result['checks'],'metadata_checks':metadata['checks'],'sha256':{n:hashlib.sha256((package/n).read_bytes()).hexdigest() for n in expected}}
(root/'build/verification/package-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
