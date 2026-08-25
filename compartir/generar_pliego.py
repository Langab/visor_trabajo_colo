# -*- coding: utf-8 -*-
"""Genera la página compartible (pliego) a partir de data/jobs.json."""
import json, html, datetime, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data", "jobs.json")
OUT  = os.path.join(BASE, "index.html")
OUT2 = os.path.join(BASE, "compartir", "pliego.html")

PASADA   = "2026-08-25"
ANTERIOR = "2026-08-20"
# Ofertas confirmadas hoy como activas vía la API pública de Get on Board
VERIFICADAS_HOY = {"Healthatom", "Penji", "Hadley Designs", "Envíame", "Commerce Theory"}

MESES = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
def fecha_corta(iso):
    if not iso: return ""
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {MESES[m]}"

def dias_hasta(iso):
    if not iso: return None
    y, m, d = (int(x) for x in iso.split("-"))
    hoy = datetime.date(*(int(x) for x in PASADA.split("-")))
    return (datetime.date(y, m, d) - hoy).days

MOD = {"remoto": "Remoto", "hibrido": "Híbrido", "presencial": "Presencial", "no_especificado": "Modalidad sin declarar"}
FIT_LABEL = {"high": "Calce alto", "medium": "Calce medio", "low": "Calce bajo"}
FIT_NOTA = {
    "high":   "Lo que piden es lo que ya hiciste. Aquí se postula.",
    "medium": "Calzas en el core, pero hay requisitos que hoy no tienes. Vale la pena con carta bien armada.",
    "low":    "Quedan registradas por transparencia: el requisito duro está lejos de tu perfil hoy.",
}
e = lambda s: html.escape(str(s or ""), quote=True)

def densitometro(pct, fit):
    if not pct: return '<span class="dens-na">sin %</span>'
    llenas = max(1, round(pct / 10))
    celdas = "".join(f'<i class="{"on" if i < llenas else ""}"></i>' for i in range(10))
    return (f'<span class="dens fit-{fit}" role="img" aria-label="calce {pct} por ciento">{celdas}</span>'
            f'<span class="dens-num">{pct}<small>%</small></span>')

d = json.load(open(DATA, encoding="utf-8"))
jobs = d["jobs"]
nuevas   = [j for j in jobs if j.get("first_seen") == PASADA]
previas  = [j for j in jobs if j.get("first_seen") == ANTERIOR]
nuevas.sort(key=lambda j: (-(j.get("match_pct") or 0)))
previas.sort(key=lambda j: (-(j.get("match_pct") or 0), j["company"]))

orden_fit = {"high": 0, "medium": 1, "low": 2}
grupos = {"high": [], "medium": [], "low": []}
for j in nuevas: grupos[j["fit"]].append(j)

# ---- prioridad de la semana (orden de postulación) ----
PRIORIDAD = [
    ("Diseñador/a de Marca Propia Regional (packaging)",
     "Es tu cargo escrito por otra persona: packaging, artes finales y proveedores en China. Y la fecha de contratación es el 31 de agosto."),
    ("Diseñador/a (packaging, producto y fotografía)",
     "Se publicó hoy: llegar el primer día pesa. Junta packaging con sesiones de fotos, que es tu combo raro."),
    ("Diseñador/a Gráfico Jr Visual Merchandising — Paris",
     "POP, imprentas y control de calidad en tienda. El calce técnico es total; el «Jr» se negocia después."),
    ("Productor Gráfico (Diseñador de Producción)",
     "Agencia global y un cargo donde la preprensa es la habilidad principal, no un extra."),
]
por_titulo = {j["title"]: j for j in nuevas}

# ---- lectura de mercado (brechas contadas sobre las 13 nuevas) ----
def cuenta(palabras):
    n = 0
    for j in nuevas:
        blob = " ".join(j.get("gaps") or []).lower()
        if any(p in blob for p in palabras): n += 1
    return n
MERCADO = [
    ("Motion y video", cuenta(["motion", "video", "capcut", "premiere", "after effects", "animad", "dron", "cámara"]),
     "Reels, animación de piezas y edición para redes. Pasó a ser el requisito más repetido de la pasada."),
    ("IA generativa", cuenta(["ia ", "ia)", "inteligencia artificial", "midjourney", "firefly", "runway", "claude", "gemini"]),
     "Firefly y Midjourney aparecen por nombre. Como ya dominas Adobe, Firefly es la puerta de entrada más corta."),
    ("Inglés de trabajo", cuenta(["inglés"]),
     "De intermedio a C2 según la oferta. Es lo que separa las remotas bien pagadas del resto."),
    ("HTML y CMS", cuenta(["html", "contentful"]),
     "Email marketing y gestores de contenido. Aparece solo en las de canal digital de retail."),
]
MAXG = max(m[1] for m in MERCADO) or 1

