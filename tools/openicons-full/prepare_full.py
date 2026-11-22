#!/usr/bin/env python3
"""Prepare the verified full-catalog offline build; do not inflate counts."""
from pathlib import Path
root=Path(__file__).resolve().parent/"src"
p=root/"main.go"
src=p.read_text(encoding="utf-8")
assert "const maxPack = 60 << 20" in src
p.write_text(src.replace("const maxPack = 60 << 20","const maxPack = 180 << 20"),encoding="utf-8")
p=root/"tools"/"pack_iconify.py"
src=p.read_text(encoding="utf-8")
assert "len(packed) > 60 << 20" in src
src=src.replace("len(packed) > 60 << 20","len(packed) > 180 << 20")
src=src.replace("uncompressed collection exceeds 60 MiB","uncompressed collection exceeds 180 MiB")
p.write_text(src,encoding="utf-8")
p=root/"web"/"index.html"
html=p.read_text(encoding="utf-8")
html=html.replace('id="allCount">7.5k','id="allCount">…')
html=html.replace('id="statIcons">7,455','id="statIcons">…')
html=html.replace('id="variantCount">2.98M','id="variantCount">…')
html=html.replace('id="statVariants">2.98M','id="statVariants">…')
html=html.replace('class="brand-version">4.0','class="brand-version">Full')
html=html.replace('Edición 5.0','Edición completa')
html=html.replace('Diseños incluidos accesibles sin conexión. También puedes instalar las colecciones oficiales restantes desde esta misma aplicación.','Biblioteca de Iconify comprimida e integrada dentro de esta aplicación. Busca y exporta tus iconos sin conexión.')
html=html.replace('Instala automáticamente las colecciones oficiales aquí mismo, sin visitar páginas externas. Necesita internet solo durante la instalación; después podrás buscar y exportar sin conexión. El contador solo muestra colecciones realmente instaladas.','El catálogo completo se incluye durante la compilación: no hay que descargar colecciones después de instalar Openicons.')
html=html.replace('No se ha instalado aún el catálogo adicional de Iconify.','Catálogo oficial incorporado al ejecutable.')
html=html.replace('Los 7,430 iconos Material Design Icons y los 25 iconos Hashcod se incluyen sin conexión. Los demás iconos solo estarán disponibles sin conexión después de instalarlos; el programa no afirma incluirlos antes.','Las colecciones del catálogo completo se incorporan durante la compilación y quedan disponibles sin conexión desde el primer inicio.')
p.write_text(html,encoding="utf-8")
p=root/"web"/"app.js"
js=p.read_text(encoding="utf-8")
key="const amount=nice(stats.distinctIcons);"
assert key in js
js=js.replace(key,"if(stats.fullCatalogBundled){const panel=document.querySelector('.install-panel');if(panel)panel.classList.add('hidden');}\n   "+key)
p.write_text(js,encoding="utf-8")
print("Full catalog source and original UI prepared.")
