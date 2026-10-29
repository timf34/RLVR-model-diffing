#!/bin/bash
# Finite queue for workstream C: generate -> score -> judge -> score(merge) -> analyse, per frozen experiment.
# Usage (repo root): bash designs/ifeval_incidental_grader/run_pipeline.sh main applicability discovery
set -u
ROOT=/Users/timf34/Documents/VSCode/model-diffing-agent
D=$ROOT/designs/ifeval_incidental_grader
MG="$HOME/.claude/bin/memguard -m 4 --"
cd $ROOT
caffeinate -i -w $$ &
for EXP in "$@"; do
  echo "=== $EXP generate $(date -u +%FT%TZ)"
  for pass in 1 2 3; do
    $MG .venv/bin/python $D/ig_generate.py $EXP --minutes 240 2>&1 | grep -v '^memguard'
    left=$($MG .venv/bin/python -c "
import sys,json; sys.path.insert(0,'$D'); import ig_generate as G
recs=G.load_records('$EXP'); done={r['key'] for r in recs if r['status']!='error'}
att={}
for r in recs: att[r['key']]=att.get(r['key'],0)+1
print(sum(1 for i in G.plan('$EXP') if i['key'] not in done and att.get(i['key'],0)<G.MAX_ATTEMPTS))" 2>/dev/null | tail -1)
    echo "  pass $pass: $left remaining"
    [ "$left" = "0" ] && break
  done
  echo "=== $EXP score $(date -u +%FT%TZ)"
  (cd $D && $MG .venv_checker/bin/python ig_score.py $EXP 2>&1 | grep -v '^memguard')
  echo "=== $EXP judge $(date -u +%FT%TZ)"
  $MG .venv/bin/python $D/ig_judge.py $EXP 2>&1 | grep -v '^memguard' | tail -2
  echo "=== $EXP analyse $(date -u +%FT%TZ)"
  (cd $D && $MG ../../.venv/bin/python ig_analysis.py $EXP 2>&1 | grep -v '^memguard' | tail -5)
  echo "=== $EXP done $(date -u +%FT%TZ)"
done
