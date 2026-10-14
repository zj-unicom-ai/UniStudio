"""Copy the bundled self-contained reference project to a new directory."""
import argparse,shutil
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('destination',type=Path)
args=parser.parse_args(); source=Path(__file__).resolve().parents[1]/'assets/template-project'
if args.destination.exists(): parser.error('Destination already exists; choose a new folder to preserve existing work.')
shutil.copytree(source,args.destination,ignore=shutil.ignore_patterns('renders','snapshots','.hyperframes','.thumbnails','.waveform-cache','node_modules','__pycache__','.DS_Store'))
print('Created:',args.destination.resolve())
print('Sample has silent narration tracks; replace them before making a narrated film.')
