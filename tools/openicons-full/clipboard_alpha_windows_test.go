//go:build windows

package main

import (
 "encoding/binary"
 "image"
 "image/color"
 "testing"
)

// Verify CF_DIBV5 explicitly declares 8-bit alpha and retains transparent pixels.
func TestClipboardPNGAlphaIsPreserved(t *testing.T) {
 src:=image.NewNRGBA(image.Rect(0,0,2,2))
 src.SetNRGBA(0,0,color.NRGBA{R:255,G:0,B:255,A:0})
 src.SetNRGBA(1,1,color.NRGBA{R:77,G:88,B:99,A:255})
 data,err:=bitmapDIBV5(src)
 if err!=nil {t.Fatal(err)}
 u32:=func(at int)uint32{return binary.LittleEndian.Uint32(data[at:at+4])}
 if u32(0)!=124 {t.Fatalf("invalid BITMAPV5HEADER size: %d",u32(0))}
 if u32(16)!=3 {t.Fatalf("missing BI_BITFIELDS: %d",u32(16))}
 if u32(52)!=0xff000000 {t.Fatalf("missing alpha mask: %08x",u32(52))}
 // Image pixels are bottom-up, BGRA: top-left is the second row.
 if data[132+3]!=0 {t.Fatalf("transparent pixel became opaque: %d",data[135])}
 // Last pixel is bottom-right of the first row.
 if got:=data[128:132];got[0]!=99||got[1]!=88||got[2]!=77||got[3]!=255 {
  t.Fatalf("opaque pixel changed: %v",got)
 }
}
