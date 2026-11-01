#!/usr/bin/env bash
# Rebuilds the video-editing toolkit (Remotion, HyperFrames, FFmpeg, whisper.cpp, yt-dlp)
# in a fresh Claude Code cloud container. Safe to re-run.
set -euo pipefail

TOOLS="$HOME/video-tools"
CHROME=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
mkdir -p "$TOOLS"

# FFmpeg (system package)
command -v ffmpeg >/dev/null || { apt-get update -qq && apt-get install -y -qq ffmpeg; }

# yt-dlp; use the system CA store so it trusts the environment's HTTPS proxy
pip install -q -U yt-dlp
mkdir -p "$HOME/.config/yt-dlp"
echo "--compat-options no-certifi" > "$HOME/.config/yt-dlp/config"

# whisper.cpp
if [ ! -x "$TOOLS/whisper.cpp/build/bin/whisper-cli" ]; then
  git clone -q --depth 1 https://github.com/ggml-org/whisper.cpp "$TOOLS/whisper.cpp"
  cmake -S "$TOOLS/whisper.cpp" -B "$TOOLS/whisper.cpp/build" -DCMAKE_BUILD_TYPE=Release >/dev/null
  cmake --build "$TOOLS/whisper.cpp/build" -j"$(nproc)" --config Release >/dev/null
fi
# Needs huggingface.co allowed in the environment's network settings
sh "$TOOLS/whisper.cpp/models/download-ggml-model.sh" base.en \
  || echo "WARN: Whisper model download failed (is huggingface.co allowed?)"

# Remotion; uses the pre-installed Chromium because remotion.media is not reachable
if [ ! -d "$TOOLS/remotion-studio" ]; then
  (cd "$TOOLS" && npx -y create-video@latest --yes --hello-world remotion-studio)
  (cd "$TOOLS/remotion-studio" && npm install --silent)
  printf '\nConfig.setBrowserExecutable("%s");\n' "$CHROME" >> "$TOOLS/remotion-studio/remotion.config.ts"
fi

# HyperFrames; serves GSAP locally because cdn.jsdelivr.net is not reachable
npm install -g hyperframes >/dev/null
if [ ! -d "$TOOLS/hyperframes-studio" ]; then
  (cd "$TOOLS" && HYPERFRAMES_SKIP_SKILLS=1 hyperframes init hyperframes-studio --non-interactive --skip-skills)
  (cd "$TOOLS/hyperframes-studio" && npm install --silent gsap@3.15.0 && mkdir -p vendor \
    && cp node_modules/gsap/dist/gsap.min.js vendor/ \
    && sed -i 's#https://cdn.jsdelivr.net/npm/gsap@[0-9.]*/dist/gsap.min.js#vendor/gsap.min.js#' index.html)
fi
echo "Done. Tools are in $TOOLS"
echo "Render HyperFrames with: PUPPETEER_EXECUTABLE_PATH=$CHROME hyperframes render"
