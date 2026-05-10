# Mithran Homebrew Tap

This tap publishes Homebrew casks for Mithran command-line tools.

## Aegis Code

Aegis Code is distributed as a macOS cask named `aegis` after a public
`mithran-hq/aegis-code` GitHub Release has been published.

```sh
brew tap mithran-hq/tap
brew install --cask aegis
```

Upgrade an existing cask install with:

```sh
brew upgrade --cask aegis
```

The cask installs the `aegis` executable and expects release assets named:

- `aegis-aarch64-apple-darwin.tar.gz`
- `aegis-x86_64-apple-darwin.tar.gz`
- `SHA256SUMS`

## Updating The Aegis Cask

After publishing an Aegis Code release tagged `rust-vX.Y.Z`, run the
`Update Aegis cask` workflow with `version` set to `X.Y.Z`. The workflow
downloads `SHA256SUMS`, renders `Casks/aegis.rb`, validates it with Homebrew,
and commits the update back to this tap.
