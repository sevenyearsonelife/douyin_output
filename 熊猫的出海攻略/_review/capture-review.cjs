const fs=require('fs'), path=require('path');
const root=path.dirname(__dirname), skill='/Users/linus/.codex/skills/douyin_pipeline';
const {chromium}=require(skill+'/node_modules/playwright');
const {openVideo}=require(skill+'/scripts/browser-media');
(async()=>{const ctx=await chromium.launchPersistentContext(skill+'/.douyin-browser-profile',{headless:false,viewport:{width:1400,height:1000}});try{
 const page=await ctx.newPage();const ledger=JSON.parse(fs.readFileSync(__dirname+'/text-review.json'));const rows=JSON.parse(fs.readFileSync(root+'/summary.json'));
 for(const row of rows.filter(r=>ledger.needs_review[r.homepageIndex]&&r.homepageIndex!==0)){
  const id=row.url.split('/').pop(),dir=path.join(__dirname,id);fs.mkdirSync(dir,{recursive:true});
  try{await openVideo(page,row.url);const player=page.locator('video').first();const duration=await player.evaluate(v=>v.duration);const out={video_url:row.url,homepageIndex:row.homepageIndex,duration,interval:10,truncated:false,frames:[]};
   for(let t=0;t<duration;t+=10){await player.evaluate((v,t)=>{v.pause();v.currentTime=t},t);await page.waitForFunction(t=>{const v=document.querySelector('video');return v&&!v.seeking&&v.readyState>=2&&Math.abs(v.currentTime-t)<.5},t,{timeout:15000});const file=t.toFixed(2).padStart(8,'0')+'.png';await player.screenshot({path:path.join(dir,file)});out.frames.push({time:t,file});
    const text=await page.locator('body').innerText();if(/购买后可看|购买完整版/.test(text)){out.truncated=true;out.access_restriction='paid_content';break;}
   } fs.writeFileSync(dir+'/frames.json',JSON.stringify(out,null,2));console.log('Frames index '+row.homepageIndex+': '+out.frames.length+(out.truncated?' restricted':''));
  }catch(e){console.log('Frame failure index '+row.homepageIndex+': '+e.message.replace(/https?:\/\/\S+/g,'[URL]'));}
 }
}finally{await ctx.close()}})().catch(e=>{console.error(e.message);process.exitCode=1});
