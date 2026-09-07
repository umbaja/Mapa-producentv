import base64, pathlib, sys
D = pathlib.Path(__file__).resolve().parent
def b64(p, m="image/png"):
    return f"data:{m};base64," + base64.b64encode((D/p).read_bytes()).decode()
css = (D/'sprava.css').read_text(encoding='utf-8')
body = "\n".join((D/f"c{i}.html").read_text(encoding='utf-8') for i in range(1,6))
for k, v, m in [('IMG_LOGO','img/logo_apetbio.png','image/png'),
                ('IMG_CELA','img/s_cela.jpg','image/jpeg'),
                ('IMG_SCENARE','img/s_scenare.jpg','image/jpeg')]:
    body = body.replace(k, b64(v, m))
(D/'sprava.html').write_text(
  f'<!doctype html><html lang="sk"><head><meta charset="utf-8"><title>D3.2</title>'
  f'<style>{css}</style></head><body>{body}</body></html>', encoding='utf-8')
sys.path.insert(0, str(D)); import head_foot
from playwright.sync_api import sync_playwright
OUT = D.parent/'APETBIO_D3-2_Energetika_uhlikova_stopa.pdf'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto((D/'sprava.html').as_uri()); pg.wait_for_timeout(2500)
    pg.pdf(path=str(OUT), format="A4",
           margin={"top":"26mm","bottom":"34mm","left":"25mm","right":"25mm"},
           print_background=True, display_header_footer=True,
           header_template=head_foot.HEADER, footer_template=head_foot.FOOTER)
    b.close()
import pypdfium2 as pdfium, os
pdf = pdfium.PdfDocument(str(OUT)); print("strán:", len(pdf), "| kB:", os.path.getsize(OUT)//1024, "|", OUT)
for i in [0,4,6]: pdf[i].render(scale=1.3).to_pil().save(f'/tmp/e{i+1}.png')
