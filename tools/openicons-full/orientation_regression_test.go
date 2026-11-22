package main

import (
 "strings"
 "testing"
)

func TestOrientationVariantsRemainUpright(t *testing.T) {
 order := newIconOrder(map[string][]string{"test": {"arrow-up", "arrow-left", "arrow-right"}})
 if order.total!=3 {t.Fatalf("total: %d",order.total)}
 scales:=map[float64]bool{}
 for pos:=int64(0);pos<int64(order.total*variantsPerIcon);pos++ {
  v,ok:=order.variant(pos);if !ok {t.Fatalf("variant missing %d",pos)}
  if v["rotation"].(int)!=0 {t.Fatalf("variant %d has unwanted rotation: %v",pos,v["rotation"])}
  s,ok:=v["scale"].(float64);if !ok||s<=0||s>1 {t.Fatalf("invalid upright scale at %d: %v",pos,v["scale"])}
  scales[s]=true
 }
 if len(scales)!=4 {t.Fatalf("expected 4 upright sizes, got %d",len(scales))}
}

func TestOrientationSourceSVGIsNotArtificiallyFlipped(t *testing.T) {
 path:=`<path d="M2 2L8 2L2 8Z"/>`
 set:=&iconSet{Prefix:"test",Width:10,Height:10,Icons:map[string]iconDef{"original":{Body:path}}}
 b,err:=renderSVG(set,"original","#17191d");if err!=nil {t.Fatal(err)}
 svg:=string(b)
 if !strings.Contains(svg,path) {t.Fatalf("original icon path changed: %s",svg)}
 if strings.Contains(svg,"<g transform=") {t.Fatalf("original orientation modified: %s",svg)}
}

func TestOrientationRespectsIntentionalIconifyAliasMetadata(t *testing.T) {
 set:=&iconSet{Prefix:"test",Width:10,Height:10,
  Icons:map[string]iconDef{"original":{Body:`<path d="M2 2L8 2L2 8Z"/>`}},
  Aliases:map[string]iconDef{"official-flipped-alias":{Parent:"original",HFlip:true}},
 }
 b,err:=renderSVG(set,"official-flipped-alias","#17191d");if err!=nil {t.Fatal(err)}
 if !strings.Contains(string(b),"scale(-1 1)") {t.Fatalf("Iconify alias metadata lost: %s",b)}
}