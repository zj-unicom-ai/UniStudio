/* 光影党史：100% Canvas2D 可寻址动画引擎。
 * 时间 -> 像素，禁止Date.now/Math.random/无限CSS循环；可被 HyperFrames 的 GSAP seek 调用。
 * 所有史地路线是结构示意，不是严格地理数据；任何原档案需替换成来源清楚的真材料。
 */
(function(){
'use strict';
const W=1920,H=1080, C={ink:'#1D1918',black:'#181516',red:'#842D34',red2:'#A94542',gold:'#C5A677',paper:'#E9DFCA',pale:'#EFE7D5',dim:'#AD9E8D',white:'#F6F0E6'};
const cn=document.getElementById('sceneCanvas');const g=cn.getContext('2d',{alpha:false});
let data=window.EP01_M4;let SHOTS=data.shots,CHAPS=data.chapters;const TOTAL=data.duration_seconds;
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const ease=t=>{t=clamp(t);return t*t*(3-2*t)};
const easeOut=t=>1-Math.pow(1-clamp(t),3);
const fract=t=>t-Math.floor(t);
function alphaText(t,x,y,size,color=C.paper,family='serif',weight='bold',align='left',opacity=1){g.save();g.globalAlpha=opacity;g.font=`${weight} ${size}px ${family==='serif'?"'Noto Serif CJK SC','Songti SC','STSong',serif":"'GuangyingSans',sans-serif"}`;g.textAlign=align;g.fillStyle=color;g.fillText(t,x,y);g.restore()}
function ellipse(x,y,rx,ry,fill){g.save();g.fillStyle=fill;g.beginPath();g.ellipse(x,y,rx,ry,0,0,Math.PI*2);g.fill();g.restore()}
function rect(x,y,w,h,c){g.fillStyle=c;g.fillRect(x,y,w,h)}
function line(x1,y1,x2,y2,color=C.gold,lw=3,p=1){p=clamp(p);g.save();g.strokeStyle=color;g.lineWidth=lw;g.lineCap='round';g.beginPath();g.moveTo(x1,y1);g.lineTo(x1+(x2-x1)*p,y1+(y2-y1)*p);g.stroke();g.restore()}
function poly(points,p,color=C.gold,lw=5){p=clamp(p);if(points.length<2)return;let lens=[],total=0;for(let i=1;i<points.length;i++){const l=Math.hypot(points[i][0]-points[i-1][0],points[i][1]-points[i-1][1]);lens.push(l);total+=l;}let remaining=p*total;g.save();g.strokeStyle=color;g.lineWidth=lw;g.lineCap='round';g.lineJoin='round';g.beginPath();g.moveTo(...points[0]);for(let i=1;i<points.length;i++){let u=lens[i-1]>0?Math.min(1,remaining/lens[i-1]):1;g.lineTo(points[i-1][0]+(points[i][0]-points[i-1][0])*u,points[i-1][1]+(points[i][1]-points[i-1][1])*u);remaining-=lens[i-1];if(u<1)break}g.stroke();g.restore()}
function dot(x,y,r,c=C.red){ellipse(x,y,r,r,c)}
function roundRect(x,y,w,h,r,fill,stroke){g.save();g.beginPath();g.roundRect(x,y,w,h,r);if(fill){g.fillStyle=fill;g.fill()}if(stroke){g.strokeStyle=stroke;g.lineWidth=2;g.stroke()}g.restore()}
function tile(t){g.fillStyle=C.black;g.fillRect(0,0,W,H); const rad=g.createRadialGradient(1340,360,180,1140,540,1200);rad.addColorStop(0,'#36272A');rad.addColorStop(0.58,'#251C1E');rad.addColorStop(1,C.black);g.fillStyle=rad;g.fillRect(0,0,W,H);g.save();g.globalAlpha=.12;g.strokeStyle=C.gold;g.lineWidth=1;for(let i=0;i<23;i++){const x=(i*131+17)%W;g.beginPath();g.moveTo(x,0);g.lineTo(x-320,H);g.stroke()}g.restore();
 // 独立于系统时间的光影脉冲
 const s=Math.sin(t*.44);let r=g.createRadialGradient(1200+Math.sin(t*.13)*160,500,40,1200,540,980);r.addColorStop(0,`rgba(150,70,60,${.12+.035*s})`);r.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=r;g.fillRect(0,0,W,H);
}
function paper(x,y,w,h){g.save();g.shadowBlur=24;g.shadowColor='rgba(0,0,0,.42)';roundRect(x,y,w,h,6,C.paper);g.shadowBlur=0;rect(x+18,y+12,w-36,2,'#D2BFA0');g.globalAlpha=.2;for(let k=0;k<11;k++)line(x+32,y+70+k*22,x+w-34,y+70+k*22,C.ink,.8);g.restore()}
function base(ch,sh,t,local){tile(t); const n=+ch.id.slice(1);g.save();rect(0,0,13,H,C.red);rect(88,91,66,6,C.red2);alphaText('光 影 党 史  ·  D O C U M E N T A R Y',174,105,22,C.gold,'sans','500');line(94,135,1820,135,'#5B4541',1);alphaText(ch.title,95,193,42,C.white,'serif');alphaText('历史解说 · 动态纪录片',1824,103,22,C.dim,'sans','400','right');g.restore();
 // all shots have changing vector content, not just a still background
 rect(95,992,1734,2,'#6C554B');rect(95,992,1734*clamp(t/TOTAL),4,C.gold);
 alphaText(`${String(n).padStart(2,'0')} / 09`,99,1036,22,C.dim,'sans','500');alphaText(`${format(t)}  /  ${format(TOTAL)}`,1820,1036,22,C.dim,'sans','500','right');
}
function format(t){const m=Math.floor(t/60),s=Math.floor(t%60);return String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')}
function chapterFor(sh){return CHAPS.find(c=>c.id===sh.chapter)||CHAPS[0]}
function shotAt(t){let lo=0,hi=SHOTS.length-1;while(lo<hi){let mid=Math.floor((lo+hi)/2);if(SHOTS[mid].end<=t)lo=mid+1;else hi=mid;}return SHOTS[lo];}
function textCut(s,n=24){return s.length>n?s.slice(0,n)+'…':s}
function drawHero(ch,sh,p,t){
 const years=['1921','1927','1929','1935'];const y=365;let xx=[240,715,1195,1680];
 g.save();g.translate(0,Math.sin(t*.4)*3);
 for(let i=0;i<4;i++){let on=ease((p-i*.13)/.32);ellipse(xx[i],y+60,108*on,108*on,`rgba(132,45,52,${.22*on})`);dot(xx[i],y+60,12*on,C.gold);alphaText(years[i],xx[i],y+5,88,C.paper,'serif','bold','center',on);if(i<3)line(xx[i]+125,y+60,xx[i+1]-130,y+60,C.gold,4,ease((p-i*.12)/.5));}
 alphaText('从石库门到遵义',960,673,96,C.paper,'serif','bold','center',ease((p-.1)/.35));alphaText('在探索中寻找中国革命的道路',960,758,40,C.gold,'serif','400','center',ease((p-.27)/.40));
 g.restore();}
function drawTimeline(ch,sh,p,t){
 const years=['1911','1919','1921','1927','1929','1935'];const lab=['辛亥革命','五四运动','中共一大','革命道路探索','古田会议','遵义会议'];const x0=175,dx=310,y=530;
 line(x0,y,1784,y,C.gold,8,ease(p*.95+.06));
 years.forEach((yval,i)=>{let tx=x0+i*dx,u=ease((p-i*.095)/.45);dot(tx,y,15*u,C.red2);g.save();g.globalAlpha=u;alphaText(yval,tx,455,60,C.paper,'serif','bold','center');alphaText(lab[i],tx,625,24,C.gold,'sans','500','center');g.restore();});
 poly([[140,720],[420,774],[790,704],[1160,761],[1530,716],[1785,744]],ease((p-.25)*1.2),'#80524A',3);
}
function drawRoute(ch,sh,p,t){
 // A deliberately schematic movement/relationship map, NOT geographic coordinates.
 g.save();g.globalAlpha=.18;for(let k=0;k<13;k++){g.beginPath();let y=280+k*36;g.moveTo(70,y+Math.sin(k)*20);for(let x=80;x<1860;x+=25)g.lineTo(x,y+Math.sin(x/122+k*.43)*25);g.strokeStyle=C.gold;g.lineWidth=2;g.stroke()}g.restore();
 const pts=[[270,420],[475,350],[755,605],[1115,455],[1430,655],[1720,470]];
 const key=ch.id==='S07'?['长征出发','转移','湘江','遵义','继续前进','探索']:(ch.id==='S04'?['上海','会场','组织','南湖','延续','回望']:['危机','南昌','秋收起义','三湾','井冈山','探索']);
 poly(pts,ease(p),C.red2,13);poly(pts,ease((p-.05)/.95),C.gold,3);
 pts.forEach((v,i)=>{let k=ease((p-i*.12)/.24);dot(v[0],v[1],11*k,C.gold);g.save();g.globalAlpha=k;alphaText(key[i],v[0],v[1]-31,26,C.white,'sans','500','center');g.restore()});
 alphaText('结构性路线示意 · 非历史精确行军路径',1730,859,22,C.dim,'sans','400','right');
}
function drawArchive(ch,sh,p,t){
 // Abstract document is always explicitly marked as structural illustration, not fake original page.
 let dx=(1-ease(p*.65))*120; paper(170+dx,266,1045,590);g.save();g.globalAlpha=ease((p-.06)/.3);
 alphaText(ch.id==='S04'?'1921 · 上海 / 嘉兴':ch.id==='S07'?'1935 · 遵义':'历史资料 · 事件结构',260,360,37,C.red,'serif');
 alphaText('从历史背景到关键选择',260,451,51,C.ink,'serif');
 const labels=['时代背景','重要事件','组织行动','历史影响'];labels.forEach((s,i)=>{let yy=530+i*73;dot(273,yy-15,7,C.red);line(305,yy-17,1000,yy-17,C.dim,1);alphaText(s,321,yy+22,25,C.ink,'sans','500')});
 g.restore();
 const cy=525; g.save();g.strokeStyle=C.gold;g.lineWidth=3;g.beginPath();g.arc(1485,cy,160,-1.45,-1.45+Math.PI*2*ease(p));g.stroke();g.restore();alphaText(ch.id==='S04'?'1921':ch.id==='S06'?'1929':ch.id==='S07'?'1935':'党史',1485,545,96,C.paper,'serif','bold','center');alphaText('结构图解 · 非原始史料',1485,810,24,C.dim,'sans','400','center');
}
function drawNetwork(ch,sh,p,t){
 const nodes=[{x:980,y:370,s:'共同目标',r:120},{x:460,y:622,s:'组织建设',r:94},{x:970,y:727,s:'制度与方法',r:100},{x:1505,y:623,s:'实践反馈',r:96}];
 const edges=[[0,1],[0,2],[0,3],[1,2],[2,3]];
 edges.forEach((e,i)=>{const a=nodes[e[0]],b=nodes[e[1]];line(a.x,a.y,b.x,b.y,C.gold,5,ease((p-i*.09)/.52));});
 nodes.forEach((v,i)=>{const u=ease((p-i*.08)/.36);ellipse(v.x,v.y,v.r*u,v.r*u,`rgba(132,45,52,${.78*u})`);ellipse(v.x,v.y,v.r*.84*u,v.r*.84*u,'#3A2627');g.save();g.globalAlpha=u;alphaText(v.s,v.x,v.y+12,i===0?32:29,C.white,'serif','bold','center');g.restore();});
 alphaText('组织关系示意 · 非历史原件',1824,845,22,C.dim,'sans','400','right');
}
function drawWhiteboard(ch,sh,p,t){
 roundRect(140,268,1632,590,6,C.pale);rect(144,275,1624,3,'#B7A991');
 let names=ch.id==='S05'?['面临困难','组织调整','寻找路径','实践检验']:ch.id==='S07'?['发现问题','总结经验','讨论调整','继续探索']:['历史条件','提出问题','组织行动','实践总结'];
 const pts=[290,710,1140,1550];
 for(let i=0;i<4;i++){let u=ease((p-i*.15)/.29);g.save();g.globalAlpha=u;g.strokeStyle=C.red;g.lineWidth=7;g.strokeRect(pts[i]-138,470,276,195);alphaText(String(i+1).padStart(2,'0'),pts[i],524,42,C.red,'serif','bold','center');alphaText(names[i],pts[i],600,30,C.ink,'sans','bold','center');g.restore();if(i<3)line(pts[i]+144,563,pts[i+1]-152,563,C.red,7,ease((p-i*.14-.12)/.30));}
 alphaText('逻辑关系示意 · 非历史人物对话原文',1654,797,23,C.red,'sans','400','right');
}
function drawContrast(ch,sh,p,t){
 const cols=[{x:160,title:'历史问题',bg:'#EEE4D1'},{x:1010,title:'实践中的回应',bg:'#DCCCB3'}];
 cols.forEach((o,i)=>{let u=ease((p-i*.18)/.4),dx=(1-u)*(i?110:-110);roundRect(o.x+dx,280,740,538,8,o.bg);g.save();g.globalAlpha=u;rect(o.x+dx,280,740,14,i?C.gold:C.red);alphaText(o.title,o.x+55+dx,414,60,C.ink,'serif','bold');const patterns=i?["调整工作方法","加强组织建设","持续实践检验"]:["现实条件变化","组织面临考验","原有方式受限"];patterns.forEach((s,j)=>{dot(o.x+70+dx,525+j*76,9,C.red);alphaText(s,o.x+96+dx,535+j*76,30,C.ink,'sans','500')});g.restore()});
 line(905,565,1000,565,C.gold,8,ease((p-.4)/.35));
 alphaText('本片归纳 · 非会议原文',1824,845,22,C.dim,'sans','400','right');
}
function drawRecap(ch,sh,p,t){const dates=['1921','1927','1929','1935'],q=[[360,350],[840,380],[1340,335],[1590,645]];for(let i=0;i<3;i++){line(q[i][0],q[i][1],q[i+1][0],q[i+1][1],C.gold,5,ease((p-i*.14)/.4))};q.forEach((v,i)=>{const u=ease((p-i*.11)/.3);ellipse(...v,80*u,80*u,C.red);alphaText(dates[i],v[0],v[1]+14,50,C.paper,'serif','bold','center',u)});alphaText('历史不是预设答案，而是在实践中不断探索',980,854,53,C.paper,'serif','bold','center',ease((p-.28)/.45))}
const painter={hero:drawHero,timeline:drawTimeline,route:drawRoute,archive:drawArchive,network:drawNetwork,whiteboard:drawWhiteboard,contrast:drawContrast,recap:drawRecap};
function drawAt(timestamp){if(!Number.isFinite(timestamp))timestamp=0;const t=clamp(timestamp,0,TOTAL-0.001);const shot=shotAt(t),ch=chapterFor(shot),d=Math.max(.01,shot.end-shot.start),local=t-shot.start,p=clamp(local/d);
 g.save();g.setTransform(1,0,0,1,0,0);base(ch,shot,t,local);
 g.save();g.globalAlpha=clamp(local/.27)*clamp((shot.end-t)/.32);(painter[shot.kind]||drawTimeline)(ch,shot,p,t);g.restore();
 // Captions are a separate timed HyperFrames track so they remain visible over Huashu video.
 window.__currentShot=shot.id;
 g.restore();return shot;
}
window.renderAt=drawAt;window.montageRender=(idx,progress)=>{const shot=SHOTS[Math.min(SHOTS.length-1,Math.max(0,idx))];return drawAt(shot.start+(shot.end-shot.start)*clamp(progress))};
drawAt(0);
})();
