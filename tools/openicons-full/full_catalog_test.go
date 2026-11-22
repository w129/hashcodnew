package main
import (
    "encoding/json"
    "net/http/httptest"
    "net/http"
    "strings"
    "testing"
)
func TestFullCatalogOver300k(t *testing.T) {
    app := newApp(t.TempDir())
    w := httptest.NewRecorder()
    app.routes().ServeHTTP(w, httptest.NewRequest("GET", "/api/statistics", nil))
    if w.Code != 200 { t.Fatalf("stats HTTP %d", w.Code) }
    var s struct { DistinctIcons int `json:"distinctIcons"`; FullCatalogBundled bool `json:"fullCatalogBundled"` }
    if e:=json.Unmarshal(w.Body.Bytes(),&s);e!=nil{t.Fatal(e)}
    if s.DistinctIcons<300000||!s.FullCatalogBundled {t.Fatalf("not a full offline bundle: %+v",s)}
    for _, prefix:=range []string{"mdi","lucide","tabler","ph","iconoir","material-symbols"} {
        w=httptest.NewRecorder()
        app.routes().ServeHTTP(w,httptest.NewRequest("GET","/api/collection?prefix="+prefix,nil))
        if w.Code!=200 {t.Fatalf("collection %s: %d %s",prefix,w.Code,w.Body.String())}
        var col struct { Icons []string `json:"icons"`; Offline bool `json:"offline"` }
        if e:=json.Unmarshal(w.Body.Bytes(),&col);e!=nil{t.Fatal(e)}
        if len(col.Icons)<500||!col.Offline {t.Fatalf("not offline %s: %d",prefix,len(col.Icons))}
        set,e:=app.getPack(prefix);if e!=nil{t.Fatal(e)}
        for i:=0;i<3&&i<len(col.Icons);i++{
            name:=col.Icons[i]
            svg,e:=renderSVG(set,name,"#123456")
            if e!=nil||!strings.Contains(string(svg),"<svg") {t.Fatalf("unrenderable %s:%s: %v",prefix,name,e)}
        }
    }
}
func TestFullGalleryHasDiverseIcons(t *testing.T) {
    app:=newApp(t.TempDir())
    w:=httptest.NewRecorder()
    app.routes().ServeHTTP(w,httptest.NewRequest("GET","/api/variants?start=0",nil))
    if w.Code!=200 {t.Fatalf("variants HTTP %d",w.Code)}
    var data struct { Variants []struct { Key string `json:"key"` } `json:"variants"` }
    if e:=json.Unmarshal(w.Body.Bytes(),&data);e!=nil{t.Fatal(e)}
    keys:=map[string]bool{}
    for _,v:=range data.Variants {keys[v.Key]=true}
    if len(keys)!=72 {t.Fatalf("expected 72 different actual drawings, got %d",len(keys))}
}
