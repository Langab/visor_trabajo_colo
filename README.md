# Visor de Trabajos — Andrea Ortega

Ofertas laborales de diseño gráfico (branding, packaging, dirección de arte, RRSS e ilustración)
en Santiago de Chile, recolectadas y curadas con Claude Code.

- **Pliego (portada, para compartir):** https://langab.github.io/visor_trabajo_colo/
- **Visor interactivo:** https://langab.github.io/visor_trabajo_colo/viewer/

## Estructura

- `index.html` — el pliego de la última pasada: ofertas nuevas ordenadas por calce, con requisitos,
  brechas y orden de postulación. Se genera desde `data/jobs.json`.
- `viewer/index.html` — visor con filtros, análisis de perfil vs. mercado, histórico y seguimiento
  de postulaciones. Carga `data/jobs.json` por `fetch`.
- `data/jobs.json` — ofertas recolectadas y curadas. Cada pasada agrega una entrada a `history`.
- `compartir/generar_pliego.py` — genera `index.html` (y una copia en `compartir/pliego.html`)
  a partir de `data/jobs.json`.

## Actualizar

1. Nueva pasada de búsqueda con Claude Code (LinkedIn, Get on Board, portales chilenos) → se agregan
   las ofertas a `data/jobs.json` con `first_seen` de hoy y una entrada nueva en `history`.
2. Regenerar el pliego:

   ```
   python3 compartir/generar_pliego.py
   ```

3. Commit y push: GitHub Pages publica desde `main`.

## Ver en local

El visor necesita servirse por HTTP (no abrir el archivo directo):

```
python -m http.server 8765
```

y abrir http://localhost:8765/ (pliego) o http://localhost:8765/viewer/ (visor).
