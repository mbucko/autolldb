
xcrun python3 -m venv autolldb
source  autolldb/autolldb/bin/activate
export PYTHONPATH=$(xcrun lldb --print-script-interpreter-info | jq -r '.["lldb-pythonpath"]'):$PYTHONPATH
