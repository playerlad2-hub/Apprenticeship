# Public vacancy interface update

Removed the legacy search coverage screen, source list and management UI. The vacancy page retains only its compact refresh and freshness indicator. Hourly collection, direct application URLs, existing account settings and vacancy data remain unchanged. Frontend asset versions were updated to prevent stale scripts.

# Applicant-focused update — deployment notes

This release removes the search-coverage page, source lists and external directory shortcuts from the public vacancy interface. A small refresh indicator retains the publication time and warns if results may be incomplete. Detailed hourly search diagnostics remain in the GitHub Actions logs. The search engine, employer feeds and cron schedule are unchanged.

New **My next steps** area: application pipeline counts, upcoming and overdue actions, skills evidence checklist, interview and assessment reflection journal, monthly living-cost budget planner, offer checklist and editable recruiter message templates. New personal data is stored locally, included in existing private backup exports and optional cloud backups. It is not included in the public vacancies database.

## Update an existing deployment

1. Export a private backup using the Account page. Do not commit the backup to a public repository.
2. Fetch and pull in GitHub Desktop. Extract this ZIP over the existing repository, retaining your deployed `site/config.js` and `site/vacancies.json`. The existing Supabase and donation settings should not be overwritten.
3. Commit and push. Check the Actions run; after deployment refresh the same website.

Tested with isolated Chromium and simulated offline network: navigation, hidden diagnostics, skills checklist, journal, budget arithmetic, backup payload, templates and mobile scrolling. No change to live authentication or search engine was made.

---

## Monzo donation update

The supplied config.js includes the requested Monzo.me payment link. Confirm with Monzo that the link is suitable for public website donations before publishing. If you already have a configured Supabase account, preserve your deployed config.js and change only donationUrl to the value in the included config.js; otherwise the included config.js can replace your unconfigured file. Preserve site/vacancies.json. Sign-in still requires Supabase setup. No payment processing is performed by Career Hub.

# Career Hub Next — degree-apprenticeship applicant workspace

## Upgrade an existing GitHub Pages installation
1. On the existing website, export your personal tracker as a backup. Keep this file private; do not commit it to GitHub.
2. In GitHub Desktop, select your existing career-hub repository, click Fetch origin and then Pull origin if offered. Choose Repository > Show in Explorer.
3. Extract this ZIP. Copy its contents into the repository folder, including the hidden `.github` directory. Replace existing files when prompted, EXCEPT your configured `site/config.js` and existing `site/vacancies.json` (save copies before replacing anything, and restore them afterwards). Do not delete the repository's `.git` directory. Keep the `site` folder and workflow paths unchanged.
4. In GitHub Desktop, check the changes, enter a summary such as `Upgrade Career Hub`, click Commit to main, then Push origin.
5. On GitHub, open Actions > Hourly vacancy search and publish. The push should trigger a deployment. Alternatively, use Run workflow on the main branch. Check that both build and deploy finish successfully.
6. Open your existing Pages URL and hard refresh (Ctrl+F5). Your tracker and saved results should remain on the same browser and origin. Import your private backup if necessary.

## New installation
Create a public repository called `career-hub` with default branch `main`, clone it with GitHub Desktop, copy this ZIP's contents, commit and push. In repository Settings > Pages > Build and deployment > Source, select GitHub Actions. Then run the workflow manually.

## Free hourly search — no paid API calls
The workflow searches GOV.UK Level 6/7 public results, UCAS, Open Apprenticeships and 11 configured employer boards from the server. It does not call Brave even if an old repository secret exists. Standard GitHub-hosted Actions runners and Pages are available free for eligible public repos, subject to GitHub usage and acceptable-use limits. The hourly schedule runs at minute 17 of each hour (UTC); delays and inactivity suspension are possible. No subscription or payment method is needed for the default search. The live data sources are not end-to-end verified in this build environment. Check their terms and publication rights before enabling any public feed on a public site.

