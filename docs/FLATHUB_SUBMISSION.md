# Flathub Submission Guide

This document provides step-by-step instructions for submitting Linux Armoury to Flathub.

## Prerequisites

Before submitting to Flathub, ensure:

1. ✅ The app builds successfully with flatpak-builder
2. ✅ All required metadata files are present:
   - `com.github.th3cavalry.linux-armoury.yml` (Flatpak manifest)
   - `com.github.th3cavalry.linux-armoury.desktop` (Desktop entry)
   - `data/metainfo/com.github.th3cavalry.linux-armoury.metainfo.xml` (AppData)
   - `data/icons/com.github.th3cavalry.linux-armoury.svg` (App icon)
3. ✅ The app has been tested locally
4. ✅ Version is set to 0.6.2 in all files

## Step 1: Test the Build Locally

Before submitting, verify the Flatpak builds successfully:

```bash
# Clean any previous builds
rm -rf build-dir repo

# Build the Flatpak
flatpak-builder --user --install-deps-from=flathub --force-clean \
  --repo=repo build-dir com.github.th3cavalry.linux-armoury.yml

# Create a bundle for testing
flatpak build-bundle repo linux-armoury-0.6.2.flatpak \
  com.github.th3cavalry.linux-armoury

# Install and test locally
flatpak install --user --reinstall linux-armoury-0.6.2.flatpak
flatpak run com.github.th3cavalry.linux-armoury
```

## Step 2: Validate the Manifest

Run the Flathub linter to check for issues:

```bash
# Install the linter (if not already installed)
flatpak install --user flathub org.flatpak.Builder

# Lint the manifest
flatpak run --command=flatpak-builder-lint org.flatpak.Builder \
  manifest com.github.th3cavalry.linux-armoury.yml

# Lint the builddir (after building)
flatpak run --command=flatpak-builder-lint org.flatpak.Builder \
  builddir build-dir

# Lint the repo
flatpak run --command=flatpak-builder-lint org.flatpak.Builder \
  repo repo
```

## Step 3: Fork the Flathub Repository

1. Go to https://github.com/flathub/flathub
2. Click the "Fork" button to create your own fork
3. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/flathub.git
cd flathub
```

## Step 4: Create a Submission Branch

Flathub uses the `new-pr` branch for new app submissions:

```bash
# Fetch the new-pr branch
git fetch origin new-pr

# Create your submission branch from new-pr
git checkout -b add-linux-armoury origin/new-pr
```

## Step 5: Add Your App Files

Copy the necessary files to the flathub repository:

```bash
# Create a directory for your app (in the flathub repo)
mkdir -p com.github.th3cavalry.linux-armoury

# Copy the manifest
cp /path/to/Linux-Armoury/com.github.th3cavalry.linux-armoury.yml \
   com.github.th3cavalry.linux-armoury/

# Copy the desktop file
cp /path/to/Linux-Armoury/com.github.th3cavalry.linux-armoury.desktop \
   com.github.th3cavalry.linux-armoury/

# Copy the metainfo file
cp /path/to/Linux-Armoury/data/metainfo/com.github.th3cavalry.linux-armoury.metainfo.xml \
   com.github.th3cavalry.linux-armoury/

# Copy the icon
cp /path/to/Linux-Armoury/data/icons/com.github.th3cavalry.linux-armoury.svg \
   com.github.th3cavalry.linux-armoury/

# Copy requirements.txt if needed
cp /path/to/Linux-Armoury/requirements.txt \
   com.github.th3cavalry.linux-armoury/

# Copy flatpak-wheels directory if using vendored wheels
cp -r /path/to/Linux-Armoury/flatpak-wheels \
   com.github.th3cavalry.linux-armoury/
```

## Step 6: Commit and Push

```bash
# Add all files
git add com.github.th3cavalry.linux-armoury/

# Commit with a clear message
git commit -m "Add com.github.th3cavalry.linux-armoury"

# Push to your fork
git push origin add-linux-armoury
```

## Step 7: Create a Pull Request

1. Go to your fork on GitHub: `https://github.com/YOUR_USERNAME/flathub`
2. Click "Compare & pull request"
3. Make sure the base repository is `flathub/flathub` and base branch is `new-pr`
4. Title your PR: "Add com.github.th3cavalry.linux-armoury"
5. In the description, include:
   ```
   ## Application Information
   - Name: Linux Armoury
   - Description: GTK4 control center for ASUS ROG laptops
   - Version: 0.6.2
   - License: GPL-3.0-or-later
   - Homepage: https://github.com/th3cavalry/Linux-Armoury
   
   ## Testing
   - Built and tested locally: ✅
   - Manifest linting: ✅
   - Runs without errors: ✅
   
   ## Notes
   This is a power management and control center for ASUS ROG laptops.
   It requires system-level permissions for hardware control.
   ```
6. Submit the pull request

## Step 8: Respond to Review Feedback

Flathub maintainers will review your submission and may request changes:

1. Make requested changes in your Linux-Armoury repository
2. Update the files in your flathub fork
3. Commit and push the changes
4. The PR will automatically update

## Step 9: After Approval

Once approved:

1. Flathub will create a dedicated repository: `https://github.com/flathub/com.github.th3cavalry.linux-armoury`
2. You'll get write access to that repository
3. Future updates only require updating the manifest in that repository
4. Builds will happen automatically on Flathub's infrastructure

## Updating Your App on Flathub

After initial approval, to release updates:

```bash
# Clone your app's flathub repo
git clone https://github.com/flathub/com.github.th3cavalry.linux-armoury.git
cd com.github.th3cavalry.linux-armoury

# Update the manifest with new version/source
# Edit com.github.th3cavalry.linux-armoury.yml

# Commit and push
git commit -am "Update to version 0.6.3"
git push
```

## Common Issues and Solutions

### Issue: Build fails with network errors
**Solution**: Ensure all sources are properly specified with checksums in the manifest.

### Issue: Icon not displaying
**Solution**: Ensure icon filename matches the app ID: `com.github.th3cavalry.linux-armoury.svg`

### Issue: Desktop file validation fails
**Solution**: Run `desktop-file-validate com.github.th3cavalry.linux-armoury.desktop`

### Issue: AppStream validation fails
**Solution**: Validate with `appstream-util validate-relax com.github.th3cavalry.linux-armoury.metainfo.xml`

## Resources

- Flathub Documentation: https://docs.flathub.org/
- App Submission Guide: https://docs.flathub.org/docs/for-app-authors/submission
- Flatpak Builder Docs: https://docs.flatpak.org/en/latest/flatpak-builder.html
- Flathub Quality Guidelines: https://docs.flathub.org/docs/for-app-authors/requirements

## Support

If you need help with the submission:
- Flathub Discourse: https://discourse.flathub.org/
- Matrix: #flathub:matrix.org
- GitHub Issues: https://github.com/flathub/flathub/issues
