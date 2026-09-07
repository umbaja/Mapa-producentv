import base64, pathlib
def b64(p, mime="image/png"):
    return f"data:{mime};base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()
import pathlib as _pl
FOOT_IMG = b64(str(_pl.Path(__file__).resolve().parent / 'img' / 'logos_footer.png'))
HEADER = ('<div style="width:100%;height:100%;font-family:Carlito,sans-serif;font-size:8pt;'
          '-webkit-print-color-adjust:exact;">'
          '<table style="width:160mm;margin:12.4mm auto 0;border-collapse:collapse">'
          '<tr><td style="height:8.2mm;background-color:#1a1a1a;font-size:0;line-height:0">&nbsp;</td></tr>'
          '</table></div>')
FOOTER = ('<div style="width:100%;font-family:Carlito,Calibri,sans-serif;font-size:8pt;color:#111;">'
          f'<div style="width:160mm;margin:6mm auto 0;"><img src="{FOOT_IMG}" style="width:160mm;display:block"></div>'
          '<div style="width:160mm;margin:1.5mm auto 0;display:flex;justify-content:space-between;align-items:baseline">'
          '<span style="font-size:8.5pt">&#8222;Financované E&#218; NextGenerationEU prostredn&#237;ctvom '
          'Pl&#225;nu obnovy a odolnosti SR v r&#225;mci projektu &#269;. 09I04-03-V02-00025&#8220;.</span>'
          '<span style="font-size:8.5pt" class="pageNumber"></span></div></div>')
