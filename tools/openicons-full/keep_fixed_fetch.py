#!/usr/bin/env python3
"""Keep the earlier FULL-Fixed server and pagination improvements."""
from pathlib import Path
root=Path(__file__).resolve().parent/'src'
p=root/'main.go'
s=p.read_text(encoding='utf-8')
def sub(old,new,label):
 global s
 if s.count(old)!=1:raise SystemExit('Unexpected original '+label)
 s=s.replace(old,new,1)
sub('\tpackCache   map[string]*iconSet\n\tactiveMu    sync.Mutex',
    '\tpackCache   map[string]*iconSet\n\tpackOrder   []string // bounded cache order\n\tactiveMu    sync.Mutex','fields')
sub('return time.Since(a.lastActive) > 115*time.Second',
    '// Background tabs can throttle keepalives; extend idle expiry.\n\treturn time.Since(a.lastActive) > 12*time.Hour','timeout')
sub('\t} else {\n\t\ta.packCache[prefix] = p\n\t}\n\ta.mu.Unlock()\n\treturn p, nil\n}',
    '\t} else {\n\t\ta.packCache[prefix] = p\n\t\ta.packOrder = append(a.packOrder, prefix)\n\t\tconst maxCachedPacks = 4\n\t\tfor len(a.packOrder) > maxCachedPacks {\n\t\t\toldest := a.packOrder[0]\n\t\t\ta.packOrder = a.packOrder[1:]\n\t\t\tdelete(a.packCache, oldest)\n\t\t}\n\t}\n\ta.mu.Unlock()\n\treturn p, nil\n}','cache')
p.write_text(s,encoding='utf-8')
p=root/'web/app.js'
s=p.read_text(encoding='utf-8')
start=s.index('async function getJSON(path,options={})')
end=s.index('\nfunction setLoading',start)
s=s[:start]+'''async function getJSON(path,options={}){
 const attempts=(!options.method||options.method.toUpperCase()==='GET')?3:1;
 for(let i=0;i<attempts;i++){
  let res;
  try{res=await fetch(path,{cache:'no-store',...options})}
  catch{
   if(i+1<attempts){await new Promise(done=>setTimeout(done,350*(i+1)));continue}
   throw new Error('No se pudo conectar al servidor local. Reabre Openicons y actualiza la ventana.');
  }
  let obj;try{obj=await res.json()}catch{throw new Error('Respuesta del servidor local inválida')}
  if(!res.ok)throw new Error(obj.error||('Servidor local HTTP '+res.status));
  return obj;
 }
}'''+s[end:]
old='async function loadMore(){if(state.page*state.pageSize<state.all.length)'
new='async function loadMore(){\n if(state.loading)return; // Prevent double pagination.\n if(state.page*state.pageSize<state.all.length)'
if s.count(old)!=1:raise SystemExit('Unexpected loadMore helper')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('Previous FULL-Fixed reliability features preserved')