### Add more employers (free public feeds)
Edit `employer_sources.json` on GitHub. The registry ships with ten SmartRecruiters boards and one Greenhouse board; these are not a claim that every employer currently has a degree apprenticeship. Append actual board identifiers from employers that offer public vacancy syndication. The server adapters support SmartRecruiters (`smart`), Greenhouse (`greenhouse` or `greenhouse-eu`), Lever (`lever` or `lever-eu`), Ashby (`ashby`), Personio XML (`personio` or `personio-de`) and employer-provided Recruitee XML (`recruitee-xml`, with `url` field, only on a permitted Recruitee subdomain). Example registry entry for an existing seed: `{"type":"smart","slug":"PAConsulting","name":"PA Consulting"}`. Each source is checked hourly and has its own status; unknown levels are leads, not confirmed degree roles. Public ATS access is not a licence to republish proprietary descriptions. Only enable sources that allow your intended reuse. No access-control bypasses; the engine reports partial/failed sources and retains recent cached leads for up to 14 days (past deadlines removed). URLs are deduplicated on the server; separate URLs for the same role may still appear. The registry is bounded to 100 entries per run. Increase the workflow timeout or split the workload if adding many employers; do not use paid runners.

### Sources that require a direct search
These sites may be consulted manually outside Career Hub: Higherin, Gradcracker, Not Going To Uni, GetMyFirstJob, Amazing Apprenticeships, Prospects, Find Apprenticeships, Scotland, Wales, Indeed, Reed, LinkedIn, Totaljobs, plus targeted searches for Workday, SuccessFactors, Oracle Recruiting, Taleo, Workable and the public feed platforms. These links are **manual**, not automated integrations. Follow source rules, and import an individual vacancy manually when found. A free unrestricted general web index is not provided by GitHub Actions. Automatic national and employer feed coverage is broader than before, but cannot guarantee every vacancy or discover every unlisted employer. The official DfE Display Advert API is another option if you obtain an approved unfiltered key; this build uses the public search pages instead and does not claim to use that API.

## New applicant toolkit
- Qualifications: enter up to four A levels and optional EPQ grades. Tariff estimates are not eligibility decisions; check required subjects, GCSEs, employer requirements and the official UCAS calculator.
- CV builder: live editable plain-text preview and local draft export. Add only your own evidence; private data never belongs in the repository.
- Weekly plan: choose a flexible weekly application goal and review recorded deadlines and preparation tasks.
- Compare roles: select Compare on a vacancy card to compare up to four opportunities. Unknown pay, training providers and other details remain marked as unpublished.
- Application workspace: use Workspace on a tracker row to save a role-specific checklist, research, draft responses, assessment provider, interview questions and feedback.
- Additional filters: choose an intake year, location keyword or minimum annual salary. Unknown start dates can be included. Salary filtering excludes unknown and non-annual figures; quoted pay may be a range or conditional on the advert.
- Search reliability: source diagnostics remain in the hourly workflow logs, not in the public website.
- Account and backup: local JSON export/import and optional private cloud backup now include the new toolkit data. The previously configured public Supabase and donation settings should be preserved in config.js. Nothing is uploaded without an explicit cloud backup action.

Toolkit interaction and mobile scrolling tests passed using an isolated Chromium page with mocked local storage and network unavailable. Python syntax, sample feed enrichment and URL canonicalisation tests passed. Live sources, account sign-in and payment processing have not been verified. Existing assessments are preserved rather than independently re-tested in full.

## Assessments and accessibility
78 modules across 13 provider groups, including 13 existing game simulations and 65 generated-question modules. Extended sessions default to 35–220 rounds for the original games and 50–100 for the generated-question modules; shorter modes remain available. Fresh questions and answer order, repeated-prompt avoidance within generated sessions, progressively more demanding tasks or shorter timers, and fresh worked tutorial examples. Some providers share skill formats and some tasks intentionally repeat visual stimuli or rules. No official items or psychometric scoring are reproduced; this is not a complete or exact catalogue of actual tests. Follow employer instructions and official practice resources.

The page now uses document scrolling rather than a fixed-height nested dashboard. The sidebar is sticky on desktop, mobile has a bottom navigation bar and the Day/Night game retains its split-screen design. In an isolated Chromium rendering test, desktop and 390px mobile scrolling worked; all 78 modules reached their configured extended round counts in a simulated lifecycle test, with distinct question prompts in each generated session tested. Hosted live services are unverified.

