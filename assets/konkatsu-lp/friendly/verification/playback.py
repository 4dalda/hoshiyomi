from playwright.sync_api import sync_playwright
from pathlib import Path
import base64,json
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for name in ['pc','mobile']:
  page=b.new_page()
  data=base64.b64encode(Path(f'/workspace/work/visual-qa/{name}-scroll.mp4').read_bytes()).decode()
  page.set_content('<video muted playsinline controls src="data:video/mp4;base64,'+data+'"></video>')
  page.locator('video').evaluate('(v)=>v.play()');page.wait_for_timeout(2200)
  state=page.locator('video').evaluate('(v)=>({time:v.currentTime,duration:v.duration,width:v.videoWidth,height:v.videoHeight,error:v.error})')
  assert state['time']>1 and state['error'] is None
  page.locator('video').evaluate('(v)=>{v.currentTime=v.duration-1}')
  page.wait_for_timeout(1600)
  assert page.locator('video').evaluate('(v)=>v.ended')
  results.append({'video':name,**state,'endPlayback':True})
 b.close()
Path('/workspace/work/visual-qa/playback.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results))
