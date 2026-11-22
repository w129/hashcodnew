#!/usr/bin/env python3
"""Openicons: PNG export is transparent regardless of the preview background.
Preserves original SVG export and fixes Win32 clipboard alpha via CF_DIBV5.
"""
from pathlib import Path
root=Path(__file__).resolve().parent/'src'

def patch(file, old, new):
    path=root/file
    src=path.read_text(encoding='utf-8')
    if src.count(old)!=1:
        raise SystemExit(f'{file}: expected one match, got {src.count(old)}: {old[:90]}')
    path.write_text(src.replace(old,new,1),encoding='utf-8')

p='web/app.js'
patch(p,'function styleExportSVG(svg){',"function styleExportSVG(svg,options={}){\n  const exportBackground=options.transparentBackground===true?'transparent':state.background;")
patch(p,"if(state.rotation===0&&state.background==='transparent')return svg;","if(state.rotation===0&&exportBackground==='transparent')return svg;")
patch(p,"if(state.background!=='transparent'){\n    const rect=doc.createElementNS","if(exportBackground!=='transparent'){\n    const rect=doc.createElementNS")
patch(p,"rect.setAttribute('fill',state.background);","rect.setAttribute('fill',exportBackground);")
patch(p,"async function readSVG(key=state.selected){","async function readSVG(key=state.selected,options={}){")
patch(p,"return styleExportSVG(svg)","return styleExportSVG(svg,options)")
patch(p,"  const svg=await readSVG(key);\n  const source=new Blob([svg]","  // PNG must exclude preview background, preserving alpha on copy and download.\n  const svg=await readSVG(key,{transparentBackground:true});\n  const source=new Blob([svg]")
patch(p,"notify('PNG descargado')","notify('PNG transparente descargado')")
patch(p,"notify('PNG copiado · Pega con Ctrl+V')","notify('PNG transparente copiado · Ctrl+V')")
patch(p,"notify('PNG copiado al portapapeles de Windows · Ctrl+V')","notify('PNG transparente copiado a Windows · Ctrl+V')")

p='web/index.html'
patch(p,'id="downloadPng"><svg><use href="#i-download"/></svg> Descargar PNG','id="downloadPng"><svg><use href="#i-download"/></svg> Descargar PNG transparente')
patch(p,'id="copyPng"><svg><use href="#i-copy"/></svg> Copiar PNG al portapapeles','id="copyPng"><svg><use href="#i-copy"/></svg> Copiar PNG transparente')
patch(p,'Los iconos incluidos funcionan sin internet. Antes de redistribuirlos, consulta la licencia de su colección.','Copiar y descargar PNG siempre mantiene fondo transparente; el fondo de vista previa no se exporta. Consulta la licencia de la colección.')

p=root/'clipboard_windows.go'
s=p.read_text(encoding='utf-8')
start=s.index('func bitmapDIB(')
end=s.index('\nfunc writePNGClipboard(',start)
newfunc=r'''func bitmapDIBV5(src image.Image) ([]byte,error) {
 bounds:=src.Bounds()
 w,h:=bounds.Dx(),bounds.Dy()
 if w<=0||h<=0||w>4096||h>4096 {return nil,errors.New("dimensiones PNG inválidas")}
 const headerSize=124
 stride:=w*4
 data:=make([]byte,headerSize+stride*h)
 put32:=func(at int,v uint32){binary.LittleEndian.PutUint32(data[at:at+4],v)}
 put32(0,headerSize)
 put32(4,uint32(w))
 put32(8,uint32(h)) // bottom-up BGRA pixels
 binary.LittleEndian.PutUint16(data[12:14],1)
 binary.LittleEndian.PutUint16(data[14:16],32)
 put32(16,3) // BI_BITFIELDS
 put32(20,uint32(stride*h))
 put32(40,0x00ff0000) // red mask
 put32(44,0x0000ff00) // green mask
 put32(48,0x000000ff) // blue mask
 put32(52,0xff000000) // alpha mask
 put32(56,0x73524742) // LCS_sRGB
 for y:=0;y<h;y++{
   for x:=0;x<w;x++{
     c:=color.NRGBAModel.Convert(src.At(bounds.Min.X+x,bounds.Min.Y+y)).(color.NRGBA)
     i:=headerSize+(h-1-y)*stride+x*4
     data[i],data[i+1],data[i+2],data[i+3]=c.B,c.G,c.R,c.A
   }
 }
 return data,nil
}
'''
s=s[:start]+newfunc+s[end:]
if s.count('"bytes"\n')!=1:raise SystemExit('unexpected Win32 imports')
s=s.replace('"bytes"\n','"bytes"\n\t"encoding/binary"\n',1)
if s.count('dib, err := bitmapDIB(img)')!=1:raise SystemExit('unexpected DIB reference')
s=s.replace('dib, err := bitmapDIB(img)','dib, err := bitmapDIBV5(img)',1)
if '{{cfPNG, data}, {8, dib}}' not in s:raise SystemExit('unexpected clipboard format list')
s=s.replace('{{cfPNG, data}, {8, dib}}','{{cfPNG, data}, {17, dib}}',1)
s=s.replace('// Windows registered PNG format preserves real transparency; CF_DIB is a fallback for legacy apps.',
            '// PNG and CF_DIBV5 retain alpha; legacy CF_DIB can silently discard transparency.')
p.write_text(s,encoding='utf-8')
print('Openicons PNG transparent export + Windows CF_DIBV5 patch applied')
