import tempfile
import unittest
from pathlib import Path

from scripts.render_aegis_cask import parse_sha256sums, render_cask


class RenderAegisCaskTests(unittest.TestCase):
    def test_renders_arch_specific_binary_cask(self) -> None:
        checksums = parse_sha256sums(Path("tests/fixtures/SHA256SUMS"))

        cask = render_cask("1.2.3", checksums)

        self.assertIn('cask "aegis" do', cask)
        self.assertIn('version "1.2.3"', cask)
        self.assertIn('arch arm: "aarch64-apple-darwin", intel: "x86_64-apple-darwin"', cask)
        self.assertIn('sha256 arm:   "1111111111111111111111111111111111111111111111111111111111111111"', cask)
        self.assertIn('intel: "2222222222222222222222222222222222222222222222222222222222222222"', cask)
        self.assertIn('desc "Controlled coding agent harness derived from Codex"', cask)
        self.assertIn('url "https://github.com/mithran-hq/aegis-code/releases/download/rust-v#{version}/aegis-#{arch}.tar.gz"', cask)
        self.assertIn('binary "aegis-#{arch}", target: "aegis"', cask)
        self.assertIn('zap trash: "~/.aegis/log"', cask)

    def test_rejects_missing_required_arch_checksum(self) -> None:
        with self.assertRaises(SystemExit):
            render_cask(
                "1.2.3",
                {
                    "aegis-aarch64-apple-darwin.tar.gz": "1" * 64,
                },
            )

    def test_rejects_invalid_version(self) -> None:
        checksums = parse_sha256sums(Path("tests/fixtures/SHA256SUMS"))

        with self.assertRaises(SystemExit):
            render_cask("rust-v1.2.3", checksums)

    def test_cli_writes_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "aegis.rb"
            from scripts.render_aegis_cask import main
            import sys

            original_argv = sys.argv
            try:
                sys.argv = [
                    "render_aegis_cask.py",
                    "--version",
                    "1.2.3",
                    "--sha256sums",
                    "tests/fixtures/SHA256SUMS",
                    "--output",
                    str(output),
                ]
                main()
            finally:
                sys.argv = original_argv

            self.assertIn('version "1.2.3"', output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
