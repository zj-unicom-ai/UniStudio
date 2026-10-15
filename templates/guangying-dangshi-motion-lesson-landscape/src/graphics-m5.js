/* M5 event-led Canvas animation. Every scene is seekable from composition time. */
(function(){
'use strict';
const W=1920,H=1080, C={ink:'#191617',ink2:'#2A2221',red:'#842D34',red2:'#A94542',gold:'#C5A677',paper:'#E9DFCA',pale:'#F2EBDD',dim:'#A99C8C',white:'#F8F2E7',line:'#705B50'};
const g=document.getElementById('sceneCanvas').getContext('2d',{alpha:false});
const data=window.EP01_M5, SHOTS=data.shots, CHAPS=data.chapters, TOTAL=data.duration_seconds;
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
const ease=x=>{x=clamp(x);return x*x*(3-2*x)};
const out=x=>1-Math.pow(1-clamp(x),3);
const serif="'Noto Serif CJK SC','Songti SC','STSong',serif", sans="'GuangyingSans','PingFang SC',sans-serif";
function txt(s,x,y,size,color=C.white,align='left',weight='500',family=sans,alpha=1){g.save();g.globalAlpha=alpha;g.fillStyle=color;g.font=`${weight} ${size}px ${family}`;g.textAlign=align;g.textBaseline='alphabetic';g.fillText(String(s),x,y);g.restore()}
function fit(s,x,y,size,max,color=C.white,align='left',weight='500',family=sans){g.save();g.font=`${weight} ${size}px ${family}`;while(g.measureText(String(s)).width>max&&size>18){size-=2;g.font=`${weight} ${size}px ${family}`}g.restore();txt(s,x,y,size,color,align,weight,family)}
function box(x,y,w,h,fill,stroke=null,r=8,lw=2){g.save();g.beginPath();g.roundRect(x,y,w,h,r);if(fill){g.fillStyle=fill;g.fill()}if(stroke){g.strokeStyle=stroke;g.lineWidth=lw;g.stroke()}g.restore()}
function rect(x,y,w,h,c){g.fillStyle=c;g.fillRect(x,y,w,h)}
function circ(x,y,r,c,stroke=null,lw=2){g.save();g.beginPath();g.arc(x,y,r,0,Math.PI*2);if(c){g.fillStyle=c;g.fill()}if(stroke){g.strokeStyle=stroke;g.lineWidth=lw;g.stroke()}g.restore()}
function seg(x1,y1,x2,y2,p=1,c=C.gold,w=4,dash=[]){p=clamp(p);g.save();g.strokeStyle=c;g.lineWidth=w;g.lineCap='round';g.setLineDash(dash);g.beginPath();g.moveTo(x1,y1);g.lineTo(x1+(x2-x1)*p,y1+(y2-y1)*p);g.stroke();g.restore()}
function path(pts,p=1,c=C.gold,w=5,dash=[]){let lens=[],all=0;for(let i=1;i<pts.length;i++){let n=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);lens.push(n);all+=n}let left=all*clamp(p);g.save();g.strokeStyle=c;g.lineWidth=w;g.lineCap='round';g.lineJoin='round';g.setLineDash(dash);g.beginPath();g.moveTo(...pts[0]);for(let i=1;i<pts.length;i++){let u=lens[i-1]?Math.min(1,left/lens[i-1]):1;g.lineTo(pts[i-1][0]+(pts[i][0]-pts[i-1][0])*u,pts[i-1][1]+(pts[i][1]-pts[i-1][1])*u);left-=lens[i-1];if(u<1)break}g.stroke();g.restore()}
function dot(x,y,r,c=C.red2){circ(x,y,r,c)}
function labelPill(s,x,y,w=240){box(x,y,w,42,'rgba(25,22,23,.88)',C.gold,20,1);fit(s,x+w/2,y+29,20,w-22,C.pale,'center')}
function card(x,y,w,h,title,body,idx=0,light=true){const bg=light?C.pale:'#302526',fg=light?C.ink:C.white,ac=idx%2?C.gold:C.red2;box(x,y,w,h,bg,light?'#C8B99F':'#5D4542',5,2);rect(x,y,8,h,ac);txt(title,x+30,y+47,26,ac,'left','700');fit(body,x+30,y+91,31,w-56,fg,'left','500',serif)}
function titleScene(title,sub='',light=false,kind=''){
 let fg=light?C.ink:C.white;
 const big=new Set(['newspaper_wall','city_panorama','mountain_relief','meeting_room']);
 const left=new Set(['press_room','shikumen_street','mountain_route','document_page','archive_table','contour_map']);
 if(big.has(kind))fit(title,160,300,64,1550,fg,'left','700',serif);
 else if(left.has(kind))fit(title,150,282,46,1200,fg,'left','700',serif);
 else fit(title,150,282,54,1620,fg,'left','700',serif);
 if(sub)fit(sub,154,328,24,1590,light?'#665A4E':C.dim)
}
function reveal(p,i,n=4){return ease((p-i*.13)/(1-(n-1)*.13))}
function background(kind,t){
 const lightKinds=new Set(['fact_layers','source_margin','document_blocks','decision_stack','memory_boundary','delegate_scale','date_cards','meeting_table','three_problems','practice_table','fact_scope','restraint_card','source_frame','diagram_key','method_marks','document_page','archive_table','archive_page','minute_sheet','policy_columns']);
 const redKinds=new Set(['fracture_line','pressure_field','narrowing_ribbon','pressure_meter','problem_marks','choice_fork']);
 const mapKinds=new Set(['mountain_relief','mountain_route','contour_map','rural_layers']);
 const streetKinds=new Set(['shikumen_street','city_panorama','press_room','newspaper_wall']);
 const waterKinds=new Set(['boat_silhouette','river_marker']);
 const light=lightKinds.has(kind), red=redKinds.has(kind), map=mapKinds.has(kind), street=streetKinds.has(kind), water=waterKinds.has(kind);
 const base=light?C.paper:(red?'#402527':map?'#192B29':water?'#17282D':street?'#252426':C.ink);
 rect(0,0,W,H,base);
 if(!light&&!red){let center=map?'#30433B':water?'#2C4448':street?'#3A302D':'#38282A';let gr=g.createRadialGradient(1210+Math.sin(t*.09)*90,410,40,1080,510,1100);gr.addColorStop(0,center);gr.addColorStop(.66,map?'#22332F':water?'#20343A':street?'#2B2929':'#251D1E');gr.addColorStop(1,base);g.fillStyle=gr;g.fillRect(0,0,W,H)}
 g.save();g.globalAlpha=light?.11:.08;g.strokeStyle=light?C.red:map?'#9BAA8A':water?'#72939A':street?'#C5A677':C.gold;g.lineWidth=1;
 if(map){for(let i=0;i<8;i++){g.beginPath();for(let x=150;x<=1770;x+=22){let y=330+i*62+Math.sin(x*.006+i*1.3)*28+Math.cos(x*.003+i*.6)*18;if(x===150)g.moveTo(x,y);else g.lineTo(x,y)}g.stroke()}}
 else if(street){for(let i=0;i<9;i++){let y=310+i*58;g.beginPath();g.moveTo(80,y);g.lineTo(1840,y);g.stroke()}for(let i=0;i<12;i++){let x=120+i*150;g.beginPath();g.moveTo(x,270);g.lineTo(x,825);g.stroke()}}
 else if(water){for(let i=0;i<9;i++){let y=320+i*68;g.beginPath();for(let x=80;x<=1840;x+=26){let yy=y+Math.sin(x*.008+i)*16;if(x===80)g.moveTo(x,yy);else g.lineTo(x,yy)}g.stroke()}}
 else{for(let i=0;i<11;i++){let x=(i*191+53)%W;g.beginPath();g.moveTo(x,150);g.lineTo(x-120,840);g.stroke()}}
 g.restore();
 return light;
}
function shell(ch,shot,t,light){
 let fg=light?C.ink:C.white,muted=light?'#776B5F':C.dim,n=+ch.id.slice(1);
 rect(0,0,12,H,C.red);rect(108,104,52,5,C.red2);txt('光 影 党 史   /   DOCUMENTARY',178,113,20,C.gold,'left','500');
 fit(ch.title,108,190,34,1300,fg,'left','700',serif);txt(`${String(n).padStart(2,'0')} / 09`,1810,111,22,muted,'right','500');
 seg(108,218,1812,218,1,light?'#B9AA92':'#665149',1);
 rect(108,990,1704,2,light?'#B9AA92':'#665149');rect(108,990,1704*clamp(t/TOTAL),4,C.gold);
 txt(fmt(t),108,1034,21,muted,'left','500');txt(fmt(TOTAL),1812,1034,21,muted,'right','500');
 return {fg,muted};
}
function fmt(t){let m=Math.floor(t/60),s=Math.floor(t%60);return String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')}
function findShot(t){let lo=0,hi=SHOTS.length-1;while(lo<hi){let mid=(lo+hi)>>1;if(SHOTS[mid].end<=t)lo=mid+1;else hi=mid}return SHOTS[lo]}
function content(kind,label,p,t,ch,light){let fg=light?C.ink:C.white,muted=light?'#776B5F':C.dim;titleScene(label,'',light,kind);
 const a=out(p), pulse=.5+.5*Math.sin(t*.42), years=['1921','1927','1929','1935'];
 switch(kind){
 case 'newspaper_wall':{
  const x0=210,y0=382,w=1500,h=432;box(x0,y0,w,h,'#E7DDC9','#B4A48D',2,2);rect(x0+22,y0+22,w-44,4,C.red);txt('时 代 现 场',x0+38,y0+76,23,C.red,'left','700',serif);txt('社会 · 思想 · 组织',x0+w-38,y0+76,19,'#6F655A','right');
  const cols=5,cw=260,gap=25;for(let c=0;c<cols;c++){let x=x0+38+c*(cw+gap),top=y0+112;for(let r=0;r<8;r++){let len=cw*(.48+((r*7+c*3)%5)*.095);rect(x,top+r*27,len,r===0&&c===0?9:4,r===0&&c===0?C.red:'#A89A85')}if(c===2){box(x-4,top+75,cw+8,108,'#D7CCB8','#B7A68D',2,1);txt('时代议题',x+cw/2,top+137,25,C.ink,'center','600',serif)}}
  txt('历史背景 · 报纸版式为艺术化示意',960,858,20,muted,'center');break}
 case 'shikumen_street':{
  rect(120,275,380,620,'#332725');rect(1420,275,380,620,'#3A2C29');
  for(let side=0;side<2;side++){let x=side?1460:155;for(let row=0;row<3;row++){let y=340+row*170;for(let col=0;col<2;col++){let wx=x+col*175+row*14;box(wx,y,128,112,'#252020','#A88A68',2,3);seg(wx+64,y,wx+64,y+112,1,'#8C7258',2);seg(wx,y+56,wx+128,y+56,1,'#8C7258',2)}}}
  path([[500,895],[960,545],[1420,895]],1,'#8B6C50',4);path([[500,895],[960,545],[1420,895]],1,'#3C302D',2);for(let i=0;i<5;i++){let y=610+i*50;seg(740-i*37,y,1180+i*37,y,1,'rgba(197,166,119,.35)',2)}
  box(790,400,340,250,'#201B1A','#C5A677',3,4);txt('上海 · 石库门',960,690,31,C.pale,'center','600',serif);txt('城市街巷示意 · 非历史照片',960,840,20,muted,'center');break}
 case 'press_room':{
  const x=330,y=395,w=1260,h=340;box(x,y,w,h,'#DCCFB9','#9D8B72',8,3);rect(x+22,y+22,w-44,36,C.red);txt('排字 · 印刷 · 传播',x+w/2,y+48,23,C.white,'center','600',serif);
  for(let i=0;i<5;i++){let bx=x+55+i*230;box(bx,y+93,185,185,'#EEE5D5','#B7A68D',2,2);for(let r=0;r<6;r++){let yy=y+116+r*24;seg(bx+15,yy,bx+165-(r%3)*18,yy,1,'#847767',2)}if(i===2)rect(bx+20,y+231,144,27,C.red2)}
  circ(675,810,54,'#2B2524',C.gold,3);circ(1245,810,54,'#2B2524',C.gold,3);seg(675,810,1245,810,a,C.gold,8);txt('传播链路示意',960,874,22,muted,'center');break}
 case 'city_panorama':{
  const base=815,blocks=[[220,610,190,205],[430,520,230,295],[685,585,210,230],[935,470,225,345],[1190,545,210,270],[1430,420,270,395]];
  blocks.forEach((b,i)=>{let [x,y,w,h]=b;rect(x,y,w,h,i%2?'#332B29':'#40302C');rect(x,y,w,8,C.gold);for(let r=0;r<Math.floor(h/48);r++)for(let c=0;c<Math.floor(w/42);c++){let wx=x+17+c*42,wy=y+27+r*48;box(wx,wy,22,29,'#8A6D50',null,2)}});
  seg(130,base,1785,base,1,C.gold,3);for(let i=0;i<6;i++)circ(360+i*240,base+18,4,C.gold);txt('城市与社会环境 · 构成示意',960,880,21,muted,'center');break}
 case 'meeting_room':{
  const grad=g.createRadialGradient(960,390,20,960,570,700);grad.addColorStop(0,'rgba(197,166,119,.20)');grad.addColorStop(1,'rgba(197,166,119,0)');g.fillStyle=grad;g.fillRect(220,230,1480,640);
  path([[370,750],[600,490],[1320,490],[1550,750],[960,880],[370,750]],1,'#5A463A',4);box(600,500,720,250,'#3C302B','#C5A677',10,4);box(825,525,270,118,'#E9DFCA','#A78E6D',4,2);txt('议事空间',960,594,27,C.ink,'center','700',serif);txt('会议场景为艺术化空间示意',960,842,21,muted,'center');
  for(let i=0;i<6;i++){let x=480+i*192;box(x,430,112,54,'#282221','#9B7D5A',8,2);box(x,756,112,55,'#282221','#9B7D5A',8,2)}seg(510,376,1410,376,a,C.gold,2);circ(960,380,9,C.gold);break}
 case 'document_page':{
  const x=535,y=360,w=850,h=500;box(x,y,w,h,'#EDE3D1','#A69477',3,3);rect(x+42,y+38,w-84,3,'#C4B398');rect(x+42,y+74,170,8,C.red);txt('会议记录 · 结构示意',x+42,y+127,31,C.red,'left','700',serif);
  const labels=['议题与形势','组织安排','决议起草','后续执行'];labels.forEach((s,i)=>{let yy=y+190+i*67;circ(x+65,yy-8,6,C.red);txt(s,x+91,yy,24,C.ink,'left','600');seg(x+310,yy-9,x+w-52,yy-9,1,'#B5A58E',2);if(i===2)rect(x+310,yy+8,355,4,'#D1C3AD')});
  box(1450,425,230,190,'#322927',C.gold,4,3);txt('材料边界',1565,482,25,C.gold,'center','600');txt('史实',1565,536,30,C.white,'center','700',serif);txt('与归纳分列',1565,575,21,C.pale,'center');txt('档案样式为示意，不是原件复刻',960,892,20,muted,'center');break}
 case 'archive_page':{
  const x=550,y=360,w=820,h=505;box(x,y,w,h,'#E9DFC9','#A99578',2,3);rect(x+55,y+50,7,h-100,C.red);txt('资料摘录',x+96,y+104,27,C.red,'left','700',serif);txt('日期 / 口径 / 形成过程',x+96,y+144,20,'#706352','left','500');
  for(let i=0;i<8;i++){let yy=y+198+i*37,len=430+(i%4)*55;seg(x+98,yy,x+98+len,yy,1,'#A99B83',2)}
  box(x+575,y+78,150,126,'#D3C4AA','#B19C7D',2,2);txt('R',x+650,y+159,66,C.red,'center','700',serif);txt('出处核对',x+650,y+237,19,'#6A5F51','center');txt('版式为讲解示意，不是原档案影印',960,902,20,muted,'center');break}
 case 'archive_table':{
  const x=340,y=390,w=1240,h=388;box(x,y,w,h,'#E8DECA','#B09D80',3,2);rect(x,y,w,62,'#5B302E');txt('史实边界核对',x+34,y+41,28,C.white,'left','700',serif);
  const cols=[340,720,1100,1580];for(let i=1;i<4;i++)seg(cols[i],y+63,cols[i],y+h,1,'#B9A98F',2);['事件节点','可确认内容','分析表达'].forEach((s,i)=>txt(s,cols[i]+26,y+105,22,C.red,'left','700'));for(let r=0;r<3;r++){let yy=y+152+r*72;seg(x+20,yy+18,x+w-20,yy+18,1,'#C7B99F',1);for(let c=0;c<3;c++){let ww=[300,300,360][c],xx=cols[c]+24;rect(xx,yy-10,ww*(.72+((r+c)%3)*.08),6,'#9D907D')}}txt('对照表为讲解结构，不代表原始档案格式',960,840,20,muted,'center');break}
 case 'mountain_relief':case 'contour_map':{
  const layers=[['#263A35',760],['#31473D',670],['#3A5043',590],['#475746',515]];layers.forEach((layer,i)=>{let [col,base]=layer;g.beginPath();g.moveTo(0,H);g.lineTo(0,base);for(let x=0;x<=W;x+=45){let y=base+Math.sin(x*.004+i*1.1)*45+Math.sin(x*.011+i*.8)*22;g.lineTo(x,y)}g.lineTo(W,H);g.closePath();g.fillStyle=col;g.fill()});
  for(let i=0;i<5;i++){g.save();g.globalAlpha=.28;g.beginPath();for(let x=120;x<=1800;x+=28){let y=405+i*48+Math.sin(x*.006+i)*19;if(x===120)g.moveTo(x,y);else g.lineTo(x,y)}g.strokeStyle=C.pale;g.lineWidth=2;g.stroke();g.restore()}txt('山地环境 · 路线为结构示意',960,870,22,C.pale,'center');break}
 case 'mountain_route':{
  const pts=[[215,770],[410,650],[575,695],[760,500],[970,570],[1145,390],[1355,500],[1550,350],[1745,430]];path(pts,a,'#D4B57F',10);pts.forEach((pt,i)=>{circ(pt[0],pt[1],i%2?12:17,i===0||i===pts.length-1?C.red2:C.pale,C.gold,2);if(i===0||i===4||i===8)txt(i===0?'出发':i===4?'转折':'继续前行',pt[0],pt[1]-34,22,C.white,'center','600')});txt('路径为讲解示意 · 非精确行军图',960,824,20,C.dim,'center');break}
 case 'field_camp':{
  rect(0,780,W,300,'#192522');for(let i=0;i<7;i++){let x=120+i*285,h=120+(i%3)*42;path([[x,780],[x+90,780-h],[x+185,780]],1,i%2?'#415447':'#34483E',4)}
  box(675,514,570,240,'#2A302B','#C5A677',4,3);path([[635,515],[960,365],[1285,515]],1,'#9D7852',6);for(let i=0;i<3;i++){let x=755+i*205;box(x,565,120,136,'#202522','#A88C66',3,2);seg(x+60,565,x+60,700,1,'#927656',2)}txt('基层工作场景 · 艺术化示意',960,866,22,C.pale,'center');break}
 case 'boat_silhouette':{
  const horizon=650;rect(0,horizon,W,430,'#183038');seg(0,horizon,W,horizon,1,'#8AA0A0',2);for(let i=0;i<7;i++){let y=horizon+35+i*42;seg(160+i*45,y,1760-i*25,y,1,'rgba(138,160,160,.38)',2)}
  path([[600,560],[1320,560],[1230,655],[700,655],[600,560]],1,'#171B1D',5);path([[720,557],[800,470],[1110,470],[1200,557]],1,'#282322',4);rect(838,500,228,55,'#2B2522');for(let i=0;i<3;i++)box(860+i*70,512,44,30,'#D5C7A8',null,2);seg(960,450,960,352,1,C.gold,3);path([[960,355],[1115,430],[960,430]],1,'#842D34',3);txt('红船意象 · 当代纪念象征',960,810,29,C.pale,'center','600',serif);txt('艺术化场景，不是历史影像',960,860,19,C.dim,'center');break}
 case 'river_marker':{
  g.save();g.globalAlpha=.45;for(let i=0;i<9;i++){let y=370+i*58;g.beginPath();g.moveTo(120,y);for(let x=120;x<=1800;x+=24)g.lineTo(x,y+Math.sin(x*.009+i)*25);g.strokeStyle='#89A2A1';g.lineWidth=3;g.stroke()}g.restore();
  path([[350,700],[520,610],[690,660],[850,520],[1010,580],[1180,450],[1360,520],[1540,390]],a,C.gold,8);[['上海',350,700],['嘉兴',850,520],['南湖',1540,390]].forEach(([s,x,y],i)=>{circ(x,y,16,i===2?C.red2:C.pale,C.gold,2);txt(s,x,y-34,25,C.white,'center','600')});txt('会址转移关系示意 · 不按地理比例',960,850,20,C.dim,'center');break}
 case 'minute_sheet':{
  box(480,350,960,525,'#E9DFC9','#A99679',3,3);rect(535,410,850,3,'#C4B398');txt('会议议程与决定',535,470,32,C.red,'left','700',serif);let rows=[['组织安排','讨论与会代表、中央机构'],['纲领文件','形成共同的政治主张'],['会后工作','把决定带入实际行动']];rows.forEach((r,i)=>{let y=535+i*92,q=reveal(p,i,3);txt(String(i+1).padStart(2,'0'),555,y,23,C.red,'left','700',serif);fit(r[0],635,y,27,200,C.ink,'left','700');fit(r[1],895,y,23,450,C.ink,'left','500');seg(555,y+28,1360,y+28,q,'#B8A88F',2)});txt('内容按旁白归纳 · 版式为讲解示意',960,908,19,muted,'center');break}
 case 'policy_columns':{
  const labels=['理论教育','组织生活','政治工作'];labels.forEach((s,i)=>{let x=350+i*450,y=400,w=330,h=390,q=reveal(p,i,3);box(x,y,w,h,'#EFE6D4','#B4A287',3,2);rect(x,y,w,18,i===1?C.red:C.gold);txt(['Ⅰ','Ⅱ','Ⅲ'][i],x+w/2,y+105,54,C.red,'center','700',serif);fit(s,x+w/2,y+177,30,280,C.ink,'center','700');for(let k=0;k<4;k++)seg(x+55,y+240+k*32,x+w-48-((k+i)%3)*28,y+240+k*32,q,'#9F927E',2)});txt('把原则落实到日常组织工作',960,865,24,muted,'center');break}
 case 'people_network':{
  const clusters=[{x:470,y:590,n:5,label:'成员联系'},{x:960,y:430,n:6,label:'组织协作'},{x:1450,y:610,n:5,label:'行动反馈'}];path([[520,590],[750,500],[960,430],[1185,505],[1420,610]],a,C.gold,4);
  clusters.forEach((cl,ci)=>{for(let i=0;i<cl.n;i++){let an=i*2*Math.PI/cl.n-Math.PI/2,x=cl.x+Math.cos(an)*115,y=cl.y+Math.sin(an)*85;seg(cl.x,cl.y,x,y,reveal(p,i,cl.n),'#9E8D6A',2);circ(x,y,18,C.ink2,C.gold,2);circ(x,y-4,5,C.pale);path([[x-8,y+12],[x,y+5],[x+8,y+12]],1,C.pale,2)}circ(cl.x,cl.y,48,ci===1?C.red:'#29322E',C.gold,3);fit(cl.label,cl.x,cl.y+115,22,220,C.white,'center','600')});txt('组织联系与群体协作关系示意',960,860,21,muted,'center');break}
 case 'decision_tilt':{
  path([[300,790],[690,650],[1030,570],[1610,340]],a,C.gold,6);path([[300,830],[650,690],[1010,610],[1590,380]],a,C.red2,3);
  const labels=['战局压力','调整重点','继续行动'];[[490,710],[930,610],[1390,430]].forEach(([x,y],i)=>{g.save();g.translate(x,y);g.rotate(-.27);box(-175,-58,350,116,i===1?C.red:'#332827',C.gold,4,2);fit(labels[i],0,10,28,310,C.white,'center','600',serif);g.restore()});txt('判断随着现实条件变化而调整',960,850,23,muted,'center');break}
 case 'year_gate':case 'year_return':case 'date_return':case 'four_orbits':{
  const xs=kind==='four_orbits'?[340,760,1160,1580]:[270,730,1190,1640], ys=kind==='four_orbits'?[510,390,580,430]:[510,450,570,480];
  if(kind==='four_orbits'){circ(960,530,195,null,C.line,2);circ(960,530,286,null,C.line,2);txt('问题如何',960,510,35,C.gold,'center','700',serif);txt('彼此相连',960,555,35,C.gold,'center','700',serif);}
  for(let i=0;i<4;i++){let q=reveal(p,i,4);let dx=i<3?xs[i+1]:0,dy=i<3?ys[i+1]:0;if(i<3)seg(xs[i]+75,ys[i]+5,dx-75,dy+5,reveal(p,i,4),C.gold,4);circ(xs[i],ys[i],76*q,kind==='year_return'?C.red:C.ink2,C.gold,2);txt(years[i],xs[i],ys[i]+17,43,C.pale,'center','700',serif);if(kind!=='four_orbits')txt(['建立组织','寻找道路','建设队伍','危机调整'][i],xs[i],ys[i]+113,22,muted,'center')}
  break}
 case 'stone_window':case 'shikumen_frame':case 'context_window':{
  let x=790,y=420,w=340,h=340;box(x-100,y-48,w+200,h+48,null,C.gold,0,4);box(x-44,y+4,w+88,h-4,null,C.gold,150,3);box(x,y+76,w,h-76,'#38292A',C.gold,6,3);seg(960,y+76,960,y+h,1,C.gold,2);circ(1083,y+248,7,C.gold);txt('上海',960,330,26,C.gold,'center');txt(kind==='context_window'?'时代环境':(ch.id==='S04'?'1921 · 会场':'历史条件'),960,812,24,muted,'center');break}
 case 'bridge_path':case 'choice_fork':case 'open_paths':case 'many_paths':case 'opening_path':{
  let y=620,cx=960;seg(200,y,cx-30,y,1,C.gold,8);let branches=kind==='choice_fork'||kind==='many_paths'||kind==='open_paths'?4:3;
  for(let i=0;i<branches;i++){let yy=360+i*128;path([[cx-30,y],[cx+80,y],[cx+180,yy],[1550,yy]],reveal(p,i,branches),i===0?C.red2:C.gold,i===0?8:4,i===0?[]:[9,10]);circ(1550,yy,9,C.red2);txt((['继续探索','组织调整','道路选择','实践检验'][i]),1600,yy+8,24,fg,'left')}
  circ(200,y,18,C.gold);break}
 case 'question_field':case 'open_question':case 'question_lens':{
  const rings=[140,245,350];rings.forEach((r,i)=>circ(960,570,r*reveal(p,i,3),null,i===1?C.red2:C.gold,i===1?5:2));txt(kind==='question_lens'?'当时的人看见什么？':'怎样把理想变成持续行动？',960,580,49,fg,'center','700',serif);['时代条件','组织联系','实践结果'].forEach((s,i)=>txt(s,960+Math.cos(-2.4+i*1.7)*290,570+Math.sin(-2.4+i*1.7)*290,23,C.gold,'center'));break}
 case 'fact_layers':case 'social_layers':case 'rural_layers':case 'education_layers':case 'context_stack':{
  let names=kind==='social_layers'?['社会秩序','知识与思想','工人运动','早期组织']:kind==='rural_layers'?['地理环境','地方社会','群众工作','根据地建设']:kind==='education_layers'?['思想教育','组织建设','政治工作']:kind==='context_stack'?['时代背景','组织问题','具体行动']:['可核对的事实','本片的归纳','结构示意'];
  if(kind==='rural_layers'){names.forEach((s,i)=>{let y=450+i*88,q=reveal(p,i,names.length),w=390+i*155;path([[250,850-i*84],[960-w/2,550+i*18],[960+w/2,550+i*18],[1670,850-i*84]],1,i===0?'#43594B':'#657260',3);box(960-w/2,500+i*22,w*q,48,i===0?C.red:'#293A32',C.gold,18,2);fit(s,960,532+i*22,22,w-28,C.white,'center','600')})}
  else if(kind==='education_layers'){names.forEach((s,i)=>{let x=520+i*440,h=230+i*48,y=785-h,q=reveal(p,i,names.length);rect(x,785-h*q,190,h*q,i===0?C.red:'#665344');rect(x,785-h*q,190,10,C.gold);fit(s,x+95,748-h*q,24,170,C.white,'center','600');for(let r=0;r<3;r++)rect(x+28+r*48,785-h*q+34,16,Math.max(0,h*q-58),'rgba(242,235,221,.35)')})}
  else if(kind==='social_layers'){names.forEach((s,i)=>{let x=310+i*438,y=490+(i%2)*150,q=reveal(p,i,names.length);circ(x,y,82*q,i===3?C.red:'#312726',C.gold,3);fit(s,x,y+130,24,210,fg,'center','600');if(i<3)seg(x+90,y,x+348,y+(i%2?150:-150),q,C.gold,3)})}
  else{names.forEach((s,i)=>{let y=390+i*94,w=420+i*165;let q=reveal(p,i,names.length);box(960-w/2,y,w*q,58,i===0?C.red:(light?C.pale:'#332829'),i===0?null:(light?'#BBAA91':'#5B4640'),4,2);fit(s,960,y+39,25,w-36,i===0?C.white:fg,'center','600')})}
  break}
 case 'diagram_key':case 'method_marks':{
  const rows=[['实线节点','史实日期或地点'],['细线归纳','本片解释关系'],['虚线路径','结构示意，不按比例'],['空白位置','没有可核验数字']];
  rows.forEach((r,i)=>{let y=405+i*98,q=reveal(p,i,4);if(i===2)seg(340,y,650,y,q,C.gold,4,[10,10]);else if(i===3)circ(495,y,12,null,C.red2,3);else seg(340,y,650,y,q,i===0?C.red2:C.gold,i===0?8:3);fit(r[0],720,y+8,27,260,fg,'left','700');fit(r[1],1040,y+8,25,560,muted,'left','500')});txt('图例说明表达方式，避免把示意当作原始材料',960,850,22,muted,'center');break}
 case 'society_wheel':case 'context_zoom':{
  const rr=[88,168,260,350];rr.forEach((r,i)=>circ(960,600,r*reveal(p,i,4),null,i===2?C.red2:C.gold,i===2?5:2));
  const names=kind==='society_wheel'?['国家处境','社会生活','思想传播','组织实践']:['时代','运动','城市组织','全国会议'];names.forEach((s,i)=>{let an=-Math.PI/2+i*Math.PI/2,x=960+Math.cos(an)*315,y=600+Math.sin(an)*280;fit(s,x,y,24,180,fg,'center','600')});txt(kind==='society_wheel'?'从社会环境逐层看见组织问题':'从时代背景收束到 1921 年',960,600,31,C.gold,'center','700',serif);break}
 case 'reform_fan':case 'public_square':case 'city_links':case 'village_links':case 'relay_map':case 'labor_network':case 'organization_nodes':case 'central_bureau':{
  let nodes=kind==='reform_fan'?[[960,425,'制度改革'],[610,610,'技术自强'],[1310,610,'共和探索'],[960,740,'现实问题']]:kind==='public_square'?[[620,480,'学生'],[960,430,'公共议题'],[1300,480,'工人'],[960,700,'社会响应']]:kind==='city_links'?[[480,440,'上海'],[850,350,'北京'],[1190,480,'武汉'],[780,680,'长沙'],[1390,720,'济南']]:kind==='village_links'?[[560,480,'队伍'],[960,400,'组织联系'],[1350,470,'地方社会'],[960,700,'行动条件']]:kind==='central_bureau'?[[960,390,'中央局'],[600,610,'组织联系'],[960,680,'共同方向'],[1320,610,'各地工作']]:kind==='relay_map'?[[420,620,'传播'],[780,450,'交流'],[1140,620,'联络'],[1500,450,'组织']]:[[500,600,'组织'],[850,420,'教育'],[1160,620,'行动'],[1470,440,'反馈']];
  let cx=960,cy=570;
  if(kind==='city_links'||kind==='relay_map'){for(let i=0;i<nodes.length-1;i++)seg(nodes[i][0],nodes[i][1],nodes[i+1][0],nodes[i+1][1],reveal(p,i,nodes.length-1),kind==='relay_map'?C.red2:C.gold,kind==='relay_map'?7:3,kind==='relay_map'?[]:[8,9])}
  else if(kind==='central_bureau'){let root=nodes[0];nodes.slice(1).forEach((n,i)=>{seg(root[0],root[1]+45,n[0],n[1]-38,reveal(p,i,3),C.gold,3);if(i>0)seg(n[0],n[1]+40,500+i*260,780,reveal(p,i,3),C.red2,2)})}
  else if(kind==='organization_nodes'){let xs=[430,760,1090,1420];seg(xs[0],470,xs[3],470,a,C.gold,3);xs.forEach((x,i)=>{seg(x,470,x,660,reveal(p,i,4),C.gold,2);box(x-105,650,210,86,i===1?C.red:'#332829',C.gold,6,2);fit(['组织','联系','行动','反馈'][i],x,704,25,180,C.white,'center','600')});txt('组织关系示意',960,830,21,muted,'center');break}
  else if(kind==='labor_network'){let xs=[360,660,960,1260,1560];xs.forEach((x,i)=>{if(i<xs.length-1)seg(x+38,600,xs[i+1]-38,600,reveal(p,i,4),C.gold,4);for(let j=0;j<3;j++)circ(x,530+j*70,17,C.red2,C.pale,1);fit(['成员','联络','工会','传播','持续'][i],x,780,22,160,fg,'center','600')})}
  else if(kind==='village_links'){circ(cx,cy,190,null,C.gold,2);circ(cx,cy,325,null,C.red2,2);nodes.forEach((n,i)=>{let an=-Math.PI/2+i*2*Math.PI/nodes.length,x=cx+Math.cos(an)*320,y=cy+Math.sin(an)*250;seg(cx,cy,x,y,reveal(p,i,nodes.length),'#A99A72',2);circ(x,y,45,C.ink2,C.gold,2);fit(n[2],x,y+7,19,100,fg,'center','600')})}
  else{nodes.forEach((n,i)=>seg(cx,cy,n[0],n[1],reveal(p,i,nodes.length),C.gold,3));nodes.forEach((n,i)=>{let q=reveal(p,i,nodes.length);circ(n[0],n[1],52*q,kind==='central_bureau'&&i===0?C.red:C.ink2,C.gold,2);fit(n[2],n[0],n[1]+8,23,96,fg,'center','600')})}
  if(kind==='city_links'||kind==='village_links'||kind==='relay_map')txt('关系示意 · 不按地理比例',1780,820,19,muted,'right');break}
 case 'idea_river':case 'pressure_field':case 'narrowing_ribbon':case 'fracture_line':case 'continuing_route':{
  let pts=kind==='narrowing_ribbon'?[[200,390],[620,440],[1020,540],[1500,680],[1750,730]]:kind==='fracture_line'?[[150,620],[520,620],[700,520],[860,690],[1060,510],[1290,635],[1740,635]]:[[150,620],[450,470],[780,560],[1090,430],[1410,560],[1770,390]];
  path(pts,a,C.red2,kind==='narrowing_ribbon'?24:11);path(pts,clamp(p-.08),C.gold,3);
  if(kind==='narrowing_ribbon'){for(let i=0;i<5;i++){let x=260+i*320;seg(x,365,x,760,1,'rgba(197,166,119,.35)',1)}}
  else ['思想传播','社会响应','组织实践'].forEach((s,i)=>{let x=370+i*610;dot(x,550+(i%2)*80,11,C.gold);txt(s,x,760,24,fg,'center')});break}
 case 'pressure_meter':{
  const vals=[.92,.77,.65,.49];const names=['行动空间','补给条件','队伍承受','决策压力'];names.forEach((s,i)=>{let y=420+i*92,q=reveal(p,i,4);txt(s,320,y+12,24,fg,'right');box(390,y-12,1050,28,'#302526',null,3);box(390,y-12,1050*vals[i]*q,28,i===0?C.red2:C.gold,null,3);txt('压力示意',1535,y+12,19,muted,'left')});txt('不表示历史统计数值',960,830,22,muted,'center');break}
 case 'principle_bridge':{
  path([[300,700],[480,500],[700,430],[960,400],[1220,430],[1440,500],[1620,700]],a,C.gold,8);
  [460,720,960,1200,1460].forEach((x,i)=>{let h=190+(i%2)*40;rect(x-12,700-h,24,h,C.red2);seg(x-72,700-h,x+72,700-h,1,C.gold,3)});
  seg(300,700,1620,700,a,C.gold,5);txt('思想教育',520,790,25,fg,'center');txt('组织建设',960,790,25,fg,'center');txt('政治工作',1400,790,25,fg,'center');txt('原则落实到队伍建设',960,355,29,C.gold,'center','700',serif);break}
 case 'source_margin':case 'document_blocks':case 'decision_stack':case 'restraint_card':case 'source_frame':{
  if(kind==='source_margin'){box(340,370,890,440,'#E9DFC9','#B7A68D',3,2);rect(385,420,8,320,C.red);for(let i=0;i<6;i++){let yy=445+i*48;seg(435,yy,1120-(i%3)*90,yy,reveal(p,i,6),'#9B8B72',3)}[['日期',1325,420],['出处',1515,540],['口径',1325,660]].forEach(([s,x,y],i)=>{circ(x,y,46,null,C.red2,3);txt(s,x,y+8,22,fg,'center','600');seg(1230,y,x-48,y,reveal(p,i,3),C.gold,2)})}
  else if(kind==='document_blocks'){let titles=['文件结构','核心要点','版本说明'];titles.forEach((s,i)=>{let x=310+i*450,q=reveal(p,i,3);box(x,420,370,330,i===1?'#E6D8C2':'#F2EBDD',i===1?C.red2:'#B7A68D',3,2);rect(x,420,370,12,i===1?C.red:C.gold);fit(s,x+185,490,31,320,C.red,'center','700',serif);for(let r=0;r<4;r++)seg(x+44,545+r*42,x+322-((r+i)%3)*35,545+r*42,q,'#9E907B',2)});}
  else if(kind==='decision_stack'){let rows=['形成共同纲领','明确组织安排','开启后续实践'];rows.forEach((s,i)=>{let x=535+i*34,y=410+i*118,w=850-i*68,q=reveal(p,i,3);box(x,y,w,88,'#342827',C.gold,5,2);rect(x,y,12,88,i===0?C.red2:C.gold);fit(s,x+w/2,y+56,30,w-50,C.white,'center','600',serif);if(i<2)seg(x+w/2,y+88,x+w/2,y+117,q,C.red2,4)});}
  else if(kind==='restraint_card'){box(300,405,610,350,'#E9DFC9','#B7A68D',4,2);box(1010,405,610,350,'#342827',C.gold,4,2);txt('会议中形成',605,485,32,C.red,'center','700',serif);txt('会后逐步发展',1315,485,32,C.gold,'center','700',serif);['会议决定','当时议程','正式文件'].forEach((s,i)=>{circ(405,550+i*62,7,C.red);txt(s,440,558+i*62,24,C.ink)});['分工调整','行动延续','新的问题'].forEach((s,i)=>{circ(1115,550+i*62,7,C.gold);txt(s,1150,558+i*62,24,C.white)});seg(910,580,1010,580,a,C.red2,5)}
  else {g.save();g.setLineDash([18,12]);box(430,375,1060,440,null,C.gold,2,4);g.restore();circ(960,575,120,null,C.red2,4);circ(960,575,165,null,C.gold,2);txt('史料',960,565,44,fg,'center','700',serif);txt('与示意',960,616,27,C.gold,'center','600');txt('先区分材料性质，再讨论解释边界',960,790,25,fg,'center')}
  txt(kind==='source_frame'?'史料与示意明确区分':'结构示意 · 非档案原件',960,850,21,muted,'center');break}
 case 'delegate_scale':case 'meeting_table':case 'memory_boundary':case 'lake_marker':{
  if(kind==='delegate_scale'){txt('12',620,580,150,C.red,'center','700',serif);txt('正式代表',620,635,28,muted,'center');txt('+',950,560,90,C.gold,'center');txt('1',1240,580,150,C.ink,'center','700',serif);txt('包惠僧',1240,635,28,muted,'center');seg(490,700,1420,700,a,C.red,3);txt('中国参会者共 13 人 · 代表 50 多名党员',960,765,31,C.ink,'center','600');txt('另有两位共产国际代表出席',960,814,22,muted,'center')}
  else if(kind==='meeting_table'){circ(960,570,250,null,C.gold,5);circ(960,570,190,null,'#4A3433',2);for(let i=0;i<13;i++){let an=i*2*Math.PI/13-Math.PI/2,x=960+Math.cos(an)*230,y=570+Math.sin(an)*230;circ(x,y,11,ease((p-i*.035)/.4)>0?C.red2:null,C.pale,1)}txt('共同议事',960,580,39,fg,'center','700',serif);txt('人数布局为说明性示意',960,850,21,muted,'center')}
  else if(kind==='memory_boundary'){box(270,390,610,355,C.ink2,C.gold,6,2);box(1040,390,610,355,C.pale,'#B7A68D',6,2);txt('纪念象征',575,470,34,C.gold,'center','700');txt('可辨认的史实',1345,470,34,C.red,'center','700');txt('红船意象',575,590,58,C.white,'center','700',serif);txt('会议最后一天',1345,555,31,C.ink,'center','600',serif);txt('转到嘉兴南湖继续举行',1345,602,31,C.ink,'center','600',serif);seg(880,570,1040,570,a,C.red2,5);txt('当代纪念船不是 1921 年原船实拍',960,810,24,muted,'center')}
  else {for(let i=0;i<7;i++){let x=250+i*235,yy=600+Math.sin(i*.85)*42;path([[x-40,yy+15],[x+70,yy+20],[x+150,yy-6]],reveal(p,i,7),C.gold,4);circ(x+70,yy+20,7,C.red2)}txt('1921 · 上海',480,450,36,fg,'center','700',serif);txt('嘉兴 · 南湖',1430,690,36,fg,'center','700',serif);txt('会议地点转移示意 · 非比例地图',960,820,21,muted,'center')}
  break}
 case 'date_cards':case 'three_dates':case 'date_division':case 'broken_rail':{
  let dates=kind==='date_division'?['1935.01.15–17','2 月初','3 月']:['9 月 19 日','9 月 29 日','10 月 27 日'];let acts=kind==='date_division'?['遵义会议','常委分工调整','成立新的三人军事指挥小组']:['文家市：决定转向','三湾：改编队伍','井冈山茨坪：抵达'];
  if(kind==='date_division'){seg(250,610,1670,610,a,C.gold,5);dates.forEach((d,i)=>{let x=380+i*580,q=reveal(p,i,3);seg(x,610,x,480+(i%2)*250,q,C.red2,4);circ(x,610,15,C.red,C.pale,2);txt(d,x,445+(i%2)*250,30,C.gold,'center','700',serif);fit(acts[i],x,515+(i%2)*250,25,340,fg,'center','600')})}
  else if(kind==='broken_rail'){seg(220,600,770,600,a,C.gold,8);seg(1150,600,1700,600,a,C.gold,8);path([[770,600],[825,555],[880,640],[940,555],[1000,640],[1060,600]],a,C.red2,8);dates.forEach((d,i)=>{let x=[330,960,1590][i],y=i===1?700:485;circ(x,600,12,C.pale,C.gold,2);txt(d,x,y,28,C.gold,'center','700',serif);fit(acts[i],x,y+48,24,390,fg,'center','600')});txt('路径中断后重新组织行动',960,820,22,muted,'center')}
  else{dates.forEach((d,i)=>{let x=300+i*660,q=reveal(p,i,3),y=450+(i%2)*90;box(x,y,500,235,q>0?C.pale:'#D8CBB6',i===1?C.red2:'#B7A68D',4,2);txt(d,x+34,y+70,35,C.red,'left','700',serif);fit(acts[i],x+34,y+135,30,420,C.ink,'left','600');if(i<2)seg(x+500,y+115,x+660,y+160,q,C.gold,4)});txt('按时间区分会议决定与后续变化',960,820,22,muted,'center')}
  break}
 case 'route_stages':case 'location_shift':case 'dashed_route':case 'field_window':{
  let names=kind==='location_shift'?['上海','嘉兴南湖']:['文家市','三湾','井冈山茨坪'];let pts=kind==='location_shift'?[[500,570],[1420,570]]:[[330,600],[960,430],[1580,620]];
  if(kind==='location_shift'){rect(210,390,570,360,'rgba(197,166,119,.12)');rect(1140,390,570,360,'rgba(197,166,119,.12)');path([[500,570],[770,460],[960,610],[1140,460],[1420,570]],a,C.red2,8,[14,12]);pts.forEach((v,i)=>{circ(v[0],v[1],68,C.ink2,C.gold,3);fit(names[i],v[0],v[1]+8,26,200,C.white,'center','600')});txt('会议地点转移示意 · 非比例地图',960,830,22,muted,'center')}
  else if(kind==='field_window'){box(270,390,1380,390,'rgba(15,15,15,.18)',C.gold,160,3);for(let i=0;i<5;i++){let x=390+i*285,y=650-Math.sin(i*.8)*85;path([[x-70,700],[x,y-100],[x+80,700]],1,i%2?'#566147':'#3E5545',4)}path(pts,a,C.red2,7);pts.forEach((v,i)=>{circ(v[0],v[1],12,C.pale,C.gold,2);if(i<3)fit(names[i],v[0],v[1]-40,22,230,fg,'center','600')});txt('山地地形中的路线关系示意',960,840,22,muted,'center')}
  else if(kind==='dashed_route'){path(pts,a,C.gold,10,[16,12]);pts.forEach((v,i)=>{circ(v[0],v[1],43,i===1?C.red:C.ink2,C.gold,3);fit(names[i],v[0],v[1]+95,24,220,fg,'center','600')});txt('节点关系示意 · 非精确行军路线',960,825,22,muted,'center')}
  else{path(pts,a,C.gold,8);pts.forEach((v,i)=>{rect(v[0]-8,v[1]-58,16,58,C.red2);circ(v[0],v[1]-72,16,C.pale,C.gold,2);fit(names[i],v[0],v[1]+53,23,250,fg,'center','600')})}
  break}
 case 'unit_rebuild':case 'company_branch':case 'organization_scaffold':case 'responsibility_lanes':case 'command_shift':{
  if(kind==='company_branch'){let root=[960,400],mid=[[560,580],[960,580],[1360,580]];seg(960,450,960,510,a,C.gold,4);mid.forEach((v,i)=>{seg(root[0],root[1]+50,v[0],v[1]-45,reveal(p,i,3),C.gold,3);box(v[0]-120,v[1]-35,240,70,C.ink2,C.gold,5,2);fit(['连队','支部','小组'][i],v[0],v[1]+9,25,200,C.white,'center','600');for(let j=0;j<3;j++)seg(v[0],v[1]+36,v[0]-70+j*70,785,reveal(p,i,3),C.red2,2)});txt('基层组织关系示意',960,870,21,muted,'center')}
  else if(kind==='organization_scaffold'){let layers=[['组织原则',410],['基层单位',545],['日常联系',680]];layers.forEach(([s,y],i)=>{let q=reveal(p,i,3),w=620+i*280;box(960-w/2,y,w*q,74,i===0?C.red:'#332829',C.gold,34,2);fit(s,960,y+47,25,w-50,C.white,'center','600');if(i<2)seg(960,y+74,960,y+132,q,C.gold,3)});txt('组织建设由原则落实到基层',960,850,22,muted,'center')}
  else if(kind==='command_shift'){box(300,390,570,340,'#E9DFC9','#B7A68D',3,2);box(1050,390,570,340,'#342827',C.gold,3,2);txt('原有安排',585,470,34,C.red,'center','700',serif);txt('调整之后',1335,470,34,C.gold,'center','700',serif);for(let i=0;i<3;i++){let y=540+i*62;box(380,y,410,34,'#BEB09A',null,3);box(1130,y,410*(.62+i*.12)*a,34,i===0?C.red2:C.gold,null,3)}seg(870,560,1050,560,a,C.pale,6);txt('领导机制变化示意',960,830,22,muted,'center')}
  else {let rows=kind==='responsibility_lanes'?['会议决策','会后分工','军事指挥']:['改编前','组织关系调整','基层联系'];rows.forEach((s,i)=>{let y=420+i*125,q=reveal(p,i,3),x=300+i*120,w=1320-i*180;box(x,y,w*q,78,i===1?C.red:'#36292A',C.gold,5,2);txt(s,x+35,y+50,27,C.white,'left','600');for(let j=0;j<4;j++)if(i===1)dot(x+380+j*190,y+39,8,C.pale)});}
  break}
 case 'support_conditions':case 'method_flow':case 'labor_workflow':case 'political_work':case 'daily_work':case 'practice_table':{
  let names=kind==='support_conditions'?['社会条件','交通补给','群众基础','军事压力']:kind==='method_flow'?['事实核对','历史归纳','结构示意']:kind==='labor_workflow'?['联系成员','传播主张','工会工作','持续联络']:kind==='political_work'?['思想教育','组织生活','政治工作']:kind==='daily_work'?['学习','讨论','执行','检验']:['方向','组织','实践','反馈'];let n=names.length, step=1280/n,left=320;
  if(kind==='support_conditions'){names.forEach((s,i)=>{let x=430+i*350,h=(170+((i*71)%170))*reveal(p,i,n),y=760-h;rect(x,y,160,h,i===0?C.red:'#8C775A');rect(x,y,160,7,C.gold);fit(s,x+80,815,22,270,fg,'center','600');txt(['01','02','03','04'][i],x+80,y-20,22,C.gold,'center','700',serif)});txt('条件并列，不换算成统计数值',960,875,20,muted,'center')}
  else if(kind==='method_flow'){names.forEach((s,i)=>{let x=430+i*530,y=690-i*140,q=reveal(p,i,n);box(x,y,420,120,i===1?C.red:'#332829',C.gold,3,2);fit(s,x+210,y+74,29,360,C.white,'center','600');if(i<n-1)path([[x+420,y+60],[x+490,y+60],[x+490,y-80]],q,C.gold,4)});txt('方法由核对走向归纳，再回到呈现',960,870,20,muted,'center')}
  else if(kind==='labor_workflow'){let pts=[[300,680],[700,520],[1120,680],[1580,460]];path(pts,a,C.gold,6);names.forEach((s,i)=>{let [x,y]=pts[i],q=reveal(p,i,n);circ(x,y,58*q,i===1?C.red:C.ink2,C.gold,3);fit(s,x,y+110,22,260,fg,'center','600')})}
  else if(kind==='political_work'){path([[390,700],[540,450],[1380,450],[1530,700]],a,C.gold,8);names.forEach((s,i)=>{let x=560+i*400,h=200+(i===1?90:0);rect(x,700-h,26,h,C.red2);rect(x-55,700-h,136,13,C.gold);fit(s,x+12,755,23,200,fg,'center','600')});txt('思想与组织共同支撑政治工作',960,370,27,C.gold,'center','600',serif)}
  else if(kind==='daily_work'){let pts=[[680,440],[1240,440],[1240,720],[680,720]];path([...pts,pts[0]],a,C.gold,5);names.forEach((s,i)=>{let [x,y]=pts[i],q=reveal(p,i,n);circ(x,y,74*q,i===2?C.red:C.ink2,C.gold,3);fit(s,x,y+8,25,150,fg,'center','600')})}
  else if(kind==='practice_table'){box(390,390,1140,430,null,C.gold,3,2);seg(960,390,960,820,1,C.gold,2);seg(390,605,1530,605,1,C.gold,2);names.forEach((s,i)=>{let x=675+(i%2)*570,y=510+Math.floor(i/2)*215;circ(x,y-10,18,i===2?C.red:C.gold);fit(s,x,y+55,25,380,fg,'center','600')})}
  else names.forEach((s,i)=>{let x=left+i*step,q=reveal(p,i,n),h=(i%2?175:250)*q,y=630-h/2;box(x,y,step-32,h,i===0?C.red:C.pale,i===0?null:'#B7A68D',4,2);fit(s,x+(step-32)/2,y+h/2+8,25,step-55,i===0?C.white:C.ink,'center','600');if(i<n-1)seg(x+step-30,630,x+step+5,630,reveal(p,i,n),C.gold,4)});
  break}
 case 'practice_loop':case 'feedback_cycle':case 'practice_spiral':case 'practice_loop':{
  if(kind==='practice_spiral'){let pts=[];for(let i=0;i<28;i++){let an=-Math.PI/2+i*.42,r=20+i*15;pts.push([960+Math.cos(an)*r,590+Math.sin(an)*r])}path(pts,a,C.gold,5);txt('实践不断展开',960,590,27,C.gold,'center','600',serif)}
  else if(kind==='feedback_cycle'){circ(960,590,285,null,C.gold,4);circ(960,590,170,null,C.red2,2);['提出问题','采取行动','观察结果','调整方法'].forEach((s,i)=>{let an=-Math.PI/2+i*Math.PI/2,x=960+Math.cos(an)*285,y=590+Math.sin(an)*210;circ(x,y,58,C.red,C.gold,2);fit(s,x,y+8,21,118,C.white,'center','600')})}
  else{let pts=[[570,480],[1350,480],[1350,730],[570,730],[570,480]];path(pts,a,C.gold,6);['提出问题','采取行动','观察结果','调整方法'].forEach((s,i)=>{let [x,y]=pts[i],q=reveal(p,i,4);box(x-90,y-45,180,90,i===2?C.red:'#332829',C.gold,36,2);fit(s,x,y+8,22,160,C.white,'center','600')})}break}
 case 'problem_marks':case 'three_problems':case 'problem_marks':{
  let names=kind==='three_problems'?['单纯军事观点','极端民主化','流寇思想']:['思想认识','组织运行','政治工作'];names.forEach((s,i)=>{let x=420+i*540,q=reveal(p,i,names.length);g.save();g.globalAlpha=q;path([[x-145,710],[x-50,490],[x+25,590],[x+95,405],[x+155,710]],1,C.red2,8);circ(x,725,44,C.ink2,C.gold,2);txt(s,x,810,25,fg,'center','600');g.restore()});break}
 case 'resolution_focus':case 'meeting_focus':case 'decision_blocks':case 'decision_scope':case 'fact_scope':{
  if(kind==='meeting_focus'){circ(960,595,225*a,null,C.gold,3);circ(960,595,150*a,null,C.red2,5);txt('遵义',960,588,82,fg,'center','700',serif);txt('军事与组织问题',960,640,26,C.gold,'center')}
  else if(kind==='decision_blocks'){let labels=['增选毛泽东为常委','委托张闻天起草决议','取消原“三人团”'];labels.forEach((s,i)=>{let y=410+i*138,q=reveal(p,i,3);circ(390,y+44,36,i===0?C.red:C.ink2,C.gold,2);txt(String(i+1),390,y+53,23,C.white,'center','700',serif);seg(445,y+44,610,y+44,q,C.gold,3);box(620,y,950,88,'#332827',C.gold,4,2);fit(s,665,y+56,29,860,C.white,'left','600',serif)})}
  else if(kind==='decision_scope'){box(300,400,600,390,'#E9DFC9','#B7A68D',3,2);box(1020,400,600,390,'#332827',C.gold,3,2);txt('会议明确形成',600,475,31,C.red,'center','700',serif);txt('会后继续发展',1320,475,31,C.gold,'center','700',serif);['组织安排','决议起草','指挥机制'].forEach((s,i)=>{let y=550+i*74;seg(390,y,810,y,1,'#B6A88F',3);fit(s,600,y-14,22,390,C.ink,'center','600')});['分工调整','行动延续','新的问题'].forEach((s,i)=>{let y=550+i*74;seg(1110,y,1530,y,1,'#715D4C',3);fit(s,1320,y-14,22,390,C.white,'center','600')})}
  else if(kind==='fact_scope'){let labels=['事实','归纳','示意'];let xs=[550,960,1370];labels.forEach((s,i)=>{let q=reveal(p,i,3);circ(xs[i],580,116*q,i===0?C.red:i===1?C.gold:C.ink2,C.pale,2);fit(s,xs[i],593,32,190,C.white,'center','700',serif);if(i<2)seg(xs[i]+125,580,xs[i+1]-125,580,q,C.gold,4)});txt('三类内容分层呈现，不相互替代',960,800,23,muted,'center')}
  else{txt('取 舍',960,560,120,C.gold,'center','700',serif);seg(510,650,1410,650,a,C.red2,5);txt('组织方向',560,735,28,fg,'center');txt('具体问题',1360,735,28,fg,'center');txt('在危急局势中重新判断行动重点',960,830,24,muted,'center')}
  break}
 case 'decision_stack':case 'decision_scope':case 'document_blocks':break;
 case 'date_return':case 'chapter_link':{
  const y=600,xs=[300,720,1150,1600];years.forEach((v,i)=>{if(i<3)seg(xs[i]+72,y,xs[i+1]-72,y,reveal(p,i,4),C.gold,5);circ(xs[i],y,60*reveal(p,i,4),C.red,C.gold,2);txt(v,xs[i],y+16,34,C.white,'center','700',serif)});txt('成立组织',300,720,22,muted,'center');txt('道路探索',720,720,22,muted,'center');txt('队伍建设',1150,720,22,muted,'center');txt('总结调整',1600,720,22,muted,'center');break}
 case 'three_lenses':case 'method_marks':{
  let labels=['时代条件','组织行动','实践检验'];let xs=[500,960,1420],ys=[520,520,520];labels.forEach((s,i)=>{let r=150*reveal(p,i,3);g.save();g.translate(xs[i],ys[i]);g.rotate((i-1)*.1);g.beginPath();g.ellipse(0,0,r,r*.68,0,0,Math.PI*2);g.strokeStyle=i===1?C.red2:C.gold;g.lineWidth=5;g.stroke();txt(s,0,12,29,fg,'center','600');g.restore()});break}
 case 'date_cards':break;
 case 'meeting_table':break;
 case 'city_links':break;
 case 'three_problems':break;
 case 'year_return':break;
 case 'fracture_line':break;
 case 'shikumen_frame':break;
 case 'document_blocks':break;
 case 'narrowing_ribbon':break;
 case 'central_bureau':break;
 case 'source_frame':break;
 case 'title_end':{
  years.forEach((v,i)=>{let x=360+i*400,y=440+Math.sin(i*1.1)*115,q=reveal(p,i,4);circ(x,y,52*q,C.red,C.gold,2);txt(v,x,y+13,31,C.white,'center','700',serif);if(i<3)seg(x+55,y,x+345,440+Math.sin((i+1)*1.1)*115,q,C.gold,4)});txt('从石库门到遵义',960,690,68,C.white,'center','700',serif);txt('在实践中不断探索',960,755,31,C.gold,'center');break}
 default:{
  let labels=['提出问题','形成组织','开展实践','回看结果'];labels.forEach((s,i)=>{let q=reveal(p,i,4),x=350+i*410,y=500+(i%2)*140;box(x,y,300,150,q>0?'#332829':null,C.gold,7,2);fit(s,x+150,y+88,27,270,fg,'center','600');if(i<3)seg(x+302,y+75,x+408,y+140,q,C.gold,3)});
 }
 }
}
function updateCaption(value){
 const line1=document.getElementById('caption-line-1'),line2=document.getElementById('caption-line-2');if(!line1||!line2)return;
 const chars=Array.from(String(value||'').replace(/\s+/g,''));let first=chars,second=[];
 if(chars.length>43){let split=43;for(let i=31;i<=43;i++)if('，。；：！？、'.includes(chars[i-1]))split=i;first=chars.slice(0,split);second=chars.slice(split);}
 line1.textContent=first.join('');line2.textContent=second.join('');line2.style.display=second.length?'':'none';
 line1.setAttribute('y',second.length?'909':'923');line2.setAttribute('y','947');
}
function updateSourceLabel(t){
 const label=document.getElementById('source-label');if(!label)return;
 const active=Array.from(document.querySelectorAll('video.huashu')).some(v=>{const s=Number(v.dataset.start)||0,d=Number(v.dataset.duration)||0;return t>=s&&t<s+d});
 label.style.display=active?'block':'none';
}
function renderAt(timestamp){if(!Number.isFinite(timestamp))timestamp=0;let t=clamp(timestamp,0,TOTAL-.001),shot=findShot(t),ch=CHAPS.find(v=>v.id===shot.chapter)||CHAPS[0],dur=Math.max(.01,shot.end-shot.start),p=clamp((t-shot.start)/dur),light=background(shot.kind,t);shell(ch,shot,t,light);g.save();g.globalAlpha=clamp((t-shot.start)/.18)*clamp((shot.end-t)/.22);content(shot.kind,shot.label,p,t,ch,light);g.restore();updateCaption(shot.caption);updateSourceLabel(t);window.__currentShot=shot.id;return shot}
window.renderAt=renderAt;window.montageRender=(i,p)=>{let sh=SHOTS[clamp(i|0,0,SHOTS.length-1)];return renderAt(sh.start+(sh.end-sh.start)*clamp(p))};renderAt(0);
})();
