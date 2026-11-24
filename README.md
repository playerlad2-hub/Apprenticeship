# Career Hub Plus — daily vacancy search, application planning and 78 practice modules

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

The schedule remains 07:17 Europe/London daily; GitHub may delay runs or disable inactive schedules. The optional `BRAVE_SEARCH_API_KEY` repository secret is preserved when updating. Only enable search API use if your plan permits storing and redistributing results; check costs and eligibility. Never commit credentials. The live vacancy services and hosted authentication were not verified in this build environment. The existing search engine and daily workflow are preserved.

## Assessments and accessibility
78 modules across 13 provider groups, including 13 existing game simulations and 65 generated-question modules. Extended sessions default to 35–220 rounds for the original games and 50–100 for the generated-question modules; shorter modes remain available. Fresh questions and answer order, repeated-prompt avoidance within generated sessions, progressively more demanding tasks or shorter timers, and fresh worked tutorial examples. Some providers share skill formats and some tasks intentionally repeat visual stimuli or rules. No official items or psychometric scoring are reproduced; this is not a complete or exact catalogue of actual tests. Follow employer instructions and official practice resources.

The page now uses document scrolling rather than a fixed-height nested dashboard. The sidebar is sticky on desktop, mobile has a bottom navigation bar and the Day/Night game retains its split-screen design. In an isolated Chromium rendering test, desktop and 390px mobile scrolling worked; all 78 modules reached their configured extended round counts in a simulated lifecycle test, with distinct question prompts in each generated session tested. Hosted live services are unverified.

## Account sign-in (optional)
The site works in guest mode without setup. Email-link authentication and explicit private cloud backups use Supabase. If you already configured `site/config.js`, retain your values when upgrading. Do not add credentials or private data to the repository.
1. If eligible to use the service, create a Supabase project; check terms and involve a parent or guardian if required. Use the project's URL and **publishable key** only (not a secret/service-role key).
2. In Supabase SQL Editor run the included `account_setup.sql`. It creates the backup table and user-specific row-level security policies.
3. In Authentication > URL Configuration set the Site URL to your GitHub Pages URL, and add the exact deployed site URL(s), including the trailing slash and `/index.html` if used, to allowed redirects. Enable email authentication and use a magic-link email template. See https://supabase.com/docs/guides/auth/auth-email-passwordless and https://supabase.com/docs/guides/auth/redirect-urls.
4. Edit `site/config.js` to set `supabaseUrl` and `supabasePublishableKey`. Commit and push. The Sign in screen will then allow an email link request. Test sign-in, sign-out and private save/restore/delete with your own test data. Review provider limits and security before public use.
5. Backups are voluntary, not automatic sync. Signing out does not erase this device's local workspace. Use separate browser profiles on shared devices. Keep personal backups private.

## Notifications, planning and preparation
The notifications page checks for newly seen directory listings, active application deadlines, upcoming next steps and planner tasks when the website is open. Enable browser desktop alerts if desired; this is not a background push or email service. The planner supports calendar export, and the preparation area includes interview prompts, a timed practice answer, checklist, resources and a STAR evidence bank. Save searches and export/restore your local workspace via Account. Vacancy filters, hidden jobs and daily publication remain available.

## Optional donations
Support displays a donation link only when `donationUrl` in `site/config.js` is set to an existing HTTPS hosted payment page managed by an eligible account holder. If under the provider's minimum age, leave it disabled unless a parent or guardian manages it in accordance with the provider's terms. Do not collect payment details in the HTML. All tools remain free and donations are not required. The payment service has not been configured or tested.
