# Flathub Submission - Quick Start Guide

This repository is now ready for Flathub submission! This quick guide will help you submit Linux Armoury to Flathub in just a few steps.

## What's Been Prepared

✅ Version incremented to 0.6.2  
✅ All metadata files updated  
✅ Icon files correctly named with app ID  
✅ Desktop file updated  
✅ Comprehensive documentation created  
✅ Automated preparation script ready  

## Quick Steps to Submit

### 1. Test Locally (Recommended)

```bash
# Build the Flatpak locally to verify everything works
make clean
make flatpak-build

# Test run it
flatpak run com.github.th3cavalry.linux-armoury
```

### 2. Prepare Submission Files

```bash
# Run the automated preparation script
./prepare-flathub-submission.sh

# This creates a 'flathub-submission' directory with all necessary files
```

### 3. Fork Flathub Repository

1. Go to https://github.com/flathub/flathub
2. Click "Fork" button
3. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/flathub.git
   cd flathub
   ```

### 4. Create Submission Branch

```bash
# Checkout from the new-pr branch (required for new apps)
git fetch origin new-pr
git checkout -b add-linux-armoury origin/new-pr
```

### 5. Add Your Files

```bash
# Create app directory
mkdir -p com.github.th3cavalry.linux-armoury

# Copy files from the prepared submission directory
cp -r /path/to/Linux-Armoury/flathub-submission/* \
   com.github.th3cavalry.linux-armoury/

# Add and commit
git add com.github.th3cavalry.linux-armoury/
git commit -m "Add com.github.th3cavalry.linux-armoury"
git push origin add-linux-armoury
```

### 6. Create Pull Request

1. Go to your fork on GitHub
2. Click "Compare & pull request"
3. **Base repository**: `flathub/flathub`
4. **Base branch**: `new-pr`
5. **Title**: `Add com.github.th3cavalry.linux-armoury`
6. **Description**: Use the template below

```markdown
## Application Information
- Name: Linux Armoury
- Description: GTK4 control center for ASUS ROG laptops
- Version: 0.6.2
- License: GPL-3.0-or-later
- Homepage: https://github.com/th3cavalry/Linux-Armoury

## Testing
- [x] Built and tested locally
- [x] Desktop file validated
- [x] Application runs without errors

## Notes
Linux Armoury is a power management and control center specifically designed for ASUS ROG laptops. It provides:
- Power profile management (TDP control 10W-90W)
- Display refresh rate management (30Hz-180Hz)
- System monitoring and status
- GTK4/libadwaita interface

The application requires system-level permissions for hardware control via D-Bus and polkit.
```

7. Submit the pull request

## What Happens Next

1. **Automated Checks**: Flathub's CI will automatically build and test your submission
2. **Manual Review**: Flathub maintainers will review your app (usually within a few days)
3. **Feedback**: They may request changes - just update your branch and push
4. **Approval**: Once approved, Flathub creates a dedicated repository for your app
5. **Access**: You'll receive write access to manage future updates

## After Approval

Once approved, you'll have your own repository at:
`https://github.com/flathub/com.github.th3cavalry.linux-armoury`

For updates, just push changes to that repository - builds happen automatically!

## Need Help?

- **Full Guide**: See `docs/FLATHUB_SUBMISSION.md` for detailed instructions
- **Flathub Docs**: https://docs.flathub.org/
- **Flathub Discourse**: https://discourse.flathub.org/
- **Matrix**: #flathub:matrix.org

## Files Included in Submission

The preparation script includes:
- `com.github.th3cavalry.linux-armoury.yml` (Flatpak manifest)
- `com.github.th3cavalry.linux-armoury.desktop` (Desktop file)
- `com.github.th3cavalry.linux-armoury.metainfo.xml` (AppData)
- `com.github.th3cavalry.linux-armoury.svg` (Icon)
- `requirements.txt` (Python dependencies)
- `flatpak-wheels/` (Vendored Python wheels)
- `README.md` and `LICENSE` (Documentation)

All files follow Flathub's requirements and best practices!

---

**Ready to go!** Just follow the steps above and you'll have Linux Armoury on Flathub soon. 🚀
