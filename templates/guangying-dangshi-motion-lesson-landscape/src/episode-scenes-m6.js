/* M6 visual beats follow the unchanged M5 narration and ASR caption timing. */
(function(){
  const source=window.EP01_M5;
  const beats=[
    ['M6-01','S01-001','S01-005','year-thread'],
    ['M6-02','S02-001','S02-003','evidence-layers'],
    ['M6-03','S02-004','S02-005','inquiry-path'],
    ['M6-04','S03-001','S03-004','social-strata'],
    ['M6-05','S03-005','S03-008','exploration-spectrum'],
    ['M6-06','S03-009','S03-014','may-fourth-gathering'],
    ['M6-07','S03-015','S03-019','idea-publication'],
    ['M6-08','S03-020','S03-023','context-confluence'],
    ['M6-09','S04-001','S04-004','shikumen-address'],
    ['M6-10','S04-005','S04-008','delegate-count'],
    ['M6-11','S04-009','S04-013','congress-decisions'],
    ['M6-12','S04-014','S04-018','shanghai-jiaxing'],
    ['M6-13','S04-019','S04-023','work-after-congress'],
    ['M6-14','S04-024','S04-026','boat-symbol'],
    ['M6-15','S05-001','S05-005','1927-crisis'],
    ['M6-16','S05-006','S05-010','three-stops'],
    ['M6-17','S05-011','S05-015','sanwan-reorganization'],
    ['M6-18','S05-016','S05-020','rural-conditions'],
    ['M6-19','S05-021','S05-024','open-ended-route'],
    ['M6-20','S06-001','S06-004','gutian-setting'],
    ['M6-21','S06-005','S06-009','problems-to-principles'],
    ['M6-22','S06-010','S06-013','daily-organization'],
    ['M6-23','S06-014','S06-017','task-evolution'],
    ['M6-24','S06-018','S06-020','continuing-practice'],
    ['M6-25','S07-001','S07-004','longmarch-pressure'],
    ['M6-26','S07-005','S07-009','zunyi-decisions'],
    ['M6-27','S07-010','S07-013','decisions-after-meeting'],
    ['M6-28','S07-014','S07-019','route-continues'],
    ['M6-29','S08-001','S08-003','three-lenses'],
    ['M6-30','S08-004','S08-006','source-boundary'],
    ['M6-31','S09-001','S09-002','closing-arc']
  ];
  const byId=new Map(source.shots.map(shot=>[shot.id,shot]));
  window.EP01_M6={
    duration_seconds:source.duration_seconds,
    chapters:source.chapters,
    captions:source.shots,
    scenes:beats.map(([id,first,last,kind])=>{
      const start=byId.get(first),end=byId.get(last);
      if(!start||!end)throw new Error('M6 scene references a missing narration segment: '+id);
      return {id,kind,chapter:start.chapter,start:start.start,end:end.end,first,last};
    })
  };
})();
