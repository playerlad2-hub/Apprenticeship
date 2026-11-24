# Career Hub — provider-organised practice and daily vacancy updates

## Upgrade an existing GitHub Pages installation
1. On the existing website, export your personal tracker as a backup. Keep this file private; do not commit it to GitHub.
2. In GitHub Desktop, select your existing career-hub repository, click Fetch origin and then Pull origin if offered. Choose Repository > Show in Explorer.
3. Extract this ZIP. Copy its contents into the repository folder, including the hidden `.github` directory. Replace existing files when prompted. Do not delete the repository's `.git` directory. Keep the `site` folder and workflow paths unchanged.
4. In GitHub Desktop, check the changes, enter a summary such as `Upgrade Career Hub`, click Commit to main, then Push origin.
5. On GitHub, open Actions > Daily vacancy search and publish. The push should trigger a deployment. Alternatively, use Run workflow on the main branch. Check that both build and deploy finish successfully.
6. Open your existing Pages URL and hard refresh (Ctrl+F5). Your tracker and saved results should remain on the same browser and origin. Import your private backup if necessary.

## New installation
Create a public repository called `career-hub` with default branch `main`, clone it with GitHub Desktop, copy this ZIP's contents, commit and push. In repository Settings > Pages > Build and deployment > Source, select GitHub Actions. Then run the workflow manually.

## Search coverage
GOV.UK level 6 and level 7, UCAS, Open Apprenticeships, browser-accessible employer feeds, and optional wider-web discovery (51 queries). Coverage is not comprehensive. Source failures and partial data are labelled; unverified leads are not confirmed openings. Actual advertised release dates are distinct from first-discovered dates. Unknown release dates sort last. Hide/unhide preferences remain in this browser and can be included in a tracker backup.

The schedule remains 07:17 Europe/London daily; GitHub may delay runs or disable inactive schedules. The optional `BRAVE_SEARCH_API_KEY` repository secret is preserved when updating. Only enable search API use if your plan permits storing and redistributing results; check costs and eligibility. Never commit credentials. Live network and real browser rendering were not verified in the build environment. Python compilation, sample Level 6/7 parsers, JS syntax, mock-DOM rendering, hide/unhide, date sorting and the 25 added practice-module lifecycle tests passed.

## Assessments
38 practice modules grouped into seven provider categories, including 13 existing game simulations and 25 additional reasoning, numerical, attention, judgement and coding drills. These are original practice exercises; provider groupings are suggested preparation categories, not verified replicas or a comprehensive list of actual tests. Follow the instructions supplied by your employer.
