# Career Hub — all-in-one update (24 November 2026)

## Copy and paste into your existing GitHub repository
1. Pull the latest version of your repository, and optionally export your personal workspace from Career Hub's Account page.
2. Extract this ZIP. Copy the contents (including the `site` and hidden `.github` folders) into the **root** of your existing repository. Merge folders and replace matching files. Do not delete the existing repository contents or replace the entire `site` directory with an empty directory first.
3. Keep your existing `site/cloud-config.js`, `site/config.js`, `site/feedback-config.js`, `site/alerts-config.js`, `site/vacancies.json`, custom `employer_sources.json`, and any existing credentials or custom workflows. The first six files are intentionally excluded to preserve your installation. `config-examples/` contains optional templates, not active configurations; only use them if a required configuration is genuinely missing. Do not paste private credentials into frontend files.
4. Commit and push. The existing hourly GitHub Actions workflow tests and deploys the site. After deployment, hard-refresh the website (Ctrl+F5 on Windows). The new versioned icon links and service worker cache help browsers pick up the new icon.

## Included
- Complete Applicant Upgrade and its existing site features, including closed vacancy filtering and assessment practice.
- Automatic cloud backup while signed in (checks for changes every 30 seconds); automatic restore on sign-in when safe, with conflict protection and manual options.
- Tracked vacancies are excluded by default from the main vacancy list and untracked dashboard count; optional show-tracked checkbox. Removing an application can make it visible again.
- New Career Hub navy/teal briefcase and growth-arrow icon: SVG, ICO, PNG, Apple touch icon and installable app icons. Generated vacancy, guide and employer pages use the same icon.

## Firebase and data
No Firebase rule changes are required for the new backup, load, filter or icon features beyond your existing working account setup. The `config-examples/firestore.rules.example` file from the earlier Complete Applicant Upgrade is provided as a reference; do not publish it over custom live rules simply to install this update. The earlier major upgrade's optional admin and private feedback features require their appropriate rules if you never enabled them. Copying website files does not itself delete Firebase accounts, backups or local workspace data. Existing local/cloud conflicts still require manual resolution. For actual live validation, test sign-in and backup/restore with two browser profiles using a test account.

## Checks
Offline release tests (all JavaScript syntax checks, generated pages, URL safety and closed-vacancy sitemap) pass. The account scripts match the automatic loading release exactly. Live Firebase and GitHub Pages deployment are not verified here.
