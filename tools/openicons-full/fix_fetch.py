#!/usr/bin/env python3
"""Patch stable offline Openicons desktop behavior before the Windows build."""
from pathlib import Path
root=Path(__file__).resolve().parent/"src"
p=root/"main.go"
s=p.read_text(encoding="utf-8")
def once(text,old,new,label):
 if text.count(old)!=1: raise RuntimeError(label+" source mismatch")
 return text.replace(old,new,1)
s=once(s,"return time.Since(a.lastActive) > 115*time.Second",
 "// Local browser app must survive background tab timer throttling.\n\treturn time.Since(a.lastActive) > 12*time.Hour","idle timeout")
s=once(s,"\tpackCache   map[string]*iconSet\n\tactiveMu",
 "\tpackCache   map[string]*iconSet\n\tpackOrder   []string // capped decompressed cache\n\tactiveMu","cache fields")
s=once(s,"\t} else {\n\t\ta.packCache[prefix] = p\n\t}\n\ta.mu.Unlock()\n\treturn p, nil\n}",
 "\t} else {\n\t\ta.packCache[prefix] = p\n\t\ta.packOrder = append(a.packOrder,prefix)\n\t\t// Keep only four decompressed Iconify packs to avoid out-of-memory crashes.\n\t\tfor len(a.packOrder)>4 {\n\t\t\told := a.packOrder[0]\n\t\t\ta.packOrder = a.packOrder[1:]\n\t\t\tdelete(a.packCache,old)\n\t\t}\n\t}\n\ta.mu.Unlock()\n\treturn p, nil\n}","cache policy")
p.write_text(s,encoding="utf-8")
p=root/"web"/"app.js"
s=p.read_text(encoding="utf-8")
old=" const response=await fetch(path,{cache:'no-store',...options});"
new=""" const attempts=(!options.method||options.method.toUpperCase()==='GET')?3:1;
 let response;
 for(let i=0;i<attempts;i++){
  try{response=await fetch(path,{cache:'no-store',...options});break}
  catch{
   if(i+1<attempts){await new Promise(done=>setTimeout(done,350*(i+1)));continue}
   throw Error('Servidor local de Openicons desconectado. Reabre el ejecutable y recarga la ventana.');
  }
 }"""
s=once(s,old,new,"fetch retry")
s=once(s,"async function loadMore(){if(state.page*state.pageSize<state.all.length)",
 "async function loadMore(){if(state.loading)return;\n if(state.page*state.pageSize<state.all.length)","paging concurrency")
p.write_text(s,encoding="utf-8")
(root/"fetch_reliability_test.go").write_text("""package main
import (
 "encoding/json"
 "fmt"
 "net/http/httptest"
 "os"
 "path/filepath"
 "testing"
 "time"
)
func TestFullLocalServerSurvivesBrowserIdle(t *testing.T) {
 a:=newApp(t.TempDir())
 a.activeMu.Lock();a.lastActive=time.Now().Add(-4*time.Minute);a.activeMu.Unlock()
 if a.expired(){t.Fatal("server closed during ordinary browsing")}
 a.activeMu.Lock();a.lastActive=time.Now().Add(-13*time.Hour);a.activeMu.Unlock()
 if !a.expired(){t.Fatal("idle time limit not applied")}
}
func TestFullCachedCollectionsHaveBoundedMemory(t *testing.T) {
 a:=newApp(t.TempDir())
 if e:=os.MkdirAll(a.folder("packs"),0700);e!=nil{t.Fatal(e)}
 for i:=0;i<9;i++{
  prefix:=fmt.Sprintf("testpack%d",i)
  doc:=map[string]any{"prefix":prefix,"width":24,"height":24,"icons":map[string]any{"icon":map[string]string{"body":"<circle/>"}}}
  data,_:=json.Marshal(doc)
  if e:=os.WriteFile(filepath.Join(a.folder("packs"),prefix+".json"),data,0600);e!=nil{t.Fatal(e)}
  if _,e:=a.getPack(prefix);e!=nil{t.Fatal(e)}
  if len(a.packCache)>4{t.Fatal("unbounded cache")}
 }
 if _,e:=a.getPack("testpack0");e!=nil{t.Fatal("evicted collection cannot be reloaded:",e)}
}
func TestFullLoadMorePages(t *testing.T) {
 h:=newApp(t.TempDir()).routes()
 seen:=map[string]bool{}
 for n:=0;n<4;n++{
  w:=httptest.NewRecorder()
  h.ServeHTTP(w,httptest.NewRequest("GET",fmt.Sprintf("/api/browse?start=%d",n*120),nil))
  if w.Code!=200{t.Fatalf("page %d HTTP %d",n,w.Code)}
  var data map[string]any
  if e:=json.Unmarshal(w.Body.Bytes(),&data);e!=nil{t.Fatal(e)}
  icons:=data["icons"].([]any)
  if len(icons)!=120 || int(data["total"].(float64))<300000{t.Fatalf("bad page %d count",n)}
  for _,v:=range icons{key:=v.(string);if seen[key]{t.Fatal("duplicate page entry",key)};seen[key]=true}
 }
}
""",encoding="utf-8")
print("Fixed idle timeout, bounded cache, GET retry and page guard.")
