#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
printf 'V0233-PHASE5-ORACLE-STUB-PASS\n' > /tmp/stub-out.txt
if OUT=/tmp/stub-out.txt ./verify.sh >/tmp/stub.log 2>&1; then
  echo 'STUB-WAS-ACCEPTED'; exit 1
fi
echo 'STUB-REJECTED'
