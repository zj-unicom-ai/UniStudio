/* Content-led, seekable SVG scenes. Captions and narration remain sourced from M5 unchanged. */
(function(){
  'use strict';
  const W=1920,H=1080,C={ink:'#191617',panel:'#292323',panel2:'#33292A',red:'#842D34',red2:'#A94542',gold:'#C5A677',paper:'#E9DFC9',pale:'#F4EEDF',muted:'#B3A798',green:'#637568',green2:'#405448'};
  const M=window.EP01_M6, S=M.scenes, SH=M.captions, CH=M.chapters;
  const art=document.getElementById('illustration'),titleNode=document.getElementById('chapter-title');
  const clamp=(n,a=0,b=1)=>Math.max(a,Math.min(b,n));
  const esc=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  const G=(at,html)=>`<g data-reveal="${at}">${html}</g>`;
  const T=(x,y,s,size=27,color=C.pale,anchor='middle',weight=500,extra='')=>`<text x="${x}" y="${y}" text-anchor="${anchor}" font-size="${size}" font-weight="${weight}" fill="${color}" ${extra}>${esc(s)}</text>`;
  const P=(d,color=C.gold,w=4,at=null,dash='')=>`<path d="${d}" fill="none" stroke="${color}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" ${at===null?'':dash?`data-reveal="${at}"`:`data-draw="${at}"`} ${dash?`stroke-dasharray="${dash}"`:''}/>`;
  const R=(x,y,w,h,fill='none',stroke='none',sw=0,rx=0)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  const Cc=(x,y,r,fill='none',stroke=C.gold,sw=3)=>`<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>`;
  const person=(x,y,scale=1,color=C.pale)=>`<g stroke="${color}" fill="none" stroke-width="3"><circle cx="${x}" cy="${y}" r="${9*scale}" fill="${color}" stroke="none"/><path d="M ${x-15*scale} ${y+40*scale} Q ${x-13*scale} ${y+13*scale} ${x} ${y+13*scale} Q ${x+13*scale} ${y+13*scale} ${x+15*scale} ${y+40*scale} M ${x} ${y+22*scale} L ${x} ${y+57*scale} M ${x-20*scale} ${y+37*scale} L ${x+20*scale} ${y+37*scale}"/></g>`;
  const label=(x,y,s,at=0,color=C.pale,size=22)=>G(at,T(x,y,s,size,color,'middle',600));
  const titleLine=(s)=>T(150,305,s,31,C.gold,'start',600,'letter-spacing="2"');

  function sceneMarkup(scene){
    let z='';
    switch(scene.kind){
      case 'year-thread': {
        z+=titleLine('四个年份之间，问题如何传递');
        const nodes=[
          [270,548,'1921','组织实践','circle'],[700,560,'1927','道路调整','rect'],
          [1165,540,'1929','队伍建设','diamond'],[1660,552,'1935','决策调整','ring']
        ];
        z+=P('M250 560 C420 440 570 470 720 570 S1010 700 1160 545 S1450 420 1680 565',C.gold,7,.16);
        nodes.forEach((n,i)=>{const [x,y,yr,cap,shape]=n;let icon=shape==='circle'?Cc(x,y,52,C.red,C.gold,3):shape==='rect'?R(x-49,y-49,98,98,C.panel2,C.gold,3,12):shape==='diamond'?`<path d="M${x} ${y-58} L${x+58} ${y} L${x} ${y+58} L${x-58} ${y} Z" fill="${C.red}" stroke="${C.gold}" stroke-width="3"/>`:`${Cc(x,y,57,'none',C.gold,3)}${Cc(x,y,45,C.red,C.gold,2)}`;z+=G([.02,.08,.14,.2][i],icon+T(x,y+10,yr,27,C.pale,'middle',700)+T(x,y+94,cap,22,C.muted));});
        z+=P('M270 730 H1650',C.red2,2,.84,'4 14')+T(960,785,'路径连接的是问题演变，不代表历史必然路线',22,C.muted);break;
      }
      case 'evidence-layers': {
        z+=titleLine('先分清材料、归纳与示意');
        z+=G(.05,`${R(300,405,490,305,C.paper,'#B9A98F',3,3)}${R(328,433,434,250,'none','#C7B99F',1)}${T(360,470,'可核验材料',25,C.red,'start',700)}${P('M360 502 H725',C.gold,3,.08)}${[0,1,2,3,4].map(i=>R(360,530+i*26,330-(i%3)*32,4,'#958671')).join('')}`);
        z+=G(.34,`${R(850,435,340,250,C.panel2,C.gold,2,2)}${P('M900 495 H1140',C.red2,5,.35)}${T(1020,550,'本片归纳',30,C.pale,'middle',650)}${T(1020,600,'解释关系',22,C.muted)}`);
        z+=G(.66,`${R(1280,390,330,320,'none',C.gold,2,4)}${P('M1340 620 L1450 500 L1545 570',C.gold,4,.67,'10 10')}${Cc(1340,620,9,C.red2,'none',0)}${Cc(1450,500,9,C.red2,'none',0)}${Cc(1545,570,9,C.red2,'none',0)}${T(1445,665,'结构示意',23,C.pale)}`);
        z+=P('M790 555 H845',C.red2,3,.26)+P('M1190 555 H1270',C.red2,3,.6);break;
      }
      case 'inquiry-path': {
        z+=titleLine('从问题，到选择，再到实践');
        z+=P('M300 670 C470 670 500 470 690 470 S900 670 1080 670 S1320 470 1600 470',C.gold,6,.04);
        const q=[['01','面对什么困难',330,665],['02','作出什么选择',930,665],['03','怎样检验调整',1535,465]];
        q.forEach((a,i)=>{const [n,s,x,y]=a;z+=G([.08,.27,.46][i],`${Cc(x,y,57,i===1?C.red:C.panel,C.gold,3)}${T(x,y+9,n,20,C.gold,'middle',700)}${T(x,y+112,s,27,C.pale,'middle',600)}`)});
        z+=T(960,800,'节点之后仍有实践',21,C.muted);break;
      }
      case 'social-strata': {
        z+=titleLine('制度更替之后，现实问题仍然存在');
        z+=G(.04,`${P('M250 430 C560 390 650 465 930 420 S1380 380 1660 440',C.gold,3,.06)}${P('M250 540 C560 500 700 580 970 535 S1380 500 1660 555',C.gold,3,.07)}${P('M250 650 C560 610 700 690 970 645 S1380 610 1660 665',C.gold,3,.08)}`);
        z+=G(.18,`${R(300,380,350,80,C.panel2,C.gold,2,40)}${T(475,432,'共和制度出现',27,C.pale)}`);
        z+=G(.4,`${R(720,495,380,80,C.panel2,C.red2,2,4)}${T(910,547,'政治秩序仍不稳定',25,C.pale)}`);
        z+=G(.47,`${R(1190,610,400,80,C.panel2,C.gold,2,40)}${T(1390,662,'经济艰难 · 外来压力',24,C.pale)}`);
        z+=P('M530 716 H1390',C.red2,2,.87,'5 13')+T(960,785,'改朝换代，并未自动给出解决办法',22,C.muted);break;
      }
      case 'exploration-spectrum': {
        z+=titleLine('不同探索，各自回应时代之问');
        // Four deliberately different marks: factory, scroll, republic seal, and open book.
        z+=G(.05,`${R(260,470,260,210,'none',C.gold,3)}${P('M285 470 V405 L350 440 V385 L425 430 V360 L495 405 V470',C.gold,4,.07)}${R(295,495,35,100,C.red2)}${R(350,510,38,85,C.panel2,C.gold,2)}${T(390,745,'洋务运动',24,C.pale)}`);
        z+=G(.2,`${P('M660 405 Q840 355 850 490 Q840 610 660 570 Z',C.gold,4,.21)}${P('M690 430 Q790 410 815 455 M690 470 Q790 450 815 495 M690 510 Q770 500 800 520',C.red2,3,.22)}${T(755,745,'维新变法',24,C.pale)}`);
        z+=G(.36,`${Cc(1110,500,106,C.red,C.gold,4)}${P('M1010 500 H1210 M1110 400 V600',C.pale,2,.38)}${T(1110,512,'共和',31,C.pale,'middle',700)}${T(1110,745,'辛亥革命',24,C.pale)}`);
        z+=G(.52,`${P('M1380 422 Q1490 380 1605 422 V605 Q1495 565 1380 605 Z',C.gold,4,.54)}${P('M1490 410 V584 M1405 455 H1470 M1510 455 H1580 M1405 490 H1470 M1510 490 H1580',C.pale,2,.56)}${T(1490,745,'新文化运动',24,C.pale)}`);
        z+=T(960,815,'参与者、目标与方式不同，共同呈现持续的问题',21,C.muted);break;
      }
      case 'may-fourth-gathering': {
        z+=titleLine('公共议题让分散的社会力量发生联系');
        for(let i=0;i<5;i++)z+=G(.06+i*.025,person(300+i*65,510+(i%2)*24,.85,C.pale));
        for(let i=0;i<5;i++)z+=G(.22+i*.025,person(1290+i*65,510+(i%2)*24,.85,C.gold));
        z+=G(.21,`${P('M650 520 C760 460 850 460 930 520',C.red2,5,.22)}${P('M990 520 C1080 460 1160 460 1270 520',C.red2,5,.3)}`);
        z+=G(.38,`${R(720,385,480,250,C.paper,C.gold,3,4)}${R(770,430,380,155,'none','#B9A98F',1)}${T(960,500,'五四运动',40,C.red,'middle',700)}${T(960,550,'爱国行动 · 公共议题',23,C.ink)}`);
        z+=G(.72,`${R(510,700,900,58,C.panel2,C.gold,2,3)}${T(960,738,'学生行动   →   工人响应   →   运动范围扩大',23,C.pale)}`);break;
      }
      case 'idea-publication': {
        z+=titleLine('早期组织需要稳定联络和持续工作');
        z+=G(.04,`${P('M300 430 H730 V730 H300 Z',C.gold,3,.05)}${P('M340 485 H680 M340 525 H640 M340 565 H690 M340 605 H620',C.pale,3,.08)}${T(515,685,'印刷与传播',22,C.muted)}`);
        z+=G(.25,`${P('M755 535 C850 420 900 690 1000 535 S1140 420 1210 535',C.red2,7,.28)}${T(980,455,'思想交流',22,C.gold)}`);
        z+=G(.52,`${R(1280,420,330,255,C.panel2,C.gold,3,8)}${Cc(1445,490,30,C.red2,C.gold,2)}${P('M1360 565 H1530 M1360 605 H1510 M1360 645 H1470',C.pale,3,.56)}${T(1445,715,'工人运动',23,C.pale)}`);
        z+=G(.78,`${P('M700 780 H1280',C.gold,3,.8,'8 12')}${T(960,820,'重要思想线索，不代表所有参与者立场相同',19,C.muted)}`);break;
      }
      case 'context-confluence': {
        z+=titleLine('社会环境、思想传播、组织实践交织');
        z+=P('M300 410 C600 410 600 560 930 560',C.red2,6,.05);
        z+=P('M300 560 H930',C.gold,6,.28);
        z+=P('M300 710 C600 710 600 560 930 560',C.green,6,.5);
        z+=G(.56,`${Cc(1110,560,128,C.panel,C.gold,4)}${Cc(1110,560,92,'none',C.red2,3)}${T(1110,548,'全国性',27,C.pale,'middle',600)}${T(1110,588,'组织',27,C.pale,'middle',600)}`);
        z+=G(.86,`${P('M1240 560 H1510',C.gold,5,.88)}${R(1510,465,220,190,C.paper,C.gold,3,4)}${T(1620,540,'1921',33,C.red,'middle',700)}${T(1620,585,'会议条件',22,C.ink)}`);
        z+=T(530,390,'社会环境',23,C.pale,'start')+T(530,550,'思想传播',23,C.pale,'start')+T(530,735,'组织实践',23,C.pale,'start');break;
      }
      case 'shikumen-address': {
        z+=titleLine('一处城市民居，成为会议开幕地点');
        z+=G(.03,`${P('M450 760 H1470 M535 760 V450 H1385 V760',C.gold,5,.04)}${P('M535 450 L660 350 H1260 L1385 450',C.gold,5,.08)}${P('M690 450 V405 H1230 V450',C.gold,3,.1)}`);
        z+=G(.27,`${R(760,480,400,280,C.panel,C.gold,4,5)}${P('M960 480 V760 M760 575 H1160',C.gold,3,.3)}${Cc(1115,620,7,C.gold,'none',0)}`);
        z+=G(.56,`${R(250,405,310,112,C.panel2,C.red2,2,5)}${T(405,450,'望志路 106 号',24,C.pale)}${T(405,489,'1921 年',20,C.gold)}`);
        z+=G(.74,`${R(1360,405,310,112,C.panel2,C.gold,2,5)}${T(1515,450,'兴业路 76 号',24,C.pale)}${T(1515,489,'今天地址',20,C.gold)}`);
        z+=T(960,820,'石库门民居示意 · 非历史照片',20,C.muted);break;
      }
      case 'delegate-count': {
        z+=titleLine('把不同计数口径分开看');
        z+=G(.04,`${T(470,390,'正式代表',23,C.gold)}${Array.from({length:12},(_,i)=>person(330+(i%4)*88,470+Math.floor(i/4)*98,.55,C.pale)).join('')}${T(470,735,'12 人',38,C.pale,'middle',700)}`);
        z+=G(.3,`${P('M670 540 H835',C.red2,4,.31)}${Cc(900,540,55,C.red,C.gold,3)}${T(900,551,'+1',26,C.pale,'middle',700)}${T(900,650,'包惠僧',23,C.pale)}`);
        z+=G(.5,`${T(1180,390,'代表全国 50 多名党员',24,C.gold)}${Array.from({length:50},(_,i)=>Cc(1010+(i%10)*38,445+Math.floor(i/10)*38,7,i%7===0?C.red2:C.gold,'none',0)).join('')}${T(1200,675,'13 名中国参会者',28,C.pale,'middle',650)}`);
        z+=G(.5,`${Cc(1510,485,28,C.panel,C.gold,2)}${Cc(1590,485,28,C.panel,C.gold,2)}${T(1550,570,'另有 2 位共产国际代表',20,C.muted)}`);
        z+=T(960,805,'12 名正式代表；计入包惠僧后，中国参会者共 13 人',20,C.muted);break;
      }
      case 'congress-decisions': {
        z+=titleLine('大会形成名称、纲领与组织安排');
        z+=G(.04,`${P('M520 370 H1320 L1430 480 V765 H520 Z',C.gold,3,.05)}${P('M1320 370 V480 H1430',C.gold,3,.08)}${T(650,440,'大会决定',24,C.red,'start',700)}${P('M650 465 H1280',C.gold,2,.1)}`);
        const lines=[['名称','中国共产党'],['纲领与决议','形成共同政治主张'],['中央局','选举产生领导机构']];
        lines.forEach((r,i)=>{const y=535+i*76;z+=G([.16,.33,.5][i],`${Cc(675,y-8,8,C.red2,'none',0)}${T(720,y,r[0],24,C.red,'start',650)}${T(970,y,r[1],25,C.ink,'start',500)}${P(`M700 ${y+20} H1300`,'#B8AA91',1,.18+i*.17)}`)});
        z+=T(960,815,'解释结构示意，不是大会原有图表',20,C.muted);break;
      }
      case 'shanghai-jiaxing': {
        z+=titleLine('会议地点从上海转到嘉兴南湖');
        z+=G(.06,`${R(250,430,380,250,C.panel2,C.gold,3,6)}${P('M330 620 V525 H550 V620 M310 525 L440 450 L570 525',C.gold,3,.08)}${T(440,715,'上海会址',28,C.pale)}`);
        z+=G(.18,`${P('M650 560 C760 485 850 485 960 560',C.red2,7,.2,'14 10')}${Cc(960,560,12,C.red2,C.pale,2)}${T(960,500,'地点转移',21,C.gold)}`);
        z+=G(.22,`${P('M1160 610 Q1390 690 1640 610',C.gold,4,.24)}${P('M1170 655 Q1390 735 1630 655 M1210 700 Q1400 760 1590 700',C.red2,2,.26)}${Cc(1440,560,13,C.red2,C.pale,2)}${T(1440,510,'嘉兴南湖',28,C.pale)}${T(1440,790,'会址地点',21,C.gold)}`);
        z+=T(960,812,'地点关系示意 · 不按比例地图',20,C.muted);break;
      }
      case 'work-after-congress': {
        z+=titleLine('共同方向，进入各地的具体工作');
        z+=G(.04,`${R(765,350,390,98,C.paper,C.gold,3,7)}${T(960,410,'共同纲领与决议',27,C.red,'middle',650)}`);
        z+=P('M960 448 V545 M380 545 H1540 M380 545 V610 M770 545 V610 M1150 545 V610 M1540 545 V610',C.gold,4,.12);
        const tasks=[['联系成员','点状联络'],['宣传主张','刊物与讲解'],['工人工作','工会与组织'],['持续建设','地方实践']];
        tasks.forEach((r,i)=>{const x=380+i*387;const co=i===1?C.red2:C.gold;z+=G(.28+i*.16,`${Cc(x,650,47,C.panel2,co,3)}${T(x,658,String(i+1).padStart(2,'0'),20,C.pale,'middle',700)}${T(x,735,r[0],23,C.pale,'middle',600)}${T(x,772,r[1],18,C.muted)}`)});
        z+=T(960,825,'各地条件不同，具体工作不能完全照搬',20,C.muted);break;
      }
      case 'boat-symbol': {
        z+=titleLine('红船是后来形成的纪念象征');
        z+=G(.05,`${P('M430 570 Q600 545 770 570 L855 660 H520 Z',C.gold,4,.07)}${P('M600 560 V385 L760 545 H600',C.red2,5,.2)}${P('M530 665 Q800 630 1060 665 M610 715 Q850 685 1100 715 M770 765 Q1000 740 1250 765',C.gold,3,.35)}`);
        z+=G(.6,`${R(1130,440,470,135,C.panel2,C.red2,2,5)}${T(1365,494,'纪念船意象',29,C.pale)}${T(1365,540,'非 1921 年原船',22,C.gold)}`);
        z+=T(960,820,'用于纪念与回望，不作为历史现场影像',20,C.muted);break;
      }
      case '1927-crisis': {
        z+=titleLine('形势变化，行动方向需要重新判断');
        z+=G(.03,`${P('M300 430 H720 V740 H300 Z',C.red2,3,.04)}${P('M340 475 H680 M340 530 H680 M340 585 H610',C.gold,4,.08)}${T(510,700,'城市工作受挫',23,C.pale)}`);
        z+=G(.28,`${P('M720 585 C850 585 830 470 960 470',C.red2,6,.29)}${P('M720 585 C850 585 830 700 960 700',C.gold,6,.3)}${Cc(720,585,16,C.paper,C.gold,3)}`);
        z+=G(.58,`${P('M1000 720 L1120 590 L1240 720 M1210 720 L1350 520 L1490 720 M1460 720 L1580 610 L1700 720',C.green,5,.6)}${T(1350,785,'农村与山区',25,C.pale)}`);
        z+=G(.42,`${R(970,385,270,72,C.panel2,C.red2,2,4)}${T(1105,431,'8 月 1 日 · 南昌起义',21,C.pale)}`);
        z+=T(960,825,'重要转向，探索仍在继续',20,C.muted);break;
      }
      case 'three-stops': {
        z+=titleLine('文家市、三湾、井冈山：三个不同节点');
        z+=P('M300 640 C560 640 670 510 900 510 S1240 690 1610 520',C.gold,5,.04);
        z+=G(.1,`${R(240,420,350,170,C.paper,C.gold,3,2)}${T(415,470,'9 月 19 日',25,C.red,'middle',700)}${T(415,525,'文家市会议',26,C.ink,'middle',600)}${T(415,565,'决定转向',20,C.ink)}`);
        z+=G(.28,`${Cc(945,518,75,C.red,C.gold,3)}${T(945,510,'9 月 29 日',22,C.pale,'middle',650)}${T(945,550,'三湾改编',21,C.pale)}`);
        z+=G(.48,`${P('M1320 670 L1480 470 L1640 670 Z',C.green,4,.5)}${Cc(1480,470,12,C.gold,'none',0)}${T(1480,715,'10 月 27 日',23,C.gold)}${T(1480,756,'抵达井冈山茨坪',22,C.pale)}`);
        z+=T(960,820,'先讨论去向，再整顿队伍，继而寻找立足点',20,C.muted);break;
      }
      case 'sanwan-reorganization': {
        z+=titleLine('把组织联系落实到基层单位');
        z+=G(.02,`${R(330,410,380,245,'none',C.gold,2,5)}${Cc(450,490,16,C.red2,'none',0)}${Cc(550,555,16,C.gold,'none',0)}${Cc(650,465,16,C.gold,'none',0)}${P('M450 490 L550 555 L650 465',C.muted,2,.04,'6 9')}${T(520,700,'改编前：联系分散',20,C.muted)}`);
        z+=P('M740 530 H920',C.red2,5,.24);
        z+=G(.34,`${R(930,405,590,70,C.panel2,C.gold,2,3)}${T(1225,451,'队伍组织',24,C.pale)}${P('M1225 475 V550 M1035 550 H1415 M1035 550 V610 M1225 550 V610 M1415 550 V610',C.gold,3,.38)}`);
        z+=G(.42,`${R(940,610,190,86,C.paper,C.red2,3,5)}${R(1130,610,190,86,C.paper,C.gold,3,5)}${R(1325,610,190,86,C.paper,C.gold,3,5)}${T(1035,664,'连队',24,C.ink)}${T(1225,664,'连队',24,C.ink)}${T(1420,664,'连队',24,C.ink)}`);
        z+=G(.52,`${R(1105,715,240,66,C.red,C.gold,2,28)}${T(1225,757,'党支部建在连上',20,C.pale)}`);
        z+=T(960,825,'组织关系示意，不等同于完整编制图',19,C.muted);break;
      }
      case 'rural-conditions': {
        z+=titleLine('根据地建设受多种现实条件影响');
        z+=G(.02,`${P('M180 760 L360 610 L515 700 L690 500 L850 660 L1030 450 L1190 670 L1370 530 L1570 700 L1760 590',C.green,6,.04)}${P('M200 790 C530 730 800 800 1120 750 S1500 775 1740 720',C.gold,2,.06,'7 12')}`);
        const conditions=[['地方社会',300,430],['交通条件',690,380],['群众基础',1110,385],['军事压力',1510,450]];
        conditions.forEach((a,i)=>{const [s,x,y]=a;z+=G(.14+i*.12,`${P(`M${x} ${y+35} L${x} ${530+i%2*36}`,i===3?C.red2:C.gold,2,.16+i*.12)}${Cc(x,y,48,C.panel2,i===3?C.red2:C.gold,3)}${T(x,y+7,String(i+1).padStart(2,'0'),18,C.pale,'middle',700)}${T(x,y+92,s,22,C.pale)}`)});
        z+=T(960,825,'交通、补给与地方工作条件，不作数字化虚构',19,C.muted);break;
      }
      case 'open-ended-route': {
        z+=titleLine('没有预先写好的完整路线图');
        z+=G(.02,`${P('M180 700 C360 670 370 480 590 500 S820 690 1010 590 S1280 435 1450 525 S1640 670 1850 420',C.gold,8,.03)}${P('M250 758 C430 730 450 600 620 608 M1040 650 C1220 580 1280 560 1440 600',C.red2,2,.08,'5 13')}`);
        [[260,686,'观察'],[590,500,'选择'],[1010,590,'实践'],[1450,525,'再判断']].forEach((a,i)=>{z+=G(.15+i*.17,`${Cc(a[0],a[1],14,i===2?C.red2:C.paper,C.gold,2)}${T(a[0],a[1]-34,a[2],21,C.pale)}`)});
        z+=G(.82,`${P('M1725 470 L1850 420 L1770 540',C.gold,5,.85)}`);
        z+=T(960,810,'线条向画面外延伸：实践继续，结果并非当时已知',20,C.muted);break;
      }
      case 'gutian-setting': {
        z+=titleLine('古田会议面对具体队伍建设问题');
        z+=G(.02,`${P('M210 720 L440 650 L595 690 L770 620 L930 705 L1105 625 L1265 680 L1460 610 L1710 700',C.green,5,.05)}${P('M480 675 L650 540 L820 675',C.gold,4,.12)}${P('M1370 675 L1510 535 L1650 675',C.gold,4,.14)}`);
        z+=G(.28,`${R(790,445,360,218,C.panel2,C.gold,3,4)}${P('M840 490 H1100 M840 535 H1080 M840 580 H1040',C.pale,3,.3)}${T(970,625,'会议记录',22,C.gold)}`);
        z+=G(.53,`${R(350,520,230,140,C.panel,C.red2,2,4)}${T(465,575,'转移',24,C.pale)}${T(465,615,'与战斗',20,C.muted)}${R(1340,520,230,140,C.panel,C.gold,2,4)}${T(1455,575,'物资',24,C.pale)}${T(1455,615,'紧张',20,C.muted)}`);
        z+=G(.77,`${person(700,700,.7,C.gold)}${person(1210,700,.7,C.pale)}${T(960,800,'成员经历与认识并不完全相同',21,C.muted)}`);break;
      }
      case 'problems-to-principles': {
        z+=titleLine('从偏差问题，转向可落实的建设工作');
        const problems=['单纯军事观点','极端民主化','流寇思想'];
        problems.forEach((s,i)=>{const y=420+i*93;z+=G(.03+i*.1,`${P(`M300 ${y} H620 L670 ${y+25} H760`,C.red2,5,.04+i*.1)}${T(320,y-12,s,22,C.pale,'start',600)}`)});
        z+=G(.4,`${R(790,445,240,230,C.paper,C.gold,3,3)}${T(910,505,'决议',33,C.red,'middle',700)}${P('M835 535 H985 M835 568 H985 M835 601 H965','#B7A88E',2,.42)}`);
        z+=P('M1030 560 H1135 M1135 385 V730',C.gold,4,.3);
        const responses=[['思想教育',385],['组织建设',545],['政治工作',705]];
        responses.forEach((a,i)=>{z+=G(.3+i*.08,`${P(`M1135 ${a[1]} H1290`,C.gold,3,.32+i*.08)}${R(1290,a[1]-40,350,80,i===1?C.red:C.panel2,C.gold,2,2)}${T(1465,a[1]+9,a[0],24,C.pale)}`)});
        z+=T(960,817,'回应关系为讲解结构，不是一一对应的原文图表',19,C.muted);break;
      }
      case 'daily-organization': {
        z+=titleLine('原则要进入组织生活和日常工作');
        z+=G(.03,`${P('M440 390 H1260 L1340 470 V770 H440 Z',C.gold,3,.04)}${P('M1260 390 V470 H1340',C.gold,3,.08)}${T(520,445,'工作台账',22,C.gold,'start',600)}`);
        const rows=[['思想教育','经常开展'],['组织生活','持续进行'],['纪律建设','融入日常']];
        rows.forEach((a,i)=>{let y=520+i*75;z+=G([.1,.27,.44][i],`${Cc(540,y-8,7,C.red2,'none',0)}${T(590,y,a[0],25,C.pale,'start',600)}${P(`M920 ${y-8} H${1250-i*45}`,'#877868',2,.12+i*.17)}${T(1280,y,a[1],20,C.muted,'end')}`)});
        z+=G(.84,`${R(700,790,520,40,C.red2,'none',0,20)}${T(960,818,'让原则进入队伍运行',19,C.pale)}`);break;
      }
      case 'task-evolution': {
        z+=titleLine('历史任务随阶段变化');
        z+=G(.04,`${Cc(460,565,133,'none',C.gold,3)}${Cc(460,565,90,'none',C.red2,2)}${T(460,550,'建立',25,C.pale)}${T(460,592,'组织',25,C.pale)}${T(460,750,'1921',22,C.gold,'middle',700)}`);
        z+=G(.35,`${P('M620 565 C700 430 775 430 850 565 M620 565 C700 700 775 700 850 565',C.gold,4,.37)}${P('M700 510 L770 565 L700 620',C.red2,5,.4)}${T(740,750,'1927',22,C.gold,'middle',700)}`);
        z+=G(.36,`${R(930,450,540,230,'none',C.gold,3,2)}${R(1000,500,140,130,C.panel2,C.gold,2,4)}${R(1160,500,140,130,C.panel2,C.red2,2,4)}${R(1320,500,100,130,C.panel2,C.gold,2,4)}${T(1200,750,'1929',22,C.gold,'middle',700)}`);
        z+=P('M590 800 H1510',C.red2,2,.88,'4 12')+T(960,830,'组织建立 → 行动调整 → 队伍建设',20,C.muted);break;
      }
      case 'continuing-practice': {
        z+=titleLine('决定提出方向，实践继续检验');
        z+=G(.03,`${P('M350 420 H1130 L1230 520 V740 H350 Z',C.gold,3,.05)}${P('M1130 420 V520 H1230',C.gold,3,.08)}${T(470,485,'会议决议',24,C.gold,'start',650)}${P('M470 520 H1080',C.gold,2,.1)}${P('M470 565 H1020 M470 610 H1080 M470 655 H950','#948571',3,.12)}`);
        z+=G(.52,`${P('M1230 570 C1390 520 1460 500 1610 510',C.red2,5,.54)}${P('M1230 625 C1390 675 1460 700 1610 690',C.gold,5,.57)}${T(1580,475,'现实检验',22,C.pale)}${T(1580,735,'新的问题',22,C.pale)}`);
        z+=T(960,815,'会议不是让所有问题在一次讨论后消失',20,C.muted);break;
      }
      case 'longmarch-pressure': {
        z+=titleLine('行动条件收窄，既有判断受到检验');
        z+=G(.02,`${P('M260 420 H1660',C.gold,2,.03)}${P('M260 780 H1660',C.gold,2,.05)}${P('M300 465 C700 465 850 530 1160 590 L1610 620',C.red2,9,.1)}${P('M300 735 C700 735 850 670 1160 630 L1610 660',C.red2,9,.25)}`);
        z+=G(.12,`${R(390,505,310,140,C.panel2,C.gold,2,4)}${T(545,557,'1934 年 10 月',23,C.gold)}${T(545,605,'开始长征',27,C.pale)}`);
        z+=G(.35,`${P('M850 545 L920 610 M930 540 L1000 605 M1010 535 L1080 600',C.red2,8,.37)}${T(970,690,'突破封锁',21,C.pale)}`);
        z+=G(.46,`${R(1250,500,335,150,'none',C.red2,2,4)}${T(1417,558,'湘江战役',23,C.pale)}${T(1417,604,'重大损失',22,C.red2)}`);
        z+=T(960,820,'不虚构伤亡数字：以路径收窄呈现行动压力',19,C.muted);break;
      }
      case 'zunyi-decisions': {
        z+=titleLine('会议处理军事与组织方面的关键问题');
        z+=G(.03,`${R(600,365,720,92,C.paper,C.gold,3,4)}${T(960,424,'遵义 · 1935 年 1 月 15—17 日',28,C.red,'middle',650)}`);
        z+=G(.26,`${R(700,500,520,220,C.panel2,C.gold,3,4)}${T(960,555,'第五次反“围剿”',27,C.pale)}${T(960,600,'经验教训',27,C.gold)}${P('M790 635 H1130',C.red2,3,.3)}`);
        const acts=[['领导安排','增选毛泽东为中央政治局常委'],['决议起草','委托张闻天起草决议'],['指挥机制','取消长征前成立的“三人团”']];
        acts.forEach((a,i)=>{let y=390+i*130;z+=G(.43+i*.17,`${P(`M1230 ${y+35} H1390`,C.gold,3,.45+i*.17)}${R(1390,y,360,80,i===1?C.red:C.panel,C.gold,2,3)}${T(1570,y+32,a[0],20,C.gold)}${T(1570,y+59,a[1],18,C.pale)}`)});
        z+=T(960,805,'逐项呈现会议决定，不概括为“全面改组”',19,C.muted);break;
      }
      case 'decisions-after-meeting': {
        z+=titleLine('会中决定与会后调整分开呈现');
        z+=G(.03,`${R(275,410,350,272,C.panel2,C.gold,3,6)}${T(450,475,'1 月 15—17 日',23,C.gold)}${T(450,530,'遵义会议',30,C.pale)}${T(450,600,'形成决定',22,C.muted)}`);
        z+=P('M650 545 H810',C.red2,5,.12);
        z+=G(.18,`${P('M840 455 V735',C.gold,3,.2)}${Cc(840,485,13,C.red2,C.pale,2)}${T(900,493,'2 月初',24,C.gold,'start',650)}${T(900,535,'常委分工发生变化',23,C.pale,'start')}`);
        z+=G(.42,`${Cc(840,675,13,C.red2,C.pale,2)}${T(900,683,'3 月',24,C.gold,'start',650)}${T(900,725,'成立新的三人军事指挥小组',23,C.pale,'start')}`);
        z+=G(.83,`${P('M1330 560 H1690',C.gold,3,.85,'7 10')}${T(1510,520,'行动仍在继续',20,C.muted)}`);break;
      }
      case 'route-continues': {
        z+=titleLine('转折开启新的阶段，并未让长征停止');
        z+=G(.02,`${P('M250 610 C520 610 600 500 850 500 S1170 690 1420 620 S1660 535 1850 520',C.gold,7,.04)}`);
        z+=G(.18,`${Cc(430,590,53,C.red,C.gold,3)}${T(430,598,'遵义',22,C.pale,'middle',600)}${T(430,700,'新阶段',20,C.gold)}`);
        z+=G(.42,`${R(760,435,320,130,C.panel,C.gold,2,4)}${T(920,490,'独立处理',24,C.pale)}${T(920,530,'实际问题',24,C.pale)}`);
        z+=G(.65,`${R(1260,620,375,105,C.panel2,C.red2,2,4)}${T(1447,665,'领导与指挥继续调整',21,C.pale)}`);
        z+=G(.85,`${P('M1640 620 H1850',C.gold,4,.87,'7 10')}${T(1760,690,'长征继续',18,C.muted)}`);
        z+=T(960,810,'历史转折是过程，不是终点',21,C.muted);break;
      }
      case 'three-lenses': {
        z+=titleLine('回看历史：三个观察角度');
        z+=G(.04,`${P('M380 620 C420 400 690 375 810 555 C690 740 420 735 380 620 Z',C.gold,4,.06)}${T(590,585,'放回当时',25,C.pale)}${T(590,625,'社会条件',21,C.muted)}`);
        z+=G(.36,`${P('M790 555 C920 365 1160 400 1210 595 C1160 780 930 770 790 625 Z',C.red2,4,.38)}${T(1000,585,'看组织',25,C.pale)}${T(1000,625,'如何行动',21,C.muted)}`);
        z+=G(.68,`${P('M1180 595 C1300 390 1550 430 1610 610 C1550 770 1300 785 1180 625 Z',C.gold,4,.7)}${T(1405,585,'检验实践',25,C.pale)}${T(1405,625,'再作判断',21,C.muted)}`);
        z+=P('M680 686 C870 740 1100 740 1310 680',C.gold,2,.85,'5 12');break;
      }
      case 'source-boundary': {
        z+=titleLine('史实、分析和示意需要明确标注');
        z+=G(.03,`${R(270,380,950,385,C.paper,'#B9A98F',3,2)}${R(305,415,880,315,'none','#C7B99F',1,0)}${R(310,415,10,315,C.red2,'none',0)}${T(370,470,'复核记录',23,C.red,'start',700)}${P('M370 500 H1120','#B7A88F',2,.07)}${T(390,565,'日期',24,C.ink,'start',600)}${P('M520 558 H1060','#958671',2,.1)}${T(390,620,'文献',24,C.ink,'start',600)}${P('M520 613 H1020','#958671',2,.12)}${T(390,675,'语境',24,C.ink,'start',600)}${P('M520 668 H1090','#958671',2,.14)}`);
        z+=G(.42,`${P('M1245 405 V745',C.gold,3,.44)}${T(1340,455,'事实',24,C.pale,'start',650)}${T(1340,520,'本片归纳',24,C.gold,'start',650)}${T(1340,585,'结构示意',24,C.pale,'start',650)}${P('M1300 470 H1680 M1300 535 H1640 M1300 600 H1700','#8B7B68',2,.46)}`);
        z+=G(.78,`${R(1305,665,370,70,C.panel2,C.red2,2,4)}${T(1490,708,'解释不冒充原始材料',20,C.pale)}`);break;
      }
      case 'closing-arc': {
        z+=titleLine('从石库门到遵义，回到探索的过程');
        z+=G(.02,`${P('M360 540 C500 430 620 430 760 540 S1020 650 1160 540 S1430 430 1560 540',C.gold,6,.03)}`);
        const years=[['1921',400,520],['1927',720,520],['1929',1120,560],['1935',1525,510]];
        years.forEach((a,i)=>{z+=G(.02+i*.1,`${Cc(a[1],a[2],38,i===0?C.red:C.panel2,C.gold,3)}${T(a[1],a[2]+8,a[0],20,C.pale,'middle',700)}`)});
        z+=G(.78,`${T(960,710,'在实践中不断探索',51,C.pale,'middle',700)}${P('M630 750 H1290',C.red2,3,.83)}`);
        z+=T(960,805,'感谢收看《光影党史》',21,C.muted);break;
      }
      default: z=T(960,550,'',24,C.pale);break;
    }
    return `<defs><marker id="m6-arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0 0 L10 5 L0 10 Z" fill="${C.gold}"/></marker></defs>${z}`;
  }

  let mountedId='',animated=[];
  function mount(scene){
    art.innerHTML=sceneMarkup(scene);
    mountedId=scene.id;
    animated=[...art.querySelectorAll('[data-reveal]')].map(node=>({node,at:Number(node.getAttribute('data-reveal'))||0}));
    for(const node of art.querySelectorAll('[data-draw]')){
      try{const length=node.getTotalLength();node.style.strokeDasharray=String(length);node.dataset.drawLength=String(length);animated.push({node,at:Number(node.getAttribute('data-draw'))||0,draw:true,length});}catch{}
    }
  }
  function apply(p){
    for(const item of animated){
      const progress=clamp((p-item.at)/(item.draw?.2:.055));
      if(item.draw)item.node.style.strokeDashoffset=String(item.length*(1-progress));
      else item.node.style.opacity=String(progress);
    }
  }
  function find(list,t,key='end'){
    let lo=0,hi=list.length-1;while(lo<hi){const mid=(lo+hi)>>1;if(list[mid][key]<=t)lo=mid+1;else hi=mid;}return list[lo];
  }
  function updateCaption(value){
    const a=document.getElementById('caption-a'),b=document.getElementById('caption-b');
    const chars=Array.from(String(value||'').replace(/[\r\n]+/g,' '));let first=chars,second=[];
    if(chars.length>43){let split=43;for(let i=31;i<=43;i++)if('，。；：！？、'.includes(chars[i-1]))split=i;first=chars.slice(0,split);second=chars.slice(split);}
    a.textContent=first.join('');b.textContent=second.join('');b.style.display=second.length?'':'none';
    a.setAttribute('y',second.length?'910':'925');b.setAttribute('y','948');
  }
  function renderAt(t){
    if(!Number.isFinite(t))t=0;t=clamp(t,0,M.duration_seconds-.001);
    const scene=find(S,t),caption=find(SH,t),chapter=CH.find(c=>c.id===caption.chapter)||CH[0];
    if(scene.id!==mountedId)mount(scene);
    const p=clamp((t-scene.start)/Math.max(.001,scene.end-scene.start));
    apply(p);titleNode.textContent=chapter.title;const number=document.getElementById('chapter-number');if(number)number.textContent=`${chapter.id.slice(1).padStart(2,'0')} / 09`;updateCaption(caption.caption);
    const cover=document.getElementById('title-cover');
    if(cover){const fade=clamp((t-3.6)/.4);cover.style.opacity=String(1-fade*fade*(3-2*fade));}
    const contentFade=clamp((t-4)/.3),contentOpacity=contentFade*contentFade*(3-2*contentFade);
    art.style.opacity=String(contentOpacity);document.getElementById('interface').style.opacity=String(contentOpacity);
    const openingCover=t<4;
    for(const layer of [art,document.getElementById('interface')])for(const text of layer.querySelectorAll('text')){
      if(openingCover)text.setAttribute('data-layout-allow-occlusion','');
      else text.removeAttribute('data-layout-allow-occlusion');
    }
    const timer=document.getElementById('timecode');if(timer)timer.textContent=fmt(t);
    const prog=document.getElementById('progress-fill');if(prog)prog.setAttribute('width',String(1704*clamp(t/M.duration_seconds)));
    window.__currentScene=scene.id;window.__currentCaption=caption.id;return scene;
  }
  function fmt(t){return `${String(Math.floor(t/60)).padStart(2,'0')}:${String(Math.floor(t%60)).padStart(2,'0')}`;}
  window.renderAt=renderAt;
  window.montageRender=(i,p)=>renderAt(S[clamp(i|0,0,S.length-1)].start+(S[clamp(i|0,0,S.length-1)].end-S[clamp(i|0,0,S.length-1)].start)*clamp(p));
  renderAt(0);
})();
