from playwright.sync_api import sync_playwright
import json
from pathlib import Path
out=Path('/workspace/work/visual-qa')
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 results=[]
 for width,height in [(1440,900),(390,844)]:
  page=b.new_page(viewport={'width':width,'height':height})
  page.goto('http://127.0.0.1:4173/assets/konkatsu-lp/friendly/');page.wait_for_timeout(500)
  initial=page.locator('[data-layer=text]').evaluate('(e)=>getComputedStyle(e).transform')
  for progress in [0,.25,.5,.75,1]:
   page.evaluate('(p)=>{const e=document.querySelector(".hero"),s=document.querySelector(".scene");scrollTo({top:p*(e.offsetHeight-s.offsetHeight),behavior:"instant"})}',progress)
   page.wait_for_timeout(100)
   assert not page.evaluate('document.documentElement.scrollWidth>innerWidth')
  page.screenshot(path=str(out/f'{width}-scene-end.png'))
  page.evaluate('scrollTo({top:0,behavior:"instant"})');page.wait_for_timeout(100)
  assert page.locator('[data-layer=text]').evaluate('(e)=>getComputedStyle(e).transform')==initial
  page.emulate_media(reduced_motion='reduce');page.wait_for_timeout(100)
  page.mouse.wheel(0,200);page.wait_for_timeout(200)
  for layer in ['background','light','person','text']:
   assert page.locator(f'[data-layer={layer}]').evaluate('(e)=>getComputedStyle(e).transform')=='none'
  results.append({'width':width,'progressSamples':[0,.25,.5,.75,1],'overflow':False,'reverseRestored':True,'reducedMotionTransforms':'none'})
  page.close()
 b.close()
(out/'verification.json').write_text(json.dumps(results,indent=2));print(json.dumps(results))
