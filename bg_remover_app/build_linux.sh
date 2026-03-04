#!/usr/bin/env bash
# build_linux.sh — Build BG Remover for Linux
# Outputs: lin/BGRemover-v{VERSION}-x86_64.AppImage
#          lin/bg-remover-{VERSION}-1.x86_64.rpm
#          lin/bg-remover_{VERSION}_amd64.deb
#          lin/BGRemover-v{VERSION}-linux.tar.gz

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Read version ──────────────────────────────────────────────────────────────
VERSION=$(python3 -c "from version import __version__; print(__version__)")
APP_NAME="BGRemover"
PKG_NAME="bg-remover"
echo "==> Building ${APP_NAME} v${VERSION} for Linux"

# ── Activate venv if present ──────────────────────────────────────────────────
if [ -d ".build_venv" ]; then
    source .build_venv/bin/activate
elif [ -d "../.venv" ]; then
    source ../.venv/bin/activate
fi

PYINSTALLER=$(command -v pyinstaller 2>/dev/null || true)
if [ -z "$PYINSTALLER" ]; then
    echo "ERROR: pyinstaller not found in PATH or venv"
    exit 1
fi

mkdir -p lin
mkdir -p .build_tools

# ── 1. PyInstaller binary ─────────────────────────────────────────────────────
echo "==> [1/4] PyInstaller…"
"$PYINSTALLER" bg_remover_app.spec --clean --noconfirm \
    --distpath dist --workpath build 2>&1 | tail -5

BINARY="dist/${APP_NAME}"
if [ ! -f "$BINARY" ]; then
    echo "ERROR: binary not found at $BINARY"
    exit 1
fi

# ── 2. tar.gz archive ────────────────────────────────────────────────────────
echo "==> [2/4] tar.gz…"
TARBALL="lin/${APP_NAME}-v${VERSION}-linux.tar.gz"
tar czf "$TARBALL" -C dist "${APP_NAME}"
echo "    $TARBALL"

# ── 3. AppImage ───────────────────────────────────────────────────────────────
echo "==> [3/4] AppImage…"
APPIMAGETOOL=".build_tools/appimagetool"
if [ ! -f "$APPIMAGETOOL" ]; then
    curl -L -o "$APPIMAGETOOL" \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x "$APPIMAGETOOL"
fi

APPDIR="build/${APP_NAME}.AppDir"
rm -rf "$APPDIR" && mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/share/icons/hicolor/256x256/apps"

cp "$BINARY" "$APPDIR/usr/bin/${APP_NAME}"
cp "icons/icon.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/${PKG_NAME}.png"
cp "icons/icon.png" "$APPDIR/${PKG_NAME}.png"

cat > "$APPDIR/${APP_NAME}.desktop" <<DESKTOP
[Desktop Entry]
Name=BG Remover
Exec=${APP_NAME}
Icon=${PKG_NAME}
Type=Application
Categories=Graphics;
Comment=AI-powered batch background removal — 100% offline
DESKTOP

cat > "$APPDIR/AppRun" <<'APPRUN'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
exec "$HERE/usr/bin/BGRemover" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

APPIMAGE_FILE="lin/${APP_NAME}-v${VERSION}-x86_64.AppImage"
APPIMAGE_EXTRACT_AND_RUN=1 "$APPIMAGETOOL" "$APPDIR" "$APPIMAGE_FILE" 2>&1 | tail -3
chmod +x "$APPIMAGE_FILE"
echo "    $APPIMAGE_FILE"

# ── 4a. RPM ───────────────────────────────────────────────────────────────────
if command -v rpmbuild &>/dev/null; then
    echo "==> [4a/4] RPM…"
    RPM_STAGE="dist/_rpm_stage/${APP_NAME}-${VERSION}"
    mkdir -p "${RPM_STAGE}/usr/bin" \
              "${RPM_STAGE}/usr/share/applications" \
              "${RPM_STAGE}/usr/share/icons/hicolor/256x256/apps"

    cp "$BINARY" "${RPM_STAGE}/usr/bin/${APP_NAME}"
    cp "icons/icon.png" "${RPM_STAGE}/usr/share/icons/hicolor/256x256/apps/${PKG_NAME}.png"

    cat > "${RPM_STAGE}/usr/share/applications/${PKG_NAME}.desktop" <<DESKTOP
