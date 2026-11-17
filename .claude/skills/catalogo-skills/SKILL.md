---
name: catalogo-skills
description: Cataloga las skills disponibles del usuario (personales, sincronizadas de claude.ai, de plugins y del proyecto), las agrupa por origen y por categoría temática y explica para qué sirve cada una y cómo invocarla. Úsala cuando el usuario pida "catalogar", "listar", "inventariar" o "ver qué skills tengo", busque una skill para una tarea ("¿tengo alguna skill para PDFs?") o quiera saber cuál usar.
---

# Catálogo de skills

Genera un catálogo claro y en castellano de las skills que el usuario tiene disponibles.

## Paso 1 — Recoger los datos

Ejecuta el script incluido (solo biblioteca estándar de Python):

```bash
python3 "<directorio de esta skill>/scripts/catalogar.py" --json
```

Opciones útiles:
- `--buscar <texto>`: filtra por nombre o descripción (p. ej. `--buscar pdf`).
- `--raiz <ruta>`: escanea una carpeta adicional de skills.
- Sin `--json` devuelve directamente una tabla Markdown agrupada por origen
  (`--max-desc 0` para no recortar descripciones).

El script recorre `~/.claude/skills` (personales y sincronizadas desde claude.ai),
`~/.claude/plugins` (agrupa por el nombre del plugin) y `.claude/skills` del proyecto
actual y sus carpetas padre. Ignora copias inactivas (`inactive-skills`, `.cursor`, `.skills`).

Si el script no puede ejecutarse o no encuentra nada (por ejemplo, en claude.ai, donde
las skills no están en `~/.claude`), sáltalo y usa solo la lista de skills disponibles
de tu contexto.

**Completa con la lista de la sesión.** Algunas skills vienen integradas en Claude Code
y no tienen `SKILL.md` en disco (p. ej. `code-review`, `simplify`, `loop`, `init`,
`security-review`, `claude-api`, `artifact-design`, `dataviz`…). Añade también las que
aparezcan en la lista de skills disponibles de tu contexto y no estén en la salida del
script, marcándolas como **integradas**. No inventes skills que no estén en ninguna de
las dos fuentes.

## Paso 2 — Clasificar

Asigna a cada skill **una** categoría temática a partir de su descripción. Categorías
sugeridas (usa solo las que tengan contenido y crea otra si hace falta):

- 📄 Documentos y oficina (PDF, Word, Excel, PowerPoint, Google Workspace)
- 🎨 Diseño y contenido visual (Figma, Canva, arte, GIFs)
- 📊 Datos y análisis (SQL, dashboards, visualización, estadística)
- 🤖 IA / ML y agentes (DataRobot, Claude API)
- 🔎 Investigación y web (deep research, scraping, navegador)
- 📈 SEO y marketing
- 🗂️ Productividad y memoria (tareas, resúmenes, correos, morning brief)
- 🎬 Ocio y colección personal (libros, cine, música…)
- 🛠️ Desarrollo y Claude Code (revisión de código, hooks, configuración, CMS)

## Paso 3 — Presentar

Responde en castellano con:

1. **Resumen**: total de skills y recuento por categoría y por origen.
2. **Tus skills**: antes del catálogo, una tabla aparte con las del grupo
   `creadas por ti (claude.ai)` más las de origen `personal` y `proyecto`
   (las que el usuario ha creado). Si no hay ninguna, dilo en una línea.
3. **Catálogo por categoría**: una tabla por categoría con columnas
   `Skill (cómo invocarla)` · `Para qué sirve` (una frase propia y breve, en castellano,
   no la descripción copiada) · `Origen`.
   La invocación es `/<nombre>`; para plugins `plugin:nombre`, para las sincronizadas
   `anthropic-skills:nombre`.
4. **Observaciones** (opcional, breve): duplicados o solapamientos entre skills,
   skills sin descripción, y cuál conviene para cada caso si hay varias parecidas.

Si el usuario buscaba algo concreto, responde primero con las 1–3 skills más adecuadas
y después, si lo pide, el catálogo completo.

Si el catálogo es largo (más de ~40 skills) y el usuario quiere guardarlo o compartirlo,
ofrece generarlo como página/documento en lugar de dejarlo solo en el chat.