## Account sign-in (optional; free tier)
Guest mode works without accounts. Supabase manages authentication and the private backup database. If eligible, create a Free plan project without paid add-ons; check eligibility and involve a parent or guardian where required. Stay within free-tier limits. Do not commit secrets. Preserve existing `site/config.js` credentials when upgrading by copying the public URL and publishable key into the new config.

1. In your Supabase project open SQL Editor, run `account_setup.sql` (sets up a private backup table with RLS). In Authentication > URL Configuration, set Site URL to your deployed GitHub Pages URL and allow the exact redirect URL(s), including trailing slash or `/index.html` where appropriate.
2. In GitHub account Settings > Developer settings > OAuth Apps > New OAuth App, use the Career Hub deployed website as Homepage URL and the callback URL shown by Supabase for the GitHub provider as Authorization callback URL. See https://supabase.com/docs/guides/auth/social-sign-in/auth-github. Do not request additional repository access or scopes. Copy the OAuth client ID and secret only into Supabase's GitHub provider configuration; enable GitHub sign-in there. Do not put the client secret in GitHub or the public HTML.
3. Set `supabaseUrl`, `supabasePublishableKey` and `githubSignIn: true` in `site/config.js`. Only the publishable key (not secret/service-role) is safe for the frontend. Commit and push. On the site select Account > Continue with GitHub.
4. Optional Google OAuth: configure that provider separately following https://supabase.com/docs/guides/auth/social-sign-in/auth-google and set `googleSignIn: true`. Email magic links are disabled by default: Supabase's built-in SMTP only sends to project team members, so a public email login requires an appropriate SMTP service, subject to its own free-tier limits. Enable `emailSignIn: true` only when configured. See https://supabase.com/docs/guides/auth/auth-smtp.
5. Test on the deployed HTTPS site with two test accounts: sign in, save a private backup, sign out, then ensure the other account cannot read it. Cloud backups are manual save/restore/delete, not automatic sync. Local workspace stays on device after sign-out; use separate browser profiles on shared computers. Never upload a private tracker backup to GitHub. If configured incorrectly, use guest mode until fixed. Authentication and payment services are not live tested here.

## Notifications, planning and preparation
The notifications page checks for newly seen directory listings, active application deadlines, upcoming next steps and planner tasks when the website is open. Enable browser desktop alerts if desired; this is not a background push or email service. The planner supports calendar export, and the preparation area includes interview prompts, a timed practice answer, checklist, resources and a STAR evidence bank. Save searches and export/restore your local workspace via Account. Vacancy filters, hidden jobs and hourly publication remain available.

## Optional donations
All features are free, with no payment requirement. The Support page includes a hosted donation link when `donationUrl` is an existing HTTPS URL. Do not publish personal bank details, card information or payment credentials in the public repository. HTML cannot initiate or guarantee a transfer to a bank account. A bank or eligible hosted payment provider must handle payment authorisation and payouts. If you are under a provider's minimum age, arrange this with a parent or guardian in accordance with provider and bank rules; do not bypass eligibility checks. Configure the destination account privately with that provider, and use only its public hosted donation URL in `site/config.js`. If no suitable arrangement is available, leave `donationUrl` blank. Fees, payout rules and age requirements depend on the chosen service. The site does not handle money, verify donations, or store payment details.

## Hourly update
The workflow checks vacancies at minute 17 of each hour; GitHub can delay or skip scheduled runs. The public site checks for newly published data every 15 minutes while visible. The compact status bar shows update freshness without exposing source diagnostics. AJ Bell (AJBell1) is checked directly via its public SmartRecruiters board; the board identifier is confirmed by https://careers.smartrecruiters.com/AJBell1 . Live API results must be verified in Actions. No paid APIs are used; monitor public repository Actions and Pages usage limits. Preserve your configured site/config.js and site/vacancies.json when replacing files.

## Account & Support interface update
The guest account page no longer exposes developer configuration messages. It offers local export/import and access to applications. Once the existing Supabase project and a sign-in provider are configured, visitors can sign in; signed-in users can edit their display name, see their sign-in method, manage notification preferences, sign out, and save/restore/delete a private backup. Email change is offered only if email sign-in is enabled, and is subject to Supabase verification settings. Signing out does not clear the browser's local data. Support uses a heart icon and shows a donation button only when an eligible hosted payment link is configured. No payment details are stored. Preserve your deployed config.js and vacancies.json during upgrades.

