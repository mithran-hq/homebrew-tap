#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
from pathlib import Path


TARGETS = {
    "arm": "aarch64-apple-darwin",
    "intel": "x86_64-apple-darwin",
}
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-(?:alpha|beta)(?:\.[0-9]+)?)?$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_sha256sums(path: Path) -> dict[str, str]:
    checksums: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            raise SystemExit(f"invalid SHA256SUMS line: {raw_line}")
        digest = parts[0].lower()
        asset = Path(parts[-1].lstrip("*")).name
        if not SHA256_RE.fullmatch(digest):
            raise SystemExit(f"invalid SHA-256 digest for {asset}: {digest}")
        checksums[asset] = digest
    return checksums


def render_cask(version: str, checksums: dict[str, str]) -> str:
    if not VERSION_RE.fullmatch(version):
        raise SystemExit(f"invalid Aegis release version: {version}")

    required_assets = {
        arch: f"aegis-{target}.tar.gz" for arch, target in TARGETS.items()
    }
    missing = [
        asset for asset in required_assets.values() if asset not in checksums
    ]
    if missing:
        raise SystemExit(
            "missing required release checksum(s): " + ", ".join(sorted(missing))
        )

    arm_sha = checksums[required_assets["arm"]]
    intel_sha = checksums[required_assets["intel"]]

    return f'''cask "aegis" do
  arch arm: "aarch64-apple-darwin", intel: "x86_64-apple-darwin"

  version "{version}"
  sha256 arm:   "{arm_sha}",
         intel: "{intel_sha}"

  url "https://github.com/mithran-hq/aegis-code/releases/download/rust-v#{{version}}/aegis-#{{arch}}.tar.gz",
      verified: "github.com/mithran-hq/aegis-code/"
  name "Aegis Code"
  desc "Controlled coding agent harness derived from Codex"
  homepage "https://github.com/mithran-hq/aegis-code"

  livecheck do
    url "https://github.com/mithran-hq/aegis-code/releases/latest"
    regex(/^rust-v(\\d+(?:\\.\\d+)+(?:-(?:alpha|beta)(?:\\.\\d+)?)?)$/i)
  end

  depends_on macos: ">= :monterey"

  binary "aegis-#{{arch}}", target: "aegis"

  zap trash: "~/.aegis/log"

  caveats <<~EOS
    Aegis Code stores configuration and session data under ~/.aegis.
    Run `aegis doctor` after installation to verify your setup.
  EOS
end
'''


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the Aegis Homebrew cask.")
    parser.add_argument("--version", required=True, help="Release version without rust-v.")
    parser.add_argument("--sha256sums", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    cask = render_cask(args.version, parse_sha256sums(args.sha256sums))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(cask, encoding="utf-8")


if __name__ == "__main__":
    main()
