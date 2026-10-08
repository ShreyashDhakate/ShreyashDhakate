# Install your animated GitHub profile

This package is personalized for **ShreyashDhakate/ShreyashDhakate**, which already exists. It contains your GitHub-avatar portrait, real contribution data, a terminal bio, and links to your three featured projects.

## Upload from Windows

1. Extract the ZIP. Open the `github-profile` folder. Enable **View → Show → Hidden items** so `.github` is visible.
2. Open https://github.com/ShreyashDhakate/ShreyashDhakate and choose **Add file → Upload files**.
3. Drag the **contents** of `github-profile` onto the upload page: `README.md`, `profile.json`, `assets`, `data`, `scripts`, `docs`, `.github`, and `.gitignore`. Do not upload the ZIP or the enclosing `github-profile` folder.
4. Commit to `main`. The new `README.md` belongs at the repository root, and the workflow belongs at `.github/workflows/update-profile-art.yml`.
5. Open **Actions → Update profile art → Run workflow**. The profile appears at https://github.com/ShreyashDhakate after the commit. GitHub may briefly cache old images.

If drag-and-drop does not preserve `.github`, create `.github/workflows/update-profile-art.yml` through **Add file → Create new file** and paste the supplied YAML.

Your previous README is preserved in `docs/README.before.md`. Existing repository files and workflows are not included in this ZIP and should remain in place. If an older workflow writes `README.md`, adjust that specific workflow so it does not overwrite the new profile.

## Use Git instead

Clone your existing repository, copy this package's contents into the clone, and review the changes before committing:

```sh
git clone https://github.com/ShreyashDhakate/ShreyashDhakate.git
cd ShreyashDhakate
# Copy the extracted github-profile contents here, including .github.
git status
git diff -- README.md
git add README.md profile.json assets data scripts docs .github/workflows/update-profile-art.yml .gitignore
git commit -m "Build animated terminal profile"
git push origin main
```

## Edit your bio

Change `profile.json`, then regenerate using Python 3.12 or newer:

```sh
python scripts/build_profile.py
```

Keep bio values short enough to fit the card. Edit project descriptions and contact links in `README.md`. The public email is retained from your existing profile README.

To replace the portrait:

```sh
python -m pip install -r scripts/requirements-portrait.txt
python scripts/build_profile.py --portrait assets/source-photo.png
```

The portrait preprocessing removes the yellow background in your existing avatar; change that color condition in `render_portrait` if you use a different photo. No AI-generated face is used.

## Refresh behavior

- The workflow runs daily at 06:17 UTC (11:47 AM IST), after changes to the build script/bio/workflow, or when run manually.
- It uses the public GitHub contribution calendar and Python's standard library. No personal access token or hosted stats widget is required. GitHub supplies the normal built-in workflow token to commit the generated files.
- The graph displays the dates and counts returned by GitHub's public calendar, including any anonymous private-contribution counts your GitHub settings expose. It does not reveal private repository details.
- The included graph is a real snapshot. Missing counts or an incomplete response fail the build and leave the committed graph intact rather than generating invented values.
- A signed-in calendar and the public feed can expose different contribution history. If a refresh would zero at least 10 known active days and half of the overlapping active history, the renderer retains the previous snapshot and its original timestamp. Counts are never combined, padded or invented. A matching visibility is required for live updates of that saved history.
- HTML scraping depends on GitHub's markup. If it changes, the parser may need updating. The last committed SVG remains available when a refresh fails.
- SVGs use short, one-time native animations and contain no scripts, external fonts, or external image dependencies. GitHub/browser rendering and caching can affect replay; the artwork remains readable as static SVG.
- A public repository's scheduled workflow can be disabled by GitHub after prolonged repository inactivity. Re-enable it from the Actions tab if needed.

If the workflow reports a write-permission error, check **Settings → Actions → General → Workflow permissions** and applicable branch protection. The job requests `contents: write`, but repository/organization policies can override it. No changes to security settings are needed unless an actual error occurs.

## Credits

Concept inspired by Avi Vashishta's guide: https://www.avivashishta.com/blog/build-animated-github-profile-readme. The Python implementation and profile art in this package are newly written for Shreyash Dhakate.