## Trackr external search
Trackr is not automatically searched and is no longer shown in public vacancy-source panels. It is an external research resource, not an automated data source. Trackr's terms (https://the-trackr.com/terms-of-use/) prohibit automated extraction and using platform data to populate a competing service without the required permission. The hourly workflow does not request Trackr pages, harvest or republish Trackr listings. Contact Trackr directly about an authorised feed or integration if desired.

## Direct application links
Vacancy cards now include a one-click application button. The hourly engine preserves the original advert URL and stores a separate `applyUrl` when a public, role-specific employer link is available. Employer feeds use their published application link where supplied, otherwise the employer's own advert. For GOV.UK, the resolver checks up to 80 public vacancy detail pages per run, caches successful checks for 24 hours, and prioritises the oldest unchecked records. It does not sign in, guess application URLs, or follow arbitrary external pages. Where a direct URL cannot be found, the button is labelled View listing. Existing vacancy IDs and personal tracker data remain unchanged. The original listing may still be needed to complete applications that require the official service.

## Career planner update

The new **Career planner** section adds an application board with recorded stage changes, a month-view calendar, provider-specific practice plans, six original timed assessment-centre rehearsal exercises and an offer decision matrix. The existing tracker is the source of application status. Plans can be added to the existing task planner without duplicate task entries, and offer deadlines appear on the calendar. Scores for offers and case rehearsals are self-assessments only.

All new personal data is saved locally and included in private JSON/cloud backups when configured. No new paid services are required. The hourly vacancy workflow, direct application links, and 78 practice modules are unchanged. Search coverage diagnostics remain out of the public interface.

### Updating an existing deployment

Export your personal tracker backup first. Pull your current repository in GitHub Desktop, then copy these files into the repository, preserving your existing `site/config.js` and `site/vacancies.json`. Commit, push, and refresh the site after deployment. Do not upload personal backup files to GitHub. Browser interaction tests use isolated HTML rendering and sample vacancy data; they do not verify live retrieval, sign-in or payments.

## Application studio and refinement update

Application studio provides four connected tools: a searchable application answer bank with word-limit feedback, STAR evidence references, duplication, text downloads and up to 12 previous revisions per answer; a recruiter contact log with follow-up tasks connected to the existing planner/calendar; application insights based on recorded stages and submission dates; and filterable practice session history with CSV export. Existing latest practice scores are imported as previous latest results where timestamps exist; older overwritten scores cannot be recovered. Future completed sessions are recorded (up to 1,000). Practice results are not official scores or hiring predictions. Answers, contact records and practice history are included in private backups. Notification preferences are restored without automatically enabling desktop alerts. The sidebar and dialogs support scrolling, keyboard focus is clearer, and the new layouts fit mobile screens.

Upgrade: export your private backup; extract the ZIP into your existing repository, preserving `site/config.js` and `site/vacancies.json`; commit and push. Keep the existing public website address. Do not commit personal backups. No new services or paid APIs are required. The hourly search schedule and source integrations, authentication, donation setup, and 78 practice modules are unchanged. Tested the new features in isolated Chromium using sample data and mocked storage, without live network services: answer editing and revision history, word counts, contact/reminder completion, insights, practice record capture, backup restoration, desktop layout, and 390px mobile scrolling. Live retrieval and external services were not retested.


## Organised navigation update
The sidebar now groups Overview, Applications, Preparation and Personal tools, with unique icons and a matching mobile More menu. Search Coverage is excluded. For this navigation-only update, replace `site/index.html` and add `site/navigation.js` and `site/navigation.css`. Preserve your existing config and vacancy database.


## Visual CV and Direction update
The visual CV editor offers three templates, colour choices, reorderable sections, live document preview, HTML/plain-text export and browser print/save-as-PDF. Existing CV drafts are retained. The Direction game now generates both centre and off-centre X signals. Any X anywhere means withhold a response until the timer ends; otherwise use Q/P for the centre arrow. No arrow is highlighted. The tutorial includes an outside-X example. The 90/220-round modes remain. Preserve `site/config.js` and `site/vacancies.json` when deploying.
