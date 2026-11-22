#!/usr/bin/env python3
"""Openicons: render all designs upright by default and keep variation styles upright.
Preserves Iconify source metadata orientation and previous transparent PNG behavior.
"""
from pathlib import Path
root=Path(__file__).resolve().parent/'src'

def patch(file, old, new):
    p=root/file
    s=p.read_text(encoding='utf-8')
    count=s.count(old)
    if count!=1:
        raise SystemExit(f'{file}: expected exactly one occurrence, got {count}: {old[:100]!r}')
    p.write_text(s.replace(old,new,1),encoding='utf-8')

patch('variants.go',
      'var variantRotations = []int{0, 90, 180, 270}',
      '''// Four original-orientation scale choices replace rotations; no icon is turned upside down.
var variantScales = []float64{1, 0.92, 0.84, 0.76}''')
patch('variants.go',
      '''// Variation numbers are rotated by drawing, keeping each page visually
	// diverse while preserving all 400 combinations for EVERY source icon.''',
      '''// Interleave different drawings per page while keeping the source orientation
	// intact: 10 colors x 4 sizes x 10 backgrounds = 400 per design.''')
patch('variants.go',
      '''"rotation": variantRotations[(variant/10)%4], "background": variantBackgrounds[(variant/40)%10],''',
      '''"rotation": 0, "scale": variantScales[(variant/10)%4], "background": variantBackgrounds[(variant/40)%10],''')

patch('web/app.js',
      "selected:'',collections:{},offline:{hashcod:25},favorites:new Set(),color:'#17191d',theme:'dark',rotation:0,background:'transparent',",
      "selected:'',collections:{},offline:{hashcod:25},favorites:new Set(),color:'#17191d',theme:'dark',rotation:0,scale:1,background:'transparent',")
patch('web/app.js',
      'rotation:state.rotation,background:state.background',
      'rotation:0,background:state.background')
patch('web/app.js',
      "if([0,90,180,270].includes(x.rotation))state.rotation=x.rotation;",
      'state.rotation=0; /* do not restore stale turns from older releases */')
patch('web/app.js',
      "img.style.transform='rotate('+state.rotation+'deg)'",
      "img.style.transform='none'")
patch('web/app.js',
      "card.querySelector('img').style.transform='rotate('+state.rotation+'deg)'",
      "card.querySelector('img').style.transform='none'")
patch('web/app.js',
      '''function chooseIcon(key){if(!splitKey(key))return;state.selected=key;''',
      '''function chooseIcon(key,{keepTransform=false}={}){if(!splitKey(key))return;
  // Selecting a different icon always shows its original, upright artwork.
  if(!keepTransform){state.rotation=0;state.scale=1;$('rotationSelect').value='0';}
  state.selected=key;''')
patch('web/app.js',
      "$('previewImage').style.transform='rotate('+state.rotation+'deg)';",
      "$('previewImage').style.transform='rotate('+state.rotation+'deg) scale('+state.scale+')';")
patch('web/app.js',
      "  document.querySelectorAll('.icon-card:not(.variant-card) .icon-thumb img').forEach(el=>el.style.transform='rotate('+state.rotation+'deg)');",
      "  // Do not rotate the main icon grid; any manual rotation applies only to the inspector.")
patch('web/app.js',
      "if(state.rotation===0&&exportBackground==='transparent')return svg;",
      "if(state.rotation===0&&state.scale===1&&exportBackground==='transparent')return svg;")
patch('web/app.js',
      '''if(state.rotation){
    const group=doc.createElementNS('http://www.w3.org/2000/svg','g');
    group.setAttribute('transform',`rotate(${state.rotation} ${left+width/2} ${top+height/2})`);
    while(root.firstChild)group.appendChild(root.firstChild);
    root.appendChild(group);
  }''',
      '''if(state.rotation||state.scale!==1){
    const group=doc.createElementNS('http://www.w3.org/2000/svg','g');
    const cx=left+width/2,cy=top+height/2;
    group.setAttribute('transform',`translate(${cx} ${cy}) rotate(${state.rotation}) scale(${state.scale}) translate(${-cx} ${-cy})`);
    while(root.firstChild)group.appendChild(root.firstChild);
    root.appendChild(group);
  }''')
patch('web/app.js',
      '  const img=thumb.querySelector(\'img\');img.style.transform=`rotate(${v.rotation}deg)`;',
      '  const img=thumb.querySelector(\'img\');img.style.transform=`scale(${Number(v.scale)||1})`;')
patch('web/app.js',
      '${esc(v.color)} · ${v.rotation}°</div>`;',
      '${esc(v.color)} · ${Math.round((Number(v.scale)||1)*100)}% · orientación original</div>`;')
patch('web/app.js',
      '''const activate=()=>{state.color=v.color;state.rotation=v.rotation;state.background=v.background;''',
      '''const activate=()=>{state.color=v.color;state.rotation=0;state.scale=Number(v.scale)||1;state.background=v.background;''')
patch('web/app.js',
      "chooseIcon(v.key);notify('Variante aplicada y lista para exportar')",
      "chooseIcon(v.key,{keepTransform:true});notify('Variante aplicada en su orientación original')")
patch('web/app.js',
      "'400 variaciones exportables por cada diseño: muestra generada al instante'",
      "'400 variaciones de color, tamaño y fondo por diseño, sin giros automáticos'")
patch('web/index.html',
      '10 colores × 4 giros × 10 fondos = 400 variantes por icono, creadas al instante',
      '10 colores × 4 tamaños × 10 fondos = 400 variantes por icono, sin voltearlos')
print('Orientation fix applied: upright grid + variants, source metadata preserved, PNG alpha preserved')