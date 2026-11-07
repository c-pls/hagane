#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# Hagane — Garmin Connect IQ Build Script (Forerunner 255 Music 46mm)
# Produces:
#   1. dist/Hagane.prg -> Method 1: Instant USB Sideload (copy to GARMIN/APPS/)
#   2. dist/Hagane.iq  -> Method 2: Private Beta Wireless Package (upload to Garmin Store)
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p dist

# 1. Locate monkeyc compiler (portable across macOS BSD & Linux without sort -V)
if command -v monkeyc >/dev/null 2>&1; then
  MONKEYC="monkeyc"
elif [ -n "${CIQ_SDK_HOME:-}" ] && [ -x "${CIQ_SDK_HOME}/bin/monkeyc" ]; then
  MONKEYC="${CIQ_SDK_HOME}/bin/monkeyc"
else
  LATEST_SDK=$(python3 -c '
import glob, os, re
roots = [
    os.path.expanduser("~/Library/Application Support/Garmin/ConnectIQ/Sdks"),
    os.path.expanduser("~/.Garmin/ConnectIQ/Sdks"),
]
candidates = []
for r in roots:
    for p in glob.glob(os.path.join(r, "connectiq-sdk-*")):
        if os.path.isfile(os.path.join(p, "bin", "monkeyc")):
            nums = [int(x) for x in re.findall(r"\d+", os.path.basename(p))]
            candidates.append((nums, p))
if candidates:
    candidates.sort()
    print(candidates[-1][1])
' 2>/dev/null || true)

  if [ -n "$LATEST_SDK" ] && [ -x "$LATEST_SDK/bin/monkeyc" ]; then
    MONKEYC="$LATEST_SDK/bin/monkeyc"
  else
    echo "❌ Could not find 'monkeyc' compiler."
    echo "👉 Install the free Garmin Connect IQ SDK Manager (or VS Code Monkey C extension)"
    echo "   and download the SDK + 'Forerunner 255 Music' device profile, or set CIQ_SDK_HOME."
    exit 1
  fi
fi

echo "🔧 Using compiler: $MONKEYC"

# 2. Persist 4096-bit RSA developer key outside dist/ so cleaning dist/ does not change signing identity
KEY_DER="developer_key.der"
KEY_PEM="developer_key.pem"
if [ ! -f "$KEY_DER" ]; then
  echo "🔑 Generating 4096-bit RSA Garmin developer key ($KEY_DER)..."
  openssl genrsa -out "$KEY_PEM" 4096 2>/dev/null
  openssl pkcs8 -topk8 -inform PEM -outform DER -in "$KEY_PEM" -out "$KEY_DER" -nocrypt
  echo "ℹ️  Keep garmin-watch/$KEY_DER backed up so future watch updates share the same key."
fi

# 3. Build Method 1: USB Sideload binary (Hagane.prg) for Forerunner 255 Music (fr255m)
DEVICE="${1:-fr255m}"
echo "⌚ Building dist/Hagane.prg for device '$DEVICE' (Forerunner 255 Music 46mm)..."
"$MONKEYC" \
  -o dist/Hagane.prg \
  -f monkey.jungle \
  -y "$KEY_DER" \
  -d "$DEVICE" \
  -w

echo "✅ Built: dist/Hagane.prg (Copy via USB to GARMIN/APPS/Hagane.prg)"

# 4. Build Method 2: Private Beta Store Package (Hagane.iq)
echo "📦 Packaging dist/Hagane.iq for Private Beta wireless install..."
if "$MONKEYC" \
  -e \
  -o dist/Hagane.iq \
  -f monkey.jungle \
  -y "$KEY_DER" \
  -r \
  -w; then
  echo "✅ Built: dist/Hagane.iq (Upload as Private Beta on apps.garmin.com)"
else
  echo "ℹ️  Note: .iq packaging requires both 'fr255m' and 'fr255' device profiles downloaded in SDK Manager."
  echo "   dist/Hagane.prg for '$DEVICE' is ready!"
fi
