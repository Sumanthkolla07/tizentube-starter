const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../tizentube-handoff/source/index.html'), 'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
const flush = () => new Promise(resolve => setImmediate(resolve));
function deferred() { let resolve, reject; const promise = new Promise((yes, no) => {resolve=yes;reject=no}); return {promise,resolve,reject}; }
function boot(options={}) {
  let now=0, timerId=0, keydown; const timers=new Map(); const status={textContent:''};
  const state={health:!!options.health,starts:0,loads:0,launches:0,exits:0,last:null};
  const runtime={Service:class {start(){state.starts++;return options.start ? options.start(state) : Promise.resolve();}}};
  const context=vm.createContext({
    Date:{now:()=>now},AbortController,
    document:{getElementById:()=>status,body:{classList:{toggle(){}}},addEventListener:(name,fn)=>{keydown=fn}},
    localStorage:{setItem:(_,text)=>{state.last=JSON.parse(text)}},
    tizen:{application:{getCurrentApplication:()=>({appInfo:{packageId:'TTStartr01'},exit(){state.exits++}}),launch(app,success){state.launches++;if(!options.hangLaunch)success();}}},
    fetch:()=>state.health ? Promise.resolve({}) : Promise.reject(new Error('proxy closed')),
    setTimeout:(fn,delay)=>{const id=++timerId;timers.set(id,{due:now+delay,fn});return id},
    clearTimeout:id=>timers.delete(id),
    loadRuntime:()=>{state.loads++;return options.load ? options.load() : Promise.resolve(runtime)},
  });
  assert.equal(source.split('import("wrt:service")').length,2,'inject only the Tizen runtime boundary');
  vm.runInContext(source.replace('import("wrt:service")','loadRuntime()'),context);
  return {state,status,context,key(code){keydown({keyCode:code})},async advance(ms){
    await flush();const target=now+ms;
    while(true){
      const next=[...timers].filter(([,t])=>t.due<=target).sort((a,b)=>a[1].due-b[1].due)[0];
      if(!next)break;
      now=next[1].due;timers.delete(next[0]);next[1].fn();await flush();
    }
    now=target;await flush();
  }};
}
test('hung service start times out and OK permits retry',async()=>{
 const p=boot({start:()=>new Promise(()=>{})});await p.advance(30000);
 assert.equal(p.context.busy,false);assert.match(p.status.textContent,/timed out/i);assert.match(p.status.textContent,/OK/);
 p.key(13);await p.advance(0);assert.equal(p.state.starts,2);
});
test('hung runtime import also times out',async()=>{
 const p=boot({load:()=>new Promise(()=>{})});await p.advance(30000);
 assert.equal(p.context.busy,false);assert.match(p.status.textContent,/timed out/i);
});
test('late service completion cannot launch or overwrite a newer retry',async()=>{
 const old=deferred();const p=boot({start:state=>state.starts===1?old.promise:new Promise(()=>{})});
 await p.advance(30000);p.key(13);await p.advance(0);
 old.resolve();await p.advance(0);
 assert.equal(p.state.launches,0);assert.equal(p.context.busy,true);
 p.state.health=true;await p.advance(1000);
 assert.equal(p.state.launches,1);assert.equal(p.state.exits,1);
});
test('ready proxy opens Cobalt even when service start never settles',async()=>{
 const p=boot({start:state=>{state.health=true;return new Promise(()=>{})}});
 await p.advance(1000);
 assert.equal(p.state.starts,1);assert.equal(p.state.launches,1);assert.equal(p.state.exits,1);
});
test('ready proxy opens Cobalt despite a rejected service-start request',async()=>{
 const p=boot({start:state=>{state.health=true;return Promise.reject(new Error('API rejected'))}});
 await p.advance(1000);
 assert.equal(p.state.launches,1);assert.equal(p.state.exits,1);
});
test('existing proxy opens Cobalt without starting another service',async()=>{
 const p=boot({health:true});await p.advance(500);
 assert.equal(p.state.loads,0);assert.equal(p.state.launches,1);assert.equal(p.state.exits,1);
});
test('successful service start waits for readiness then opens and exits',async()=>{
 const p=boot({start:state=>{state.health=true;return Promise.resolve()}});await p.advance(1000);
 assert.equal(p.state.starts,1);assert.equal(p.state.launches,1);assert.equal(p.state.exits,1);
 await p.advance(30000);assert.equal(p.status.textContent,'');
});
test('proxy that never becomes ready reaches the overall deadline',async()=>{
 const p=boot();await p.advance(30000);
 assert.equal(p.state.launches,0);assert.equal(p.context.busy,false);assert.match(p.status.textContent,/timed out/i);
});
test('hung application launch callback reaches the overall deadline',async()=>{
 const p=boot({health:true,hangLaunch:true});await p.advance(30000);
 assert.equal(p.context.busy,false);assert.match(p.status.textContent,/timed out/i);
});
test('Back invalidates a pending attempt before late service completion',async()=>{
 const pending=deferred();const p=boot({start:()=>pending.promise});await p.advance(0);
 p.key(10009);p.state.health=true;pending.resolve();await p.advance(30000);
 assert.equal(p.state.exits,1);assert.equal(p.state.launches,0);assert.equal(p.status.textContent,'');
});
