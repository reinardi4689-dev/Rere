#!/usr/bin/env python3
"""Escanea los SKILL.md instalados y genera un catálogo (Markdown o JSON).

Uso:
  python3 catalogar.py                 # Markdown agrupado por origen
  python3 catalogar.py --json          # JSON (para que Claude lo reclasifique)
  python3 catalogar.py --buscar pdf    # filtra por texto en nombre/descripción
  python3 catalogar.py --raiz /ruta    # añade raíces extra a escanear
Solo usa la biblioteca estándar.
"""
import argparse, json, os, re, sys
from pathlib import Path

IGNORAR = ("inactive-skills", "/.cursor/", "/.skills/", "/node_modules/", "/.git/")


def raices_por_defecto():
    home = Path.home()
    cwd = Path.cwd()
    raices = [("personal", home / ".claude" / "skills"),
              ("plugin", home / ".claude" / "plugins")]
    # Skills del proyecto: .claude/skills en el cwd y en sus padres
    for d in [cwd, *cwd.parents]:
        p = d / ".claude" / "skills"
        if p.is_dir() and p != home / ".claude" / "skills":
            raices.append(("proyecto", p))
    return raices


def parse_frontmatter(texto):
    m = re.match(r"^---\s*\n(.*?)\n---", texto, re.S)
    if not m:
        return {}
    datos, clave, bloque = {}, None, []
    for linea in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", linea)
        if km and not linea.startswith((" ", "\t")):
            if clave and bloque:
                datos[clave] = " ".join(x.strip() for x in bloque if x.strip())
            clave, valor = km.group(1), km.group(2).strip()
            bloque = []
            if valor in (">", "|", ">-", "|-", ">+", "|+", ""):
                datos[clave] = ""
            else:
                datos[clave] = valor.strip("'\"").replace('\\"', '"')
                clave = None if valor else clave
        elif clave is not None:
            bloque.append(linea)
    if clave and bloque:
        datos[clave] = " ".join(x.strip() for x in bloque if x.strip())
    return datos


def nombre_plugin(ruta, raiz):
    for d in ruta.parents:
        if d == raiz or raiz not in d.parents and d != raiz:
            break
        manifiesto = d / ".claude-plugin" / "plugin.json"
        if manifiesto.is_file():
            try:
                return json.loads(manifiesto.read_text(encoding="utf-8")).get("name") or d.name
            except Exception:
                return d.name
    return None


def escanear(raices):
    vistos, skills = set(), []
    for origen, raiz in raices:
        if not raiz.is_dir():
            continue
        for ruta in sorted(raiz.rglob("SKILL.md")):
            s = str(ruta)
            if any(x in s for x in IGNORAR):
                continue
            try:
                fm = parse_frontmatter(ruta.read_text(encoding="utf-8", errors="replace"))
            except OSError:
                continue
            nombre = fm.get("name") or ruta.parent.name
            plugin = nombre_plugin(ruta, raiz) if origen == "plugin" else None
            grupo = f"plugin: {plugin}" if plugin else origen
            if origen == "personal" and "/synced/" in s:
                grupo = "claude.ai (sincronizadas)"
            invocacion = f"{plugin}:{nombre}" if plugin else nombre
            if grupo == "claude.ai (sincronizadas)":
                invocacion = f"anthropic-skills:{nombre}"
            clave = (grupo, nombre)
            if clave in vistos:
                continue
            vistos.add(clave)
            skills.append({
                "nombre": nombre,
                "invocacion": invocacion,
                "grupo": grupo,
                "descripcion": fm.get("description", "").strip(),
                "ruta": s,
            })
    return skills


def a_markdown(skills, max_desc):
    grupos = {}
    for sk in skills:
        grupos.setdefault(sk["grupo"], []).append(sk)
    out = [f"# Catálogo de skills ({len(skills)} encontradas)\n"]
    for g in sorted(grupos):
        out.append(f"\n## {g} ({len(grupos[g])})\n")
        out.append("| Skill | Descripción |\n|---|---|")
        for sk in sorted(grupos[g], key=lambda x: x["invocacion"]):
            d = sk["descripcion"].replace("|", "\\|") or "_(sin descripción)_"
            if max_desc and len(d) > max_desc:
                d = d[: max_desc - 1].rstrip() + "…"
            out.append(f"| `{sk['invocacion']}` | {d} |")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--buscar")
    ap.add_argument("--raiz", action="append", default=[])
    ap.add_argument("--max-desc", type=int, default=200,
                    help="recorta descripciones en Markdown (0 = sin recortar)")
    a = ap.parse_args()
    raices = raices_por_defecto() + [("extra", Path(r).expanduser()) for r in a.raiz]
    skills = escanear(raices)
    if a.buscar:
        q = a.buscar.lower()
        skills = [s for s in skills if q in (s["nombre"] + " " + s["descripcion"]).lower()]
    if a.json:
        json.dump(skills, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        sys.stdout.write(a_markdown(skills, a.max_desc))


if __name__ == "__main__":
    main()