# ---------------- HTML ----------------
def fila(j, idx):
    dias = dias_hasta(j.get("deadline"))
    plazo = ""
    if dias is not None:
        clase = "plazo urgente" if dias <= 10 else "plazo"
        cuando = "cierra hoy" if dias == 0 else (f"quedan {dias} días" if dias > 0 else "plazo vencido")
        plazo = f'<span class="{clase}">Contratación {fecha_corta(j["deadline"])} · {cuando}</span>'
    renta = f'<span class="renta">{e(j["salary"])}</span>' if j.get("salary") else ""
    gaps = ""
    if j.get("gaps"):
        chips = "".join(f'<li>{e(g)}</li>' for g in j["gaps"])
        gaps = f'<div class="faltantes"><span class="faltantes-t">Le falta</span><ul>{chips}</ul></div>'
    return f'''
    <article class="run fit-{j["fit"]}">
      <div class="run-rank">{idx:02d}</div>
      <div class="run-body">
        <h3><a href="{e(j["url"])}" target="_blank" rel="noopener">{e(j["title"])}</a></h3>
        <p class="run-empresa">{e(j["company"])}</p>
        <p class="run-meta">
          <span>{e(j["location"])}</span><span>{e(MOD.get(j["modality"], j["modality"]))}</span>
          <span>{e(j["source"])}</span><span>Publicada {fecha_corta(j.get("date_posted"))}</span>
        </p>
        {plazo}{renta}
        <p class="run-nota">{e(j["notes"])}</p>
        {gaps}
        <p class="run-cta"><a href="{e(j["url"])}" target="_blank" rel="noopener">Ver y postular →</a></p>
      </div>
      <div class="run-calce">{densitometro(j.get("match_pct"), j["fit"])}<span class="run-fit">{FIT_LABEL[j["fit"]]}</span></div>
    </article>'''

secciones = []
n = 0
for fit in ("high", "medium", "low"):
    if not grupos[fit]: continue
    filas = []
    for j in grupos[fit]:
        n += 1
        filas.append(fila(j, n))
    secciones.append(f'''
    <div class="grupo">
      <div class="grupo-head fit-{fit}">
        <h3>{FIT_LABEL[fit]} <span class="grupo-n">{len(grupos[fit])} {"oferta" if len(grupos[fit])==1 else "ofertas"}</span></h3>
        <p>{FIT_NOTA[fit]}</p>
      </div>
      {"".join(filas)}
    </div>''')

prioridad_html = "".join(
    f'''<li>
        <span class="prio-n">{i}</span>
        <div>
          <a href="{e(por_titulo[t]["url"])}" target="_blank" rel="noopener">{e(por_titulo[t]["title"])}</a>
          <span class="prio-emp">{e(por_titulo[t]["company"])}</span>
          <p>{e(razon)}</p>
        </div>
      </li>''' for i, (t, razon) in enumerate(PRIORIDAD, 1) if t in por_titulo)

mercado_html = "".join(
    f'''<li>
      <div class="merc-top"><span class="merc-t">{e(t)}</span><span class="merc-n">{c}<small>/{len(nuevas)}</small></span></div>
      <div class="merc-bar"><span style="width:{round(c / MAXG * 100)}%"></span></div>
      <p>{e(desc)}</p>
    </li>''' for t, c, desc in MERCADO)

previas_html = "".join(
    f'''<tr>
      <td><a href="{e(j["url"])}" target="_blank" rel="noopener">{e(j["title"])}</a></td>
      <td>{e(j["company"])}</td>
      <td class="mono">{e(j["source"])}</td>
      <td class="mono num">{(str(j["match_pct"]) + "%") if j.get("match_pct") else "—"}</td>
      <td>{'<span class="viva">Activa hoy</span>' if j["company"].split(" (")[0] in VERIFICADAS_HOY else '<span class="sinver">Sin verificar</span>'}</td>
    </tr>''' for j in previas)

TOKENS_OSCURO = """
    --papel:#131311; --pliego:#1C1C19; --tinta:#EFECE4; --tinta-2:#A19B8E; --regla:#33322D;
    --cian:#4FC3E8; --ocre:#DCAE33; --magenta:#F576A8; --gris-tinta:#949086;
    --pliego-alt:#232320; --sombra:0 1px 0 rgba(255,255,255,.03);
"""