[Desktop Entry]
Name=BG Remover
Exec=${APP_NAME}
Icon=${PKG_NAME}
Type=Application
Categories=Graphics;
Comment=AI-powered batch background removal — 100% offline
DESKTOP

    # Symlink avoids rpmbuild issues with spaces in path
    RPM_LINK="/tmp/bgr_rpm_stage_$$"
    ln -sfn "$(realpath "${SCRIPT_DIR}/dist/_rpm_stage")" "$RPM_LINK"

    rpmbuild -bb --define "_topdir ${RPM_LINK}/rpmbuild" \
                 --define "_app_src ${RPM_LINK}/${APP_NAME}-${VERSION}" \
                 --define "__strip /bin/true" \
                 - <<SPECFILE 2>&1 | tail -5
Name:       ${PKG_NAME}
Version:    ${VERSION}
Release:    1%{?dist}
Summary:    AI-powered batch background removal — 100%% offline
License:    MIT
BuildArch:  x86_64

%description
Drop your character sprites and art; get clean transparent PNGs
without cloud APIs, subscriptions, or watermarks.
Powered by rembg, BiRefNet, ISNet, and U2Net.

%install
cp -a %{_app_src}/. %{buildroot}/

%files
/usr/bin/${APP_NAME}
/usr/share/applications/${PKG_NAME}.desktop
/usr/share/icons/hicolor/256x256/apps/${PKG_NAME}.png

%changelog
* $(date "+%a %b %d %Y") Long Weekend Labs <longweekendlabs@users.noreply.github.com> - ${VERSION}-1
- v${VERSION} release
SPECFILE

    find "${RPM_LINK}/rpmbuild/RPMS" -name "*.rpm" | while read rpm_path; do
        cp "$rpm_path" "lin/${PKG_NAME}-${VERSION}-1.x86_64.rpm"
        echo "    lin/${PKG_NAME}-${VERSION}-1.x86_64.rpm"
    done
    rm -f "$RPM_LINK"
else
    echo "    (rpmbuild not found — skipping RPM)"
fi

# ── 4b. DEB ───────────────────────────────────────────────────────────────────
echo "==> [4b/4] DEB…"
DEB_TMP="build/deb_${PKG_NAME}_${VERSION}"
rm -rf "$DEB_TMP"
mkdir -p "${DEB_TMP}/DEBIAN" \
         "${DEB_TMP}/usr/bin" \
         "${DEB_TMP}/usr/share/applications" \
         "${DEB_TMP}/usr/share/icons/hicolor/256x256/apps"

cp "$BINARY" "${DEB_TMP}/usr/bin/${APP_NAME}"
cp "icons/icon.png" "${DEB_TMP}/usr/share/icons/hicolor/256x256/apps/${PKG_NAME}.png"

cat > "${DEB_TMP}/usr/share/applications/${PKG_NAME}.desktop" <<DESKTOP
[Desktop Entry]
Name=BG Remover
Exec=${APP_NAME}
Icon=${PKG_NAME}
Type=Application
Categories=Graphics;
Comment=AI-powered batch background removal — 100% offline
DESKTOP

cat > "${DEB_TMP}/DEBIAN/control" <<CTRL
Package: ${PKG_NAME}
Version: ${VERSION}
Architecture: amd64
Maintainer: Long Weekend Labs <longweekendlabs@users.noreply.github.com>
Description: AI-powered batch background removal
 Drop your sprites; get clean transparent PNGs without cloud APIs.
 Powered by rembg, BiRefNet, ISNet, and U2Net. 100%% offline.
CTRL

DEB_FILE="lin/${PKG_NAME}_${VERSION}_amd64.deb"

if command -v dpkg-deb &>/dev/null; then
    dpkg-deb --build "$DEB_TMP" "$DEB_FILE"
elif command -v alien &>/dev/null && [ -f "lin/${PKG_NAME}-${VERSION}-1.x86_64.rpm" ]; then
    (cd lin && alien --to-deb "${PKG_NAME}-${VERSION}-1.x86_64.rpm" 2>&1 | tail -3)
else
    # Manual ar-based .deb (no external tools required)
    CONTROL_TAR="build/control_${PKG_NAME}.tar.gz"
    DATA_TAR="build/data_${PKG_NAME}.tar.gz"
    echo "2.0" > build/debian-binary
    (cd "$DEB_TMP" && tar czf "${SCRIPT_DIR}/${CONTROL_TAR}" ./DEBIAN)
    (cd "$DEB_TMP" && tar czf "${SCRIPT_DIR}/${DATA_TAR}" --exclude=./DEBIAN .)
    ar -r "$DEB_FILE" build/debian-binary "$CONTROL_TAR" "$DATA_TAR"
fi

echo "    $DEB_FILE"
echo ""
echo "==> Done. Packages in lin/:"
ls -lh lin/
