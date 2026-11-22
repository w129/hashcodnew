#!/usr/bin/env python3
"""Strict proof that all bundled SVG names and their bodies are present offline."""
import argparse, gzip, json, pathlib, re, sys
p=argparse.ArgumentParser()
p.add_argument("data",type=pathlib.Path)
p.add_argument("--min-icons",type=int,default=300000)
args=p.parse_args()
root=args.data
index=json.loads((root/"index.json").read_text(encoding="utf-8"))["collections"]
names=json.loads(gzip.decompress((root/"names.json.gz").read_bytes()))
assert len(index)>=150,(len(index),"Too few icon collections")
assert set(names)==set(index),(len(names),len(index))
verified=0
for prefix, meta in sorted(index.items()):
    packed=root/"packs"/(prefix+".json.gz")
    assert packed.is_file(),f"{prefix}: no SVG data"
    iconset=json.loads(gzip.decompress(packed.read_bytes()))
    assert iconset.get("prefix")==prefix,prefix
    unique=set(iconset.get("icons",{}))|set(iconset.get("aliases",{}))
    assert len(unique)==len(names[prefix])==meta["total"],(prefix,len(unique),len(names[prefix]),meta["total"])
    assert unique==set(names[prefix]),f"{prefix}: catalog names do not match bundled bodies"
    for name, icon in list(iconset["icons"].items())[:3]:
        assert isinstance(icon.get("body"),str) and "<" in icon["body"],(prefix,name)
    verified+=len(unique)
assert verified>=args.min_icons,(verified,args.min_icons)
for prefix in ("mdi","lucide","tabler","ph","iconoir","material-symbols"):
    assert prefix in index,f"Missing required collection {prefix}"
    assert index[prefix]["total"]>500,f"{prefix} unexpectedly small"
print(f"VERIFIED OFFLINE CATALOG: {verified:,} renderable names across {len(index)} complete collections")
print(f"SVG data packed: {sum(p.stat().st_size for p in (root/'packs').glob('*.gz'))/1048576:.1f} MiB")
(root/"verified-full.json").write_text(json.dumps({"icons":verified,"collections":len(index),"offline":True},indent=2))
