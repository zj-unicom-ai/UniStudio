"""Run the bundled project from the library template directory."""
import sys,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];project=root/'assets/template-project'
if len(sys.argv)<2:raise SystemExit('Expected compose, check, render or dev')
operation,*args=sys.argv[1:]
if operation=='compose':cmd=[sys.executable,'scripts/build_composition.py',*args]
elif operation=='check':cmd=['npx','--yes','hyperframes@0.8.133','check',*args]
elif operation=='dev':cmd=['npx','--yes','hyperframes@0.8.133','preview','--background',*args]
elif operation=='render':
 if '--output' in args:
  i=args.index('--output')+1
  if i>=len(args):raise SystemExit('--output requires a file path')
  args[i]=str((root/args[i]).resolve())
 else:args+=['--output',str(root/'out/international-vision.mp4')]
 cmd=[sys.executable,'scripts/render_and_cover.py',*args]
else:raise SystemExit('Unknown operation: '+operation)
raise SystemExit(subprocess.run(cmd,cwd=project).returncode)
