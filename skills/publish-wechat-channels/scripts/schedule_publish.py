#!/usr/bin/env python3
"""Publish one queue record to WeChat Channels with a scheduled time, via agent-browser.

Usage:
  python3 schedule_publish.py <queue-id> "YYYY-MM-DD HH:00" [--dry]   # 新一条：上传→填表→定时→发表
  python3 schedule_publish.py <queue-id> "YYYY-MM-DD HH:00" --edit    # 从列表「修改并重新发表」进入后改定时
  python3 schedule_publish.py <queue-id> "YYYY-MM-DD HH:00" --go      # 表单已在浏览器里打开，只补定时并发表
  python3 ... --dry                                                   # 填到发表前一步停下，交人工核对

Prereq: debug Chrome already running and logged in (`bash launch_wechat_chrome.sh <create-url>`
+ `agent-browser connect 9333`); the record must exist in pipeline/publish-queue.json.

Learned contract (2026-10-14):
  * eval always runs in the TOP document; the form lives in the iframe whose
    contentDocument contains '发表' -> every snippet is wrapped in an IIFE
    (a bare `const` would collide with the previous eval's declaration).
  * dispatchEvent works for most controls, but the datetime picker needs
    TRUSTED input: `agent-browser mouse move/down/up` at the element's
    getBoundingClientRect centre (inner-doc CSS px == page CSS px).
  * setting the schedule input's value does NOT commit; only clicking
    day -> 时间 -> hour inside the open panel does. Verify by re-reading the
    inputs, and never publish when the read-back hour != requested hour.
  * hours earlier than ~now+2h are `weui-desktop-picker__disabled`; a scheduled
    post shows as 「将于YYYY年M月D日 HH:00发表」 in the video list until it fires.
"""
import fcntl
import json
import os
import subprocess
import sys
import time

REPO = "/Users/wrg/Important/uni-ai-video-productions"
LOCK_PATH = os.path.join(REPO, "pipeline", ".publish-browser.lock")

