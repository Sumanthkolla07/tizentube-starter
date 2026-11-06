const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const bundle = fs.readFileSync(path.join(__dirname, '../tizentube-handoff/source/service/dist/index.js'), 'utf8');
const from = bundle.indexOf('var fs = __nccwpck_require__(9896);', bundle.indexOf('/***/ 6496:'));
const to = bundle.indexOf('module.exports = startServer;', from) + 'module.exports = startServer;'.length;
function boot(debug=false) {
  let handler; const writes=[]; const reads=[];
  const server={on(){return this},listen(){}};
  const fakeFS={existsSync(){return false},appendFileSync(...args){writes.push(args)},readFileSync(f){reads.push(f);return 'historical viewing log'},statSync(){return {size:0}}};
  const deps={9896:fakeFS,8611:{createServer(fn){handler=fn;return server}},5692:{},3179:{},9278:{},4756:{},2261:{},7016:require('node:url')};
  const context={module:{exports:{}},__nccwpck_require__(id){assert.ok(id in deps);return deps[id]},require(){return {}},process:{env:{TIZENTUBE_DIAGNOSTICS:debug?'1':'0'},on(){},once(){},version:'test',pid:1},setInterval(){return {unref(){}}},setTimeout(){},Date,console};
  vm.runInNewContext(bundle.slice(from,to),context);context.module.exports();
  return {writes,reads,request(url,remoteAddress='192.0.2.1'){
    let status;let body;const response={writeHead(s){status=s},end(b){body=b}};
    handler({url,method:'GET',socket:{remoteAddress}},response);return {status,body};
  }};
}
test('health returns no viewing data with logging disabled',()=>{
 const p=boot();assert.deepEqual(p.request('/__tthealth'),{status:200,body:'ok\n'});assert.equal(p.writes.length,0);assert.equal(p.reads.length,0);
});
test('disabled diagnostics cannot read or clear historical logs',()=>{
 const p=boot();assert.equal(p.request('/__ttlog?clear=1').status,404);assert.equal(p.reads.length,0);assert.equal(p.writes.length,0);
});
test('opt-in diagnostics still reject remote LAN readers',()=>{
 const p=boot(true);assert.equal(p.request('/__ttlog').status,404);assert.equal(p.reads.length,0);assert.ok(p.writes.length>0);
});
test('opt-in diagnostics deny loopback HTTP access, including proxy-relayed clients',()=>{
 const p=boot(true);assert.equal(p.request('/__ttlog','127.0.0.2').status,404);assert.equal(p.reads.length,0);
});
