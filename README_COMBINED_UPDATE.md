# Career Hub — complete copy-and-paste update

This is a consolidated upgrade for the existing GitHub repository (not a fresh-install package). It includes the Complete Applicant Upgrade, the Automatic Load Update, the Automatic Tracker Filter Update, and a redesigned browser/app icon. The automatic load update supersedes the earlier automatic backup patch.

## Installation
1. In Career Hub, export your workspace as a precaution. Pull the latest repository in GitHub Desktop.
2. Extract this ZIP. Copy its contents into the root of the existing repository, merging the `site`, `tests` and `.github` folders; replace matching files. Do not delete the old repository or site folder. Make sure hidden `.github` files are included. No existing data needs to be deleted.
3. The archive deliberately does not include active `site/cloud-config.js`, `site/config.js`, `site/feedback-config.js`, `site/alerts-config.js`, `site/vacancies.json`, or `employer_sources.json`, so the existing Firebase connection, preferences and vacancy data are not overwritten. Keep those files. If the optional `site/alerts-config.js` is absent, copy its example into that location (alerts off by default). Config examples are not live settings. Keep other existing files and custom settings.
4. Commit and push to main. The existing GitHub Pages Actions workflow validates, refreshes vacancy data and deploys the site. No Firebase changes are required for the automatic backup/load, tracker filter or favicon changes. If you have never installed the Complete Applicant Upgrade, review its separate instructions for optional new Firestore permissions. Do not replace custom live Firebase rules merely for this update.
5. After deployment, refresh the website. The new service worker and versioned icon URLs help refresh assets; a previously cached browser icon may need a fresh tab or browser restart. Do not clear browser storage without exporting your data first.

## Included changes
- Navy and white career briefcase logo with a teal rising arrow; SVG, multi-resolution ICO, PNG, Apple touch icon, PWA and separate maskable icon. Updated generated SEO pages and offline cache.
- Automatic cloud restore at sign-in when safe, automatic changed-data backups every 30 seconds for verified signed-in users, and conflict safeguards. Manual controls remain.
- Tracked vacancies are excluded from the default vacancy view and count; the optional checkbox includes tracked roles. Removing a tracked role makes it eligible to reappear.
- All prior applicant features, assessments, hourly search, closed-vacancy filtering and admin features from the Complete Applicant Upgrade remain.

## Validation
Offline release checks, browser tracker tests using simulated local storage, and favicon file/reference checks passed. Live Firebase, GitHub Actions deployment, and browser-specific icon caching on the hosted site were not tested.
