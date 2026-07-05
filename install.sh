#!/usr/bin/env bash
# Instala skills públicos versionados -> ~/.claude/skills/
# Uso:
#   ./install.sh                 instala TODAS las skills del repo
#   ./install.sh lean refutar    instala solo esas (archivo .md o carpeta)
set -euo pipefail
SRC="$(cd "$(dirname "$0")/skills" && pwd)"
DEST="${HOME}/.claude/skills"
mkdir -p "$DEST"

install_one() {
  local name="$1"
  if [ -d "${SRC}/${name}" ]; then
    rm -rf "${DEST}/${name}"; cp -r "${SRC}/${name}" "${DEST}/${name}"; echo "instalada: ${name}/"
  elif [ -f "${SRC}/${name}.md" ]; then
    cp "${SRC}/${name}.md" "${DEST}/${name}.md"; echo "instalada: ${name}.md"
  else
    echo "NO encontrada en el repo: ${name}" >&2; return 1
  fi
}

if [ "$#" -gt 0 ]; then
  for n in "$@"; do install_one "$n"; done
else
  # todas: rsync preserva archivos sueltos y carpetas, sin borrar skills locales
  rsync -a "${SRC}/" "${DEST}/"
  echo "instaladas TODAS las skills del repo en ${DEST}/"
fi