# 视频号发布只能单线操作：整个进程生命周期持有这把锁，第二个会话直接退出。
if "--lock-check" in sys.argv:
    _probe = open(LOCK_PATH, "a+")
    try:
        fcntl.flock(_probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
        print("FREE", flush=True)
    except BlockingIOError:
        _probe.seek(0)
        print("BUSY pid=%s" % (_probe.read().strip() or "?"), flush=True)
        sys.exit(3)
    sys.exit(0)

_LOCK = open(LOCK_PATH, "a+")
try:
    fcntl.flock(_LOCK, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    _LOCK.seek(0)
    print("SKIP 另一个发布正在进行（锁 %s 由 PID %s 持有：%s）"
          % (LOCK_PATH, _LOCK.read().strip() or "?", time.strftime("%H:%M:%S")), flush=True)
    sys.exit(3)
_LOCK.seek(0)
_LOCK.truncate()
_LOCK.write(str(os.getpid()))
_LOCK.flush()
GUARD = ("(function(){const FF=[...document.querySelectorAll('iframe')]"
         ".find(f=>{try{return f.contentDocument&&f.contentDocument.body"
         "&&f.contentDocument.body.innerText.includes('发表')}catch(e){return false}});"
         "if(!FF)throw new Error('no-form');const d=FF.contentDocument,w=d.defaultView;return (")


def ev(js, timeout=60):
    r = subprocess.run(["agent-browser", "eval", GUARD + js + ")})()"],
                       capture_output=True, text=True, cwd=REPO, timeout=timeout)
    return (r.stdout or r.stderr).strip()


def ab(*args, timeout=180):
    return subprocess.run(["agent-browser", *args], capture_output=True,
                          text=True, cwd=REPO, timeout=timeout).stdout.strip()


def mouse(x, y):
    ab("mouse", "move", str(x), str(y))
    ab("mouse", "down")
    ab("mouse", "up")
    time.sleep(0.6)


def dispatch(expr, label=""):
    js = ("(()=>{const e=%s;if(!e)return 'nf:%s';e.scrollIntoView({block:'center'});"
          "['mousedown','mouseup','click'].forEach(t=>e.dispatchEvent(new w.MouseEvent(t,"
          "{bubbles:true,cancelable:true,view:w})));return 'ok'})()" % (expr, label))
    return ev(js)


def setval(sel, value):
    js = ("(()=>{const i=d.querySelector(%s);if(!i)return 'nf';i.focus();"
          "Object.getPrototypeOf(i).__lookupSetter__('value').call(i,%s);"
          "i.dispatchEvent(new w.Event('input',{bubbles:true}));"
          "i.dispatchEvent(new w.Event('change',{bubbles:true}));return 'v='+i.value})()"
          % (json.dumps(sel), json.dumps(value)))
    return ev(js)


def rect(expr, scroll=True):
    if scroll:
        ev("(()=>{const e=%s;if(!e)return 'nf';e.scrollIntoView({block:'center'});return 'ok'})()" % expr)
        time.sleep(0.8)
    js = ("(()=>{const e=%s;if(!e)return '';const r=e.getBoundingClientRect();"
          "return JSON.stringify([Math.round(r.x+r.width/2),Math.round(r.y+r.height/2)])})()" % expr)
    out = ev(js)
    try:
        return json.loads(json.loads(out))
    except Exception:
        return None


def log(*a):
    print(*a, flush=True)


def form_ready():
    # 请选择发表时间 only exists once 定时 is selected, so gate on the row label + title input
    return "found" in ev("(()=>/定时发表/.test(d.body.innerText)&&[...d.querySelectorAll('input')].some(i=>/短标题/.test(i.placeholder))?'found':'wait')()")


def fresh_form():
    ab("open", "https://channels.weixin.qq.com/platform/post/create")
    for _ in range(20):
        time.sleep(3)
        if form_ready():
            return True
    # the SPA sometimes parks on /platform after a re-login; enter create via the orange button
    p = rect("[...document.querySelectorAll('*')].find(e=>e.textContent.trim()==='发表视频'&&e.getBoundingClientRect().width>0)", scroll=False)
    if p:
        log("form not ready after open -> clicking 发表视频 @%s" % (p,))
        mouse(*p)
        for _ in range(20):
            time.sleep(3)
            if form_ready():
                return True
    return False


def open_for_edit(desc_prefix):
    ab("open", "https://channels.weixin.qq.com/platform/post/list")
    time.sleep(9)
    js = ("(()=>{const c=[...d.querySelectorAll('*')]"
          ".filter(e=>e.textContent.trim()==='修改并重新发表'&&e.getBoundingClientRect().width>0);"
          "for(const e of c){let p=e;for(let k=0;k<14;k++){p=p.parentElement;if(!p)break;"
          "if(p.innerText.includes(%s)&&p.innerText.includes('将于')){"
          "e.scrollIntoView({block:'center'});const r=e.getBoundingClientRect();"
          "return JSON.stringify([Math.round(r.x+r.width/2),Math.round(r.y+r.height/2)])}}}return 'nf'})()")
    out = ev(js % json.dumps(desc_prefix))
    try:
        x, y = json.loads(json.loads(out))
    except Exception:
        log("FAIL edit button", out); return False
    mouse(x, y)
    for _ in range(30):
        time.sleep(2)
        if form_ready():
            return True
    return False


def cover_imgs():
    """srcs of visible cover thumbnails in the create form."""
    out = ev("(()=>JSON.stringify([...d.querySelectorAll('img')].filter(i=>i.getBoundingClientRect().width>40&&/qpic|finder|qqpica|gtimg|wxfinder/.test(i.src)).map(i=>i.src.slice(0,90))))()")
    try:
        return json.loads(json.loads(out))
    except Exception:
        return []


def dialogs_open():
    out = ev("(()=>String([...d.querySelectorAll('.weui-desktop-dialog')].filter(e=>e.getBoundingClientRect().width>200).length))()")
    try:
        return int(json.loads(out))
    except Exception:
        return -1


def do_cover(rec, tries=3):
    """Upload deliver/cover.png over the default first frame and PROVE it landed.

    Proof = the cover thumbnail's src changed and the dialog closed. A bare
    "no dialog open" is not proof: the editor dialog may never have opened, and
    the first frame is itself a CDN image (2026-10-14 踩到：confirm 按钮 nf 却被判成功).
    """
    for n in range(1, tries + 1):
        before = cover_imgs()
        r = dispatch("[...d.querySelectorAll('.edit-btn')][0]", "edit")
        time.sleep(2.5)
        if "nf" in r or dialogs_open() == 0:
            log("cover try%d: 封面编辑弹窗没开（edit=%s dialogs=%s），等 6s 重试" % (n, r, dialogs_open()))
            time.sleep(6)
            continue
        log("cover try%d tab:" % n, dispatch("[...d.querySelectorAll('*')].filter(e=>e.textContent.trim()==='上传封面'&&e.children.length===0)[0]", "tab"))
        time.sleep(1.5)
        ab("frame", "iframe")
        ab("upload", "input[accept*='image']", rec["cover"])
        ab("frame", "main")
        time.sleep(5)
        log("cover try%d confirm:" % n, dispatch("[...d.querySelectorAll('*')].filter(e=>e.textContent.trim()==='确认'&&e.getBoundingClientRect().width>0).slice(-1)[0]", "confirm"))
        time.sleep(2.5)
        left = dialogs_open()
        if left > 0:
            log("cover try%d: 弹窗没关（dialogs=%s），补一次真实鼠标点击" % (n, left))
            pt = rect("[...d.querySelectorAll('*')].filter(e=>e.textContent.trim()==='确认'&&e.getBoundingClientRect().width>0).slice(-1)[0]")
            if pt:
                mouse(*pt)
                time.sleep(2.5)
            left = dialogs_open()
        after = cover_imgs()
        log("cover try%d: dialogs=%s src %s -> %s" % (n, left, before[:1], after[:1]))
        if left == 0 and after and after != before:
            return True
    return False


def main():
    rid, when = sys.argv[1], sys.argv[2]
    hour = when.split(" ")[1][:2]
    edit = "--edit" in sys.argv
    cover_only = "--cover" in sys.argv
    rec = [r for r in json.load(open(REPO + "/pipeline/publish-queue.json"))["records"]
           if r["id"] == rid][0]
    log("== %s  %s  ->  %s%s" % (rid, rec["short_title"], when,
                                 "  [cover-only]" if cover_only else ("  [edit]" if edit else "")))

    if cover_only:
        if not open_for_edit(rec["description"][:14]):
            log("FAIL cannot open for edit"); return 1
        if not do_cover(rec):
            log("FAIL 封面仍未盖上，停在发表前"); return 2
        btn = rect("[...d.querySelectorAll('button,.weui-desktop-btn')].filter(e=>e.textContent.trim()==='发表'&&e.getBoundingClientRect().width>0)[0]")
        if not btn:
            log("FAIL publish button"); return 1
        mouse(*btn)
        time.sleep(6)
        ab("open", "https://channels.weixin.qq.com/platform/post/list")
        time.sleep(10)
        log("verify:", ev("(()=>{const t=d.body.innerText.replace(/\\n+/g,' | ');const i=t.indexOf(%s);"
                          "return JSON.stringify({count:(t.match(/视频 \\((\\d+)\\)/)||[])[1],seg:t.slice(Math.max(0,i-40),i+200)})})()"
                          % json.dumps(rec["description"][:14])))
        return 0

    if edit:
        if not open_for_edit(rec["description"][:14]):
            log("FAIL cannot open for edit"); return 1
    elif "--go" in sys.argv:
        log("using form already open in the browser")
    else:
        if not fresh_form():
            log("FAIL form not ready"); return 1
        ab("frame", "iframe")
        ab("upload", "input[type=file]", rec["video"])
        ab("frame", "main")
        for _ in range(40):
            time.sleep(4)
            if "done" in ev("(()=>/封面预览/.test(d.body.innerText)&&!/上传中|处理中/.test(d.body.innerText)?'done':'wait')()"):
                break
        else:
            log("FAIL upload timeout"); return 1
        log("uploaded:", ev("(()=>{const t=d.body.innerText;return /上传中|处理中|失败/.test(t)?'BUSY':'clean'})()"))

        log("title:", setval('input[placeholder="填写短标题有机会获得更多流量"]', rec["short_title"]))
        full = rec["description"].replace("\n", " ").strip() + "\n" + " ".join("#" + t for t in rec["topics"])
        log("desc:", ev("(()=>{const e=d.querySelector('.input-editor');if(!e)return 'nf';e.focus();"
                        "const s=w.getSelection();s.selectAllChildren(e);s.collapseToEnd();"
                        "d.execCommand('insertText',false,%s);return 'len='+e.textContent.length})()" % json.dumps(full)))

        log("coll-open:", dispatch("d.querySelector('.post-album-display')", "album"))
        time.sleep(1.5)
        log("coll:", ev("(()=>{const o=[...d.querySelectorAll('.post-album-wrap .option-item')]"
                        ".find(x=>x.textContent.includes(%s));if(!o)return 'option-nf:"
                        "'+[...d.querySelectorAll('.post-album-wrap .option-item')].map(x=>x.textContent.trim()).join(',');"
                        "['mousedown','mouseup','click'].forEach(t=>o.dispatchEvent(new w.MouseEvent(t,{bubbles:true,cancelable:true,view:w})));"
                        "return 'clicked'})()" % json.dumps(rec["collection"])))
        time.sleep(1)
        log("coll-read:", ev("(()=>{const e=d.querySelector('.collection-text');return e?e.textContent.trim():'nf'})()"))

        log("orig:", dispatch("d.querySelector('.declare-original-checkbox .ant-checkbox-wrapper')", "orig"))
        time.sleep(1.5)
        log("orig-agree:", dispatch("d.querySelector('.declare-original-dialog .ant-checkbox-wrapper')", "agree"))
        time.sleep(1.5)
        log("orig-btn:", dispatch("[...d.querySelectorAll('.declare-original-dialog button')].find(e=>e.textContent.trim()==='声明原创')", "declare"))
        time.sleep(1.5)
        log("orig-read:", ev("(()=>String(!!d.querySelector('.declare-original-checkbox .ant-checkbox-checked')))()"))

        if not do_cover(rec):
            log("FAIL 封面没盖上（deliver/cover.png 未生效），停在发表前 —— 不交付默认首帧"); return 2

    # ---- schedule (needs trusted clicks) ----
    log("sched-radio:", dispatch("[...d.querySelectorAll('.weui-desktop-form__check-content')].find(e=>e.textContent.trim()==='定时')", "radio"))
    time.sleep(1.5)
    got = ""
    for attempt in (1, 2):
        p = rect("d.querySelector('input[placeholder=\"请选择发表时间\"]')")
        if not p:
            log("FAIL date input"); return 1
        mouse(*p)
        time.sleep(1.2)
        day = rect("[...d.querySelectorAll('td')].find(x=>x.textContent.trim()==='%s'&&x.getBoundingClientRect().width>0)" % when[8:10].lstrip("0"))
        log("attempt%d day=%s" % (attempt, day))
        if day:
            mouse(*day)
            time.sleep(1.2)
        tp = rect("d.querySelector('input[placeholder=\"请选择时间\"]')")
        log("attempt%d timeInput=%s" % (attempt, tp))
        if tp:
            mouse(*tp)
            time.sleep(1.2)
        js = ("(()=>{const li=[...d.querySelectorAll('.weui-desktop-picker__time li')]"
              ".find(x=>x.textContent.trim()===%s);if(!li)return 'nf';li.scrollIntoView({block:'center'});"
              "const r=li.getBoundingClientRect();return JSON.stringify([Math.round(r.x+r.width/2),Math.round(r.y+r.height/2)])})()" % json.dumps(hour))
        out = ev(js)
        try:
            hx, hy = json.loads(json.loads(out))
            log("attempt%d hour@%s,%s" % (attempt, hx, hy))
            mouse(hx, hy)
        except Exception:
            log("FAIL hour cell", out); continue
        time.sleep(1)
        mouse(400, 200)
        time.sleep(1)
        got = ev("(()=>JSON.stringify([...d.querySelectorAll('input')].filter(i=>i.placeholder&&i.placeholder.includes('时间')).map(i=>i.value)))()")
        log("sched-read:", got)
        if when.split(" ")[1] in got:
            break
    if when.split(" ")[1] not in got:
        log("FAIL schedule not committed, abort before publish"); return 1

    log("state:", ev("(()=>{const t=d.querySelector('input[placeholder=\"填写短标题有机会获得更多流量\"]').value;"
                     "return JSON.stringify({title:t,desc:d.querySelector('.input-editor').textContent.trim().length,"
                     "coll:(d.querySelector('.collection-text')||{}).textContent,"
                     "orig:!!d.querySelector('.declare-original-checkbox .ant-checkbox-checked')})})()"))
    if len(sys.argv) > 3 and sys.argv[3] == "--dry":
        log("DRY: stopped before publish"); return 0
    btn = rect("[...d.querySelectorAll('button,.weui-desktop-btn')].filter(e=>e.textContent.trim()==='发表'&&e.getBoundingClientRect().width>0)[0]")
    if not btn:
        log("FAIL publish button"); return 1
    mouse(*btn)
    time.sleep(6)
    ab("open", "https://channels.weixin.qq.com/platform/post/list")
    time.sleep(10)
    log("verify:", ev("(()=>{const t=d.body.innerText.replace(/\\n+/g,' | ');const i=t.indexOf(%s);"
                      "return JSON.stringify({count:(t.match(/视频 \\((\\d+)\\)/)||[])[1],seg:t.slice(Math.max(0,i-40),i+300)})})()"
                      % json.dumps(rec["description"][:14])))
    return 0


sys.exit(main())
