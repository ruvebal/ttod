#!/usr/bin/env bash
# AA3 live HTML inventory (cold review F10): the header and the main landmark of five views, en and es,
# signed out and signed in, as the server sends them. Run against scripts/isolated-stack.sh, never the
# instructor stack. Usage: inventory.sh <base-url> <out-dir>
set -euo pipefail
base="${1:?base}"; out="${2:?out}"; mkdir -p "$out"
jar="$(mktemp)"; email="inv-$(date +%s)@example.test"; pw="inventory-password-1"
port="$(echo "$base" | sed -E 's#.*:([0-9]+).*#\1#')"
curl -s -o /dev/null -H 'content-type: application/json' -d "{\"email\":\"$email\",\"password\":\"$pw\"}" "$base/api/v1/auth/register"
curl -s -o /dev/null -c "$jar" -H "Origin: http://localhost:$port" -H "Host: localhost:$port" -d "email=$email&password=$pw" "$base/es/login/"
for who in out in; do
  for path in /es/ /en/ /es/wisdom/sections/architecture/ /en/oracle/ /es/login/; do
    slug="$(echo "$path" | tr '/' '-' | sed 's/^-//; s/-$//')"
    if [ "$who" = in ]; then html="$(curl -s -b "$jar" -H "Host: localhost:$port" "$base$path")"; else html="$(curl -s "$base$path")"; fi
    printf '%s' "$html" | python3 -c "
import re, sys
h = sys.stdin.read()
head = re.search(r'<header[^>]*id=\"ttod-site-header\".*?</header>', h, re.S)
main = re.search(r'<main[^>]*>', h)
skip = re.search(r'<a class=\"ttod-skip-link\"[^>]*>', h)
print('<!-- skip link -->'); print(skip.group(0) if skip else 'MISSING')
print('<!-- main landmark -->'); print(main.group(0) if main else 'MISSING')
print('<!-- header -->'); print(re.sub(r'\sdata-astro-cid-[a-z0-9]+(=\"\")?', '', head.group(0)) if head else 'MISSING')
" > "$out/$who-$slug.html"
  done
done
rm -f "$jar"; ls "$out" | wc -l