altas = len(grupos["high"]); con_renta = sum(1 for j in nuevas if j.get("salary"))

html_out = f'''<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Pliego de ofertas</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>
  :root {{
    --papel:#EBE8E1; --pliego:#F8F7F4; --tinta:#1B1A17; --tinta-2:#6B675E; --regla:#D8D4CA;
    --cian:#0E6B86; --ocre:#8A6A00; --magenta:#C22A6B; --gris-tinta:#87837A;
    --pliego-alt:#F1EFEA; --sombra:0 1px 0 rgba(27,26,23,.04);
    --display:"Archivo", "Helvetica Neue", Arial, sans-serif;
    --lectura:"Newsreader", Georgia, "Times New Roman", serif;
    --dato:"IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
    --sheet-max:980px;
  }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{{TOKENS_OSCURO}}} }}
  :root[data-theme="dark"] {{{TOKENS_OSCURO}}}

  *, *::before, *::after {{ box-sizing:border-box; }}
  body {{
    margin:0; background:var(--papel); color:var(--tinta);
    font-family:var(--lectura); font-size:17px; line-height:1.6;
    -webkit-font-smoothing:antialiased;
  }}
  a {{ color:inherit; }}
  a:focus-visible, summary:focus-visible {{ outline:2px solid var(--cian); outline-offset:3px; border-radius:2px; }}

  .hoja {{ max-width:var(--sheet-max); margin:0 auto; padding:34px 22px 90px; position:relative; }}
  /* marcas de corte */
  .corte {{ position:absolute; width:22px; height:22px; pointer-events:none; }}
  .corte::before, .corte::after {{ content:""; position:absolute; background:var(--regla); }}
  .corte::before {{ width:100%; height:1px; top:0; }}
  .corte::after {{ height:100%; width:1px; left:0; }}
  .c-tl {{ top:10px; left:6px; }}
  .c-tr {{ top:10px; right:6px; transform:scaleX(-1); }}
  .c-bl {{ bottom:34px; left:6px; transform:scaleY(-1); }}
  .c-br {{ bottom:34px; right:6px; transform:scale(-1); }}
  @media (max-width:640px) {{ .corte {{ display:none; }} }}

  /* barra de tintas */
  .barra {{ display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin-bottom:26px; }}
  .tintas {{ display:flex; gap:3px; }}
  .tintas i {{ width:13px; height:13px; display:block; }}
  .tintas i:nth-child(1) {{ background:#00A3D9; }}
  .tintas i:nth-child(2) {{ background:#E5007D; }}
  .tintas i:nth-child(3) {{ background:#FFD500; }}
  .tintas i:nth-child(4) {{ background:#1B1A17; box-shadow:inset 0 0 0 1px var(--regla); }}
  .barra span {{ font-family:var(--dato); font-size:.7rem; letter-spacing:.14em; text-transform:uppercase; color:var(--tinta-2); }}

  h1 {{
    font-family:var(--display); font-weight:700; font-size:clamp(2.5rem,7vw,4.1rem);
    line-height:.95; letter-spacing:-.025em; margin:0 0 14px; text-wrap:balance;
  }}
  .lede {{ font-size:1.16rem; max-width:60ch; margin:0 0 30px; color:var(--tinta); }}
  .lede b {{ font-weight:500; box-shadow:inset 0 -.42em 0 color-mix(in srgb, var(--cian) 16%, transparent); }}

  .stats {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(128px,1fr)); gap:1px; margin:0 0 8px;
           background:var(--regla); border:1px solid var(--regla); }}
  .stats > div {{ background:var(--pliego); padding:14px 16px; }}
  .stats dt {{ font-family:var(--dato); font-size:.66rem; letter-spacing:.13em; text-transform:uppercase; color:var(--tinta-2); }}
  .stats dd {{ margin:4px 0 0; font-family:var(--display); font-weight:700; font-size:1.85rem; font-variant-numeric:tabular-nums; line-height:1; }}
  .stats dd small {{ font-size:.78rem; font-weight:500; color:var(--tinta-2); letter-spacing:0; }}

  section {{ margin-top:56px; }}
  .eyebrow {{
    font-family:var(--dato); font-size:.71rem; letter-spacing:.18em; text-transform:uppercase;
    color:var(--tinta-2); margin:0 0 4px; display:flex; align-items:center; gap:12px;
  }}
  .eyebrow::after {{ content:""; flex:1; height:1px; background:var(--regla); }}
  h2 {{ font-family:var(--display); font-weight:600; font-size:1.62rem; letter-spacing:-.015em; margin:0 0 6px; }}
  .sub {{ color:var(--tinta-2); margin:0 0 22px; max-width:62ch; font-size:1rem; }}

  /* prioridad */
  .prio {{ list-style:none; margin:0; padding:0; display:grid; gap:1px; background:var(--regla); border:1px solid var(--regla); }}
  .prio li {{ background:var(--pliego); display:flex; gap:16px; padding:16px 18px; align-items:baseline; }}
  .prio-n {{ font-family:var(--dato); font-size:.85rem; color:var(--magenta); font-weight:500; }}
  .prio a {{ font-family:var(--display); font-weight:600; font-size:1.03rem; text-decoration:none; border-bottom:1px solid var(--regla); }}
  .prio a:hover {{ border-bottom-color:var(--cian); color:var(--cian); }}
  .prio-emp {{ font-family:var(--dato); font-size:.72rem; color:var(--tinta-2); display:block; margin-top:3px; }}
  .prio p {{ margin:7px 0 0; font-size:.97rem; color:var(--tinta); }}

  /* grupos y filas */
  .grupo {{ margin-bottom:34px; }}
  .grupo-head {{ border-top:2px solid var(--tinta); padding-top:10px; margin-bottom:6px; }}
  .grupo-head.fit-high {{ border-top-color:var(--cian); }}
  .grupo-head.fit-medium {{ border-top-color:var(--ocre); }}
  .grupo-head.fit-low {{ border-top-color:var(--gris-tinta); }}
  .grupo-head h3 {{ font-family:var(--display); font-weight:600; font-size:1.08rem; margin:0; display:flex; gap:10px; align-items:baseline; }}
  .grupo-n {{ font-family:var(--dato); font-size:.72rem; color:var(--tinta-2); font-weight:400; }}
  .grupo-head p {{ margin:2px 0 0; font-size:.94rem; color:var(--tinta-2); }}

  .run {{
    display:grid; grid-template-columns:44px 1fr 132px; gap:18px;
    background:var(--pliego); border:1px solid var(--regla); border-top:none; padding:20px 18px;
  }}
  .grupo .run:first-of-type {{ border-top:1px solid var(--regla); }}
  .run-rank {{ font-family:var(--dato); font-size:.95rem; color:var(--tinta-2); padding-top:3px; }}
  .run h3 {{ margin:0; font-family:var(--display); font-weight:600; font-size:1.16rem; letter-spacing:-.01em; line-height:1.25; text-wrap:balance; }}
  .run h3 a {{ text-decoration:none; border-bottom:1.5px solid var(--regla); }}
  .run h3 a:hover {{ color:var(--cian); border-bottom-color:var(--cian); }}
  .run-empresa {{ margin:5px 0 0; font-family:var(--display); font-weight:500; font-size:.95rem; color:var(--tinta-2); }}
  .run-meta {{ display:flex; flex-wrap:wrap; gap:6px 14px; margin:9px 0 0; font-family:var(--dato); font-size:.7rem;
              letter-spacing:.05em; text-transform:uppercase; color:var(--tinta-2); }}
  .run-meta span + span::before {{ content:"·"; margin-right:14px; }}
  .plazo, .renta {{
    display:inline-block; margin:11px 8px 0 0; font-family:var(--dato); font-size:.72rem;
    padding:3px 9px; border:1px solid var(--regla); color:var(--tinta-2);
  }}
  .plazo.urgente {{ color:var(--magenta); border-color:color-mix(in srgb, var(--magenta) 45%, transparent); }}
  .renta {{ color:var(--cian); border-color:color-mix(in srgb, var(--cian) 40%, transparent); }}
  .run-nota {{ margin:12px 0 0; max-width:64ch; }}
  .faltantes {{ margin-top:12px; display:flex; gap:9px; flex-wrap:wrap; align-items:baseline; }}
  .faltantes-t {{ font-family:var(--dato); font-size:.66rem; letter-spacing:.13em; text-transform:uppercase; color:var(--magenta); }}
  .faltantes ul {{ list-style:none; display:flex; flex-wrap:wrap; gap:6px; margin:0; padding:0; }}
  .faltantes li {{ font-family:var(--dato); font-size:.71rem; padding:2px 8px; background:var(--pliego-alt);
                  border:1px solid var(--regla); color:var(--tinta-2); }}
  .run-cta {{ margin:14px 0 0; }}
  .run-cta a {{ font-family:var(--display); font-weight:600; font-size:.87rem; text-decoration:none; color:var(--cian); }}
  .run-cta a:hover {{ text-decoration:underline; }}

  .run-calce {{ text-align:right; }}
  .dens {{ display:flex; gap:2px; justify-content:flex-end; margin-bottom:7px; }}
  .dens i {{ width:9px; height:16px; background:var(--regla); display:block; }}
  .dens.fit-high i.on {{ background:var(--cian); }}
  .dens.fit-medium i.on {{ background:var(--ocre); }}
  .dens.fit-low i.on {{ background:var(--gris-tinta); }}
  .dens-num {{ font-family:var(--display); font-weight:700; font-size:1.5rem; font-variant-numeric:tabular-nums; display:block; line-height:1; }}
  .dens-num small {{ font-size:.74rem; color:var(--tinta-2); }}
  .dens-na {{ font-family:var(--dato); font-size:.72rem; color:var(--tinta-2); }}
  .run-fit {{ font-family:var(--dato); font-size:.66rem; letter-spacing:.11em; text-transform:uppercase; color:var(--tinta-2); display:block; margin-top:5px; }}
  @media (max-width:700px) {{
    .run {{ grid-template-columns:34px 1fr; }}
    .run-calce {{ grid-column:2; text-align:left; display:flex; align-items:baseline; gap:12px; }}
    .dens {{ justify-content:flex-start; margin:0; }}
    .run-fit {{ margin:0; }}
  }}

  /* mercado */
  .mercado {{ list-style:none; margin:0; padding:0; display:grid; gap:22px; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); }}
  .merc-top {{ display:flex; justify-content:space-between; align-items:baseline; gap:10px; }}
  .merc-t {{ font-family:var(--display); font-weight:600; font-size:1.02rem; }}
  .merc-n {{ font-family:var(--display); font-weight:700; font-size:1.35rem; font-variant-numeric:tabular-nums; }}
  .merc-n small {{ font-size:.75rem; color:var(--tinta-2); font-weight:500; }}
  .merc-bar {{ height:7px; background:var(--regla); margin:8px 0 9px; }}
  .merc-bar span {{ display:block; height:100%; background:var(--cian); }}
  .mercado p {{ margin:0; font-size:.95rem; color:var(--tinta-2); }}

  /* tabla previas */
  .tabla-wrap {{ overflow-x:auto; border:1px solid var(--regla); }}
  table {{ border-collapse:collapse; width:100%; min-width:620px; background:var(--pliego); }}
  th {{ font-family:var(--dato); font-size:.66rem; letter-spacing:.13em; text-transform:uppercase; color:var(--tinta-2);
       text-align:left; padding:11px 14px; border-bottom:1px solid var(--regla); font-weight:400; }}
  td {{ padding:11px 14px; border-bottom:1px solid var(--regla); font-size:.95rem; vertical-align:top; }}
  tr:last-child td {{ border-bottom:none; }}
  td a {{ font-family:var(--display); font-weight:500; font-size:.95rem; text-decoration:none; border-bottom:1px solid var(--regla); }}
  td a:hover {{ color:var(--cian); border-bottom-color:var(--cian); }}
  td.mono {{ font-family:var(--dato); font-size:.75rem; color:var(--tinta-2); }}
  td.num {{ font-variant-numeric:tabular-nums; }}
  .viva {{ font-family:var(--dato); font-size:.68rem; color:var(--cian); }}
  .sinver {{ font-family:var(--dato); font-size:.68rem; color:var(--tinta-2); }}
  .aviso {{ border-left:2px solid var(--magenta); padding:2px 0 2px 14px; color:var(--tinta-2); font-size:.96rem; margin:0 0 20px; max-width:64ch; }}

  footer {{ margin-top:60px; border-top:1px solid var(--regla); padding-top:20px;
           font-family:var(--dato); font-size:.74rem; line-height:1.85; color:var(--tinta-2); }}
  footer p {{ margin:0 0 8px; max-width:70ch; }}
  footer b {{ color:var(--tinta); font-weight:500; }}
  @media (max-width:520px) {{
    body {{ font-size:16px; }}
    .hoja {{ padding:24px 16px 70px; }}
    h1 {{ font-size:clamp(2.1rem,10vw,3rem); }}
    .run {{ padding:18px 14px; gap:12px; }}
    .prio li {{ padding:14px 15px; }}
  }}
  @media (prefers-reduced-motion: reduce) {{ * {{ animation:none !important; transition:none !important; }} }}
</style>

<div class="hoja">
  <span class="corte c-tl"></span><span class="corte c-tr"></span>
  <span class="corte c-bl"></span><span class="corte c-br"></span>

  <header>
    <div class="barra">
      <span class="tintas"><i></i><i></i><i></i><i></i></span>
      <span>Pasada 25.08.2026 · Santiago · Diseño</span>
    </div>
    <h1>Pliego de ofertas</h1>
    <p class="lede">Barrido de LinkedIn, Get on Board y portales chilenos hecho hoy, filtrado contra tu perfil:
      branding, packaging, producción gráfica, dirección de arte y RRSS.
      <b>{len(nuevas)} ofertas nuevas</b> desde la última pasada del 20 de agosto, con lo que pide cada una,
      lo que te falta y en qué orden conviene postular.</p>
    <dl class="stats">
      <div><dt>Nuevas hoy</dt><dd>{len(nuevas)}</dd></div>
      <div><dt>Calce alto</dt><dd>{altas}</dd></div>
      <div><dt>Con renta publicada</dt><dd>{con_renta}</dd></div>
      <div><dt>Registradas en total</dt><dd>{len(jobs)}</dd></div>
    </dl>
  </header>

  <section>
    <p class="eyebrow">Orden de postulación</p>
    <h2>Esta semana, en este orden</h2>
    <p class="sub">Priorizadas por calce real y por reloj: dos tienen fecha de contratación a la vista y una se publicó hoy.</p>
    <ol class="prio">{prioridad_html}</ol>
  </section>

  <section>
    <p class="eyebrow">Las {len(nuevas)} nuevas</p>
    <h2>Detalle de cada oferta</h2>
    <p class="sub">El número marca el orden de calce, de mayor a menor. La barra de la derecha es el porcentaje
      de coincidencia con tu perfil, leído sobre la descripción completa de cada aviso.</p>
    {"".join(secciones)}
  </section>

  <section>
    <p class="eyebrow">Lectura de mercado</p>
    <h2>Lo que pidieron las ofertas de esta pasada</h2>
    <p class="sub">Contado sobre las {len(nuevas)} descripciones completas. El orden cambió respecto de la pasada anterior:
      hoy el video pesa más que la IA.</p>
    <ul class="mercado">{mercado_html}</ul>
  </section>

  <section>
    <p class="eyebrow">Pasada anterior</p>
    <h2>Las {len(previas)} del 20 de agosto</h2>
    <p class="aviso">Estas venían de la pasada anterior y no se volvieron a abrir una por una hoy. Las cinco de Get on Board
      sí se confirmaron activas; el resto puede haberse cerrado, así que revisa el enlace antes de preparar carta.</p>
    <div class="tabla-wrap">
      <table>
        <thead><tr><th>Cargo</th><th>Empresa</th><th>Portal</th><th>Calce</th><th>Estado</th></tr></thead>
        <tbody>{previas_html}</tbody>
      </table>
    </div>
  </section>

  <footer>
    <p><b>Cómo se armó.</b> Búsquedas en LinkedIn (Santiago y remoto Chile, avisos de los últimos 7 a 21 días),
      la API pública de Get on Board en Diseño/UX, Publicidad y Marketing digital, y Chiletrabajos.
      Cada oferta nueva se abrió completa para leer requisitos, renta y plazos: nada de esto viene de un resumen automático.</p>
    <p><b>Qué no está.</b> Prácticas profesionales, avisos fuera de la Región Metropolitana, UX/UI de producto
      y diseño industrial. Tampoco ofertas ya registradas antes del 20 de agosto.</p>
    <p><b>¿Quieres filtrar y marcar postulaciones?</b> El visor completo, con las 35 ofertas, filtros por
      categoría y modalidad, análisis de perfil y seguimiento de postulaciones, está en
      <a href="viewer/">/viewer/</a>.</p>
    <p>Generado el 25 de agosto de 2026 para Andrea Ortega · buscador de trabajo de Benjamín Lang</p>
  </footer>
</div>
'''

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf-8").write(html_out)
open(OUT2, "w", encoding="utf-8").write(html_out)
print("escrito:", OUT, "y", OUT2, "-", len(html_out), "bytes")
print("nuevas:", len(nuevas), "| altas:", altas, "| previas:", len(previas), "| con renta:", con_renta)
print("mercado:", [(t, c) for t, c, _ in MERCADO])
