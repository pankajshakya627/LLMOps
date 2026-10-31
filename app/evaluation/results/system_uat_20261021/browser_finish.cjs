const {chromium}=require('/private/tmp/nexaassist-uat-browser/node_modules/playwright');
const fs=require('node:fs');const path=require('node:path');
const out=path.resolve('app/evaluation/results/system_uat_20261021');
const own=JSON.parse(fs.readFileSync(path.join(out,'browser_feedback_record.json')));
const marker=own.correction.split(' ')[0];const results=[];
const check=(name,ok,detail)=>{results.push({name,result:ok?'pass':'fail',detail});fs.writeFileSync(path.join(out,'browser_finish.json'),JSON.stringify(results,null,2));console.log(JSON.stringify(results.at(-1)));};
(async()=>{const browser=await chromium.launch({channel:'chrome',headless:true});let page;
try{
 const ctx=await browser.newContext({viewport:{width:1440,height:1000}});page=await ctx.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8501');await page.getByPlaceholder('Ask NexaAssist about a policy…').waitFor({timeout:30000});
 await page.getByText('Review feedback',{exact:true}).click();await page.getByRole('button',{name:'Load feedback for review'}).click();
 const record=page.getByTestId('stExpander').filter({hasText:marker});await record.locator('summary').click();
 if(await record.getByRole('textbox',{name:'Reviewer name'}).count()){
 await record.getByRole('textbox',{name:'Reviewer name'}).fill('System UAT (synthetic)');
 await record.getByRole('textbox',{name:'Review note'}).fill(marker+' Synthetic test only; not a customer correction.');
 const decision=record.getByRole('combobox');await decision.focus();await decision.press('ArrowDown');await decision.press('End');await decision.press('Enter');
 await record.getByRole('button',{name:'Save review'}).click();
 await record.getByText(/Reviewed by System UAT/).waitFor({state:'attached',timeout:30000});
 }
 if(!(await record.getByText(/Reviewed by System UAT/).isVisible()))await record.locator('summary').click();
 const reviewed=(await(await fetch('http://127.0.0.1:8000/feedback?limit=20')).json()).find(r=>r.feedback_id===own.feedback_id);
 check('browser_review_saved',reviewed?.status==='rejected',{feedback_id:own.feedback_id});
 await record.screenshot({path:path.join(out,'browser_feedback_review.png')});
 check('browser_no_unhandled_js_errors',errors.length===0,{errors});
 const mobile=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const mp=await mobile.newPage();
 await mp.goto('http://127.0.0.1:8501');await mp.getByPlaceholder('Ask NexaAssist about a policy…').waitFor({timeout:30000});
 const widths=await mp.locator('body').evaluate(body=>({scroll:body.scrollWidth,width:body.clientWidth}));
 check('mobile_no_horizontal_overflow',widths.scroll<=widths.width+1,widths);
 await mp.screenshot({path:path.join(out,'browser_mobile.png'),fullPage:true});
 await mobile.close();await ctx.close();
}catch(e){check('browser_finish',false,{error:e.message});if(page){fs.writeFileSync(path.join(out,'browser_finish_failure.txt'),await page.locator('body').innerText());await page.screenshot({path:path.join(out,'browser_finish_failure.png'),fullPage:true});}throw e;}
finally{await browser.close();}})().catch(e=>{console.error(e.message);process.exitCode=1});
