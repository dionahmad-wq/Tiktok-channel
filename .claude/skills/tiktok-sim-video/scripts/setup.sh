#!/usr/bin/env bash
# Einmalige Einrichtung pro Cloud-Container: deutsche Offline-Stimme + HyperFrames-CLI.
# Idempotent – kann jederzeit erneut laufen.
set -euo pipefail
VOICE_DIR="${PIPER_VOICE_DIR:-/home/user/tools/voices/vits-piper-de_DE-thorsten-high}"

python3 -c "import piper" 2>/dev/null || pip install -q piper-tts numpy
if [ ! -f "$VOICE_DIR/de_DE-thorsten-high.onnx" ]; then
  mkdir -p "$(dirname "$VOICE_DIR")"
  curl -sL -o /tmp/thorsten.tar.bz2 \
    https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-de_DE-thorsten-high.tar.bz2
  tar xjf /tmp/thorsten.tar.bz2 -C "$(dirname "$VOICE_DIR")" && rm /tmp/thorsten.tar.bz2
fi
npx -y hyperframes@0.9.80 --version >/dev/null 2>&1 || true
npx -y hyperframes@0.9.80 telemetry disable >/dev/null 2>&1 || true
echo "setup ok – Stimme: $VOICE_DIR"
