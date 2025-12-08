```markdown
# Release notes — v0.6.1

Summary
-------

This release bumps Linux Armoury to v0.6.1 and produces a reproducible Flatpak bundle.

What changed
-----------

- Bumped version to 0.6.1 in project metadata and packaging files.
- Updated the Flatpak CI workflow to ensure the GNOME SDK and elfutils (for stripping) are available in CI.
- Added minor packaging fixes to improve reproducible flatpak builds.

Build artifact
--------------

This release produces `linux-armoury-0.6.1.flatpak`.

How to verify locally
---------------------

1. Rebuild the Flatpak locally (uses vendored wheels if present):

```bash
flatpak-builder --force-clean --repo=flatpak-repo flatpak-build/build com.github.th3cavalry.linux-armoury.yml
flatpak build-bundle flatpak-repo linux-armoury-0.6.1.flatpak com.github.th3cavalry.linux-armoury master
```

2. Install the bundle locally for testing:

```bash
flatpak install --user --reinstall linux-armoury-0.6.1.flatpak
flatpak run com.github.th3cavalry.linux-armoury
```

Upload / release steps (manual or CI)
-----------------------------------

1. Using GitHub CLI locally:

```bash
gh release create v0.6.1 --title "Linux Armoury v0.6.1" --notes-file docs/RELEASE-0.6.1.md
gh release upload v0.6.1 linux-armoury-0.6.1.flatpak
```

2. CI / Automation — ensure the publish workflows are configured with appropriate secrets to upload the built bundle.

Next recommended steps
----------------------

1. Add `linux-armoury-0.6.1.flatpak` to the release assets (GitHub release) or configure CI to publish automatically.
2. Verify the CI build artifacts and update any downstream release channels.

```
