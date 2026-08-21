#!/bin/sh

set -e

cd "$(dirname "$0")"

PREFIX="$(pwd)/.local-install"

if [ ! -d build ]; then
    meson setup build --prefix="$PREFIX"
fi

meson compile -C build

meson install -C build

KYOU_PKG_DIR="$(find "$PREFIX" -type d -path '*/site-packages/kyou' | head -n1)"

if [ -z "$KYOU_PKG_DIR" ]; then
    exit 1
fi

SITE_PACKAGES="$(dirname "$KYOU_PKG_DIR")"

GSETTINGS_SCHEMA_DIR="$PREFIX/share/glib-2.0/schemas" \
GI_TYPELIB_PATH="$PREFIX/lib/girepository-1.0:/opt/homebrew/lib/girepository-1.0:/usr/local/lib/girepository-1.0:${GI_TYPELIB_PATH}" \
XDG_DATA_DIRS="$PREFIX/share:${XDG_DATA_DIRS:-/opt/homebrew/share:/usr/local/share:/usr/share}" \
PYTHONPATH="$SITE_PACKAGES" \
"$PREFIX/bin/kyou"
