from playwright.sync_api import sync_playwright
import json
from pathlib import Path
out=Path('/workspace/work/visual-qa')
url='http://127.0.0.1:4173/assets/konkatsu-lp/friendly/'
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 results=[]
 for name,width,height in [('pc',1440,900),('mobile',390,844)]:
  context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,record_video_dir=str(out/'videos'),record_video_size={'width':width,'height':height})
  page=context.new_page();errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(url);page.wait_for_timeout(900)
  page.screenshot(path=str(out/f'{name}-hero.png'))
  def metrics():
   return page.evaluate('''() => ({scroll:scrollY,overflow:document.documentElement.scrollWidth>innerWidth,layers:Object.fromEntries([...document.querySelectorAll('[data-layer]')].map(e=>[e.dataset.layer,{transform:getComputedStyle(e).transform,rect:{x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}}])),cta:(()=>{let r=document.querySelector('.cta').getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})()})''')
  initial=metrics(); samples=[initial]
  for i in range(5):
   page.mouse.wheel(0,100 if name=='pc' else 65);page.wait_for_timeout(250);samples.append(metrics())
  page.screenshot(path=str(out/f'{name}-parallax.png'))
  for i in range(5):page.mouse.wheel(0,-100 if name=='pc' else -65);page.wait_for_timeout(200)
  returned=metrics()
  for i in range(16):page.mouse.wheel(0,130);page.wait_for_timeout(150)
  page.locator('#concerns').scroll_into_view_if_needed();page.wait_for_timeout(900);page.screenshot(path=str(out/f'{name}-concerns.png'))
  page.locator('#strengths').scroll_into_view_if_needed();page.wait_for_timeout(900);page.screenshot(path=str(out/f'{name}-strengths.png'))
  page.evaluate('scrollTo(0,0)');page.wait_for_timeout(1000)
  page.locator('.hero-copy [data-consult]').click();page.wait_for_timeout(300)
  dialog=page.locator('dialog').evaluate('(e)=>e.open');page.keyboard.press('Escape')
  results.append({'viewport':[width,height],'initial':initial,'samples':samples,'returned':returned,'pageErrors':errors,'ctaDialog':dialog})
  video=page.video;context.close();video.save_as(str(out/f'{name}-scroll.webm'))
 browser.close()
(out/'metrics.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print('Captured PC and mobile screenshots, wheel scroll recordings, metrics.')
