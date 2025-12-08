# Release notes — v0.6.0

Summary
-------

This release bumps Linux Armoury to v0.6.0 and prepares a reproducible Flatpak build.

What I did
-----------

- Bumped version to 0.6.0 in metadata and packaging files.
- Updated the Flatpak manifest (`com.github.th3cavalry.linux-armoury.yml`) to add two modules:
  - `vendored-wheels` — installs binary wheels bundled in `flatpak-wheels/` (ensures offline reproducible builds).
  - `python-deps` — pip install step with prefer-binary fallback.
- Downloaded and vendored wheels for the runtime Python (cp311 / manylinux) for numpy, matplotlib, pillow, customtkinter, packaging and packaged `pygobject` source tarball into `flatpak-wheels/`.
- Verified a full local flatpak build succeeded and produced `linux-armoury-0.6.0.flatpak`.

Files of interest
-----------------

- `com.github.th3cavalry.linux-armoury.yml` — flatpak manifest
- `flatpak-wheels/` — vendored binary wheels used by the `vendored-wheels` module
- `linux-armoury-0.6.0.flatpak` — built bundle placed in the repo root
- `.github/workflows/publish-to-flathub.yml` — workflow to upload a built bundle to a remote host (requires secrets in repo)

How to verify locally
---------------------

1. Rebuild the Flatpak locally (this uses the vendored wheels so it works without network):

```bash
flatpak-builder --force-clean --repo=flatpak-repo flatpak-build/build com.github.th3cavalry.linux-armoury.yml
flatpak build-bundle flatpak-repo linux-armoury-0.6.0.flatpak com.github.th3cavalry.linux-armoury master
```

2. Install the bundle locally for testing:

```bash
flatpak install --user --reinstall linux-armoury-0.6.0.flatpak
flatpak run com.github.th3cavalry.linux-armoury
```

Upload / release steps (manual or CI)
-----------------------------------

1. If you want to upload the bundle to the GitHub release for tag `v0.6.0` using the GitHub CLI (local):

```bash
# Create a release if it doesn't exist
gh release create v0.6.0 --title "Linux Armoury v0.6.0" --notes-file docs/RELEASE-0.6.0.md
# Upload asset
gh release upload v0.6.0 linux-armoury-0.6.0.flatpak
```

Note: `gh` must be authenticated (gh auth login) and the runner / user must have permission to create uploads.

2. CI / Automation — `publish-to-flathub.yml`

The repo includes a GitHub Actions workflow that can transfer a built bundle to a remote host using SSH keys and file upload steps. To enable automated publish to a host you need to add the following repository secrets:

- `TRAVIS_SSH_HOST` (or whichever secret name your workflow expects)
- `TRAVIS_SSH_USER`
- `TRAVIS_SSH_KEY` (private key content)
- `TRAVIS_TARGET_PATH`

(These names may differ in the workflow — check `.github/workflows/publish-to-flathub.yml` and add the corresponding secrets in your repository settings).

Next recommended steps
----------------------

1. Add the final `linux-armoury-0.6.0.flatpak` as a release artifact (via `gh` or GitHub web UI) to fully publish this release.
2. Configure required GitHub Secrets if you want the `publish-to-flathub` workflow to automatically upload the bundle to your destination host.
3. (Optional) Consider bundling any additional binary-only dependencies the runtime expects (Tcl/Tk) if the GUI needs them packaged inside Flatpak (verify runtime dependencies and adjust manifest accordingly).

If you'd like, I can upload the built bundle to the GitHub release for v0.6.0 if you authenticate the environment or give me credentials/secrets to use in CI. I can also help configure the publish workflow secrets.
