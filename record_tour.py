
import asyncio, sys, json, base64, time, os
from playwright.async_api import async_playwright
OUT=sys.argv[1]; URL=sys.argv[2]; DSF=float(sys.argv[3]); H=int(sys.argv[4]); LIMIT=int(sys.argv[5]) if len(sys.argv)>5 else 10**9
os.makedirs(OUT,exist_ok=True)
FPS=30
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
        ctx=await b.new_context(viewport={"width":390,"height":H},device_scale_factor=DSF,is_mobile=True,has_touch=True)
        pg=await ctx.new_page()
        errs=[]
        pg.on("console",lambda m: errs.append(("console."+m.type,m.text)) if m.type in("error",) else None)
        pg.on("pageerror",lambda e: errs.append(("pageerror",str(e))))
        cdp=await ctx.new_cdp_session(pg)
        await pg.goto(URL, wait_until="load")
        await pg.evaluate("document.fonts.ready")
        await pg.evaluate("""()=>{const s=document.createElement('style');s.textContent='.tapdot{position:fixed;z-index:99999;width:64px;height:64px;margin:-32px 0 0 -32px;border-radius:50%;border:3px solid #D4AF72;background:rgba(212,175,114,.35);pointer-events:none;animation:tapd .7s ease-out forwards}@keyframes tapd{from{transform:scale(.4);opacity:1}to{transform:scale(1.5);opacity:0}}';document.head.appendChild(s);window.__tap=(sel)=>{const e=document.querySelector(sel);if(!e)return null;const r=e.getBoundingClientRect();const d=document.createElement('div');d.className='tapdot';d.style.left=(r.left+r.width/2)+'px';d.style.top=(r.top+r.height/2)+'px';document.body.appendChild(d);setTimeout(()=>d.remove(),800);return [r.left+r.width/2,r.top+r.height/2]}}""")
        fut=[None]
        def on_exp(ev):
            if fut[0] and not fut[0].done(): fut[0].set_result(1)
        cdp.on("Emulation.virtualTimeBudgetExpired",on_exp)
        await cdp.send("Emulation.setVirtualTimePolicy",{"policy":"pause"})
        n=[0]; vt=[0.0]
        async def advance(ms):
            fut[0]=asyncio.get_event_loop().create_future()
            await cdp.send("Emulation.setVirtualTimePolicy",{"policy":"advance","budget":ms})
            await asyncio.wait_for(fut[0],60)
            vt[0]+=ms
        async def grab():
            r=await cdp.send("Page.captureScreenshot",{"format":"jpeg","quality":90,"optimizeForSpeed":True,"clip":{"x":0,"y":0,"width":390,"height":H,"scale":DSF}})
            open(f"{OUT}/f{n[0]:05d}.jpg","wb").write(base64.b64decode(r["data"])); n[0]+=1
        async def cap(sec):
            for _ in range(int(round(sec*FPS))):
                await advance(1000/FPS); await grab()
        async def skip(sec):
            for _ in range(int(sec*10)): await advance(100)
        waits=[]
        async def wait_vis(sel,maxs=14):
            s0=n[0]
            for _ in range(maxs*30):
                ok=await pg.evaluate(f"(()=>{{const e=document.querySelector({json.dumps(sel)});if(!e||e.disabled)return false;const r=e.getBoundingClientRect();if(r.width<=0||r.bottom>window.innerHeight||r.top<0)return false;const x=r.left+r.width/2,y=r.top+r.height/2;const t=document.elementFromPoint(x,y);if(!(t&&(t===e||e.contains(t))))return false;let o=1,n=e;while(n&&n.nodeType==1){{o*=parseFloat(getComputedStyle(n).opacity);n=n.parentElement}}return o>0.85}})()")
                if ok:
                    waits.append((sel,s0,n[0])); return True
                await advance(1000/FPS); await grab()
            print("NOT VISIBLE",sel,flush=True); return False
        async def tap(sel,mw=14):
            ok=await wait_vis(sel,mw)
            if ok:
                xy=await pg.evaluate(f"__tap({json.dumps(sel)})")
                await advance(250); await grab()
                if xy:
                    await cdp.send("Input.dispatchTouchEvent",{"type":"touchStart","touchPoints":[{"x":xy[0],"y":xy[1]}]})
                    await cdp.send("Input.dispatchTouchEvent",{"type":"touchEnd","touchPoints":[]})
            else:
                print("JSCLICK",sel,flush=True)
                await pg.evaluate(f"document.querySelector({json.dumps(sel)}).click()")
        async def scroll_to(sel,top,secs):
            n=int(secs*FPS)
            for k in range(n):
                v=top*(k+1)/n
                await pg.evaluate(f"document.querySelector({json.dumps(sel)}).scrollTop={v}")
                await advance(1000/FPS); await grab()
        t0=time.time()
        def mark(nm): print(nm,"frames",n[0],"vt",round(vt[0]/1000,1),"wall",round(time.time()-t0),flush=True)
        S=json.loads(os.environ.get("SECS","{}"))
        # timeline
        await cap(1.2); mark("intro")
        await tap("#btnEnter"); await cap(1.0); mark("name")
        await wait_vis("#nameInput")
        for i,ch in enumerate("Your Name"):
            await pg.evaluate(f"(()=>{{const e=document.querySelector('#nameInput');e.value=e.value+{json.dumps(ch)};e.dispatchEvent(new Event('input',{{bubbles:true}}))}})()")
            await cap(0.08)
        await cap(0.2); mark("typed")
        await tap("#btnUnlock"); await cap(1.8); mark("reveal")
        await cap(1.2); mark("countdown")
        await wait_vis("#btnToFire"); await cap(1.9); await tap("#btnToFire"); await cap(0.5); mark("fire")
        await tap("#btnCelebrate"); await cap(2.4); mark("fire_show")
        await tap("#btnToCouple"); await cap(1.6); mark("couple")
        await tap("#btnToLetter"); await cap(0.6); mark("letter")
        await tap("#btnOpenLetter"); await cap(2.2); mark("letter_open")
        await scroll_to("#letterScroll",900,2.5); mark("scroll")
        await tap("#btnToPromise",2); await cap(2.0); mark("promise")
        await tap("#btnToGift",2); await cap(0.6); mark("gift")
        await tap("#btnOpenGift"); await cap(3.0); mark("gift_open")
        await tap("#btnToFinal",2); await cap(8.0); mark("final")
        json.dump(waits,open(OUT+"/waits.json","w"))
        print("ERRS",json.dumps(errs),flush=True)
        await b.close()
asyncio.run(main())
