"""Copy explicitly allowlisted read-only ALMAS Web assets to Vercel public/.

Never copy the source schema registry, fixtures, unreviewed files, private data,
server-only variables or Python core. The two existing API functions remain
under api/ and are handled separately by Vercel Functions.
"""
from pathlib import Path
from shutil import copyfile
APP=Path(__file__).resolve().parent
PUBLIC=APP/"public"
PUBLIC.mkdir(exist_ok=True)
ASSETS=(
    "index.html",
    "app.mjs",
    "birth-request.mjs",
    "birth-ui.mjs",
    "birth-geocoding.mjs",
    "validator.mjs",
    "local-inspection.mjs",
    "evidence-graph.mjs",
    "astrology-view.mjs",
    "report-view.mjs",
    "json-lexical-digest.mjs",
    "full-schema-validator.mjs",
)
for filename in ASSETS:
    source=APP/filename
    if not source.is_file() or source.stat().st_size==0:
        raise SystemExit(f"Missing required static artifact: {filename}")
    copyfile(source,PUBLIC/filename)
print("Published strictly allowlisted offline ALMAS Web assets: "+str(len(ASSETS)))
