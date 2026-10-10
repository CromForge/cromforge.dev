"""Builds the cromforge.dev static site (GitHub Pages) from the Purrsweeper privacy policy draft."""
import re, markdown, pathlib
SRC = pathlib.Path('_policy_src.md').read_text(encoding='utf-8')
DATE_EN, DATE_ES = '10 October 2026', '10 de octubre de 2026'

def clean(section):
    # drop [PLAY GAMES] replacement lines (italic "*[PLAY GAMES] replace ...*" plus continuation lines)
    out, skip = [], False
    for line in section.splitlines():
        if line.lstrip().startswith('*[PLAY GAMES]'):
            skip = True; continue
        if skip and line.startswith('  ') and not line.lstrip().startswith('-'):
            continue
        skip = False
        out.append(line)
    text = '\n'.join(out)
    # drop whole [PLAY GAMES] sections (### heading up to the next ###)
    text = re.sub(r'### \[PLAY GAMES\].*?(?=\n### )', '', text, flags=re.S)
    return text

en = SRC.split('## English', 1)[1].split('## Español', 1)[0].strip().strip('-').strip()
es = SRC.split('## Español', 1)[1].strip()
rep = {'[DEVELOPER NAME]': 'Crom Forge', '[NOMBRE DEL DESARROLLADOR]': 'Crom Forge',
       '[EMAIL]': '<a href="mailto:support@cromforge.dev">support@cromforge.dev</a>',
       '[CORREO]': '<a href="mailto:support@cromforge.dev">support@cromforge.dev</a>',
       ' · [POSTAL ADDRESS, if required in your country]': '', ' · [DIRECCIÓN POSTAL, si lo exige tu país]': '',
       '[DATE]': DATE_EN, '[FECHA]': DATE_ES}
def fill(t):
    for k, v in rep.items(): t = t.replace(k, v)
    assert '[' not in re.sub(r'\[[^\]]*\]\(', '', t).replace('[x]', ''), re.findall(r'\[[A-Z ]+[^\]]*\]', t)
    return t
en, es = fill(clean(en)), fill(clean(es))
en = re.sub(r'\*\*(Purrsweeper — Privacy Policy)\*\*\nLast updated: (.*)', r'# \1\n\n*Last updated: \2*', en)
es = re.sub(r'\*\*(Purrsweeper — Política de privacidad)\*\*\nÚltima actualización: (.*)', r'# \1\n\n*Última actualización: \2*', es)
md = lambda t: markdown.markdown(t, extensions=['extra'])
link = lambda h: re.sub(r'(?<![">])(https://[^\s<,]+)', r'<a href="\1">\1</a>', h)

CSS = """
:root{--bg:#1c1716;--panel:#2a2321;--ink:#f3e9d8;--muted:#b9ab97;--ember:#f07a2a;--gold:#ffc24a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
a{color:var(--gold)}header{display:flex;align-items:center;justify-content:space-between;padding:18px 24px;border-bottom:3px solid var(--ember)}
.brand{font-weight:800;letter-spacing:.12em;font-size:20px;text-decoration:none;color:var(--ink)}.brand b{color:var(--ember)}
nav a{margin-left:20px;text-decoration:none;color:var(--ink);font-weight:600;letter-spacing:.06em;font-size:14px}
main{max-width:820px;margin:0 auto;padding:32px 24px 64px}h1{font-size:34px;margin:.2em 0}h2{margin-top:2em;color:var(--gold)}h3{margin-top:1.6em}
.card{background:var(--panel);border-radius:14px;padding:24px;margin:24px 0}.muted{color:var(--muted)}
.lang{display:inline-block;margin-right:14px;font-weight:700}footer{text-align:center;color:var(--muted);font-size:14px;padding:24px}
"""
def page(title, body, desc):
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><meta name="description" content="{desc}"><link rel="icon" href="/favicon.png"><style>{CSS}</style></head><body>
<header><a class="brand" href="/">CROM <b>FORGE</b></a><nav><a href="/#games">GAMES</a><a href="/privacy/">PRIVACY</a><a href="mailto:support@cromforge.dev">CONTACT</a></nav></header>
<main>{body}</main><footer>© 2026 Crom Forge · <a href="mailto:support@cromforge.dev">support@cromforge.dev</a></footer></body></html>"""

index = """<h1>Small games, forged by hand.</h1>
<p class="muted">Crom Forge is an independent studio making cosy, handcrafted pixel-art games.</p>
<section id="games" class="card"><h2 style="margin-top:0">Purrsweeper</h2>
<p>Minesweeper with cats: no guessing, a stray to adopt and a house to restore. Every board can be solved by logic alone.</p>
<p class="muted">Coming soon to Google Play.</p>
<p><a href="/privacy/">Privacy policy</a> · <a href="/privacy/#es">Política de privacidad</a></p></section>
<p>Questions or feedback? <a href="mailto:support@cromforge.dev">support@cromforge.dev</a></p>"""

priv = f"""<p><a class="lang" href="#en">English</a><a class="lang" href="#es">Español</a></p>
<section id="en">{link(md(en))}</section><hr><section id="es" lang="es">{link(md(es))}</section>"""

out = pathlib.Path('site'); (out / 'privacy').mkdir(parents=True, exist_ok=True)
(out / 'index.html').write_text(page('Crom Forge', index, 'Crom Forge: an independent studio making cosy handcrafted games.'), encoding='utf-8')
(out / 'privacy' / 'index.html').write_text(page('Purrsweeper — Privacy Policy · Crom Forge', priv, 'Privacy policy for Purrsweeper by Crom Forge.'), encoding='utf-8')
(out / '404.html').write_text(page('Not found · Crom Forge', '<h1>Page not found</h1><p><a href="/">Back home</a></p>', 'Not found'), encoding='utf-8')
(out / 'CNAME').write_text('cromforge.dev\n')
(out / '.nojekyll').write_text('')
print('built', [str(p) for p in out.rglob('*') if p.is_file()])
