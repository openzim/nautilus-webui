#!/bin/sh

JS_PATH=/user/share/nginx/html/environ.json
echo "dump NAUTILUS_* environ variables to $JS_PATH"

python3 -c 'import os; import json; print(json.dumps({k: v for k, v in os.environ.items() if k.startswith("NAUTILUS_")}, indent=2))' > $JS_PATH

cat $JS_PATH
echo "-----"

exec "$@"
