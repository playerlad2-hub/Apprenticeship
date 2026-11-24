# Career Hub — Cloud Accounts and Backups

This release uses Firebase Authentication and Cloud Firestore instead of Supabase for account backups. It preserves the hourly free-first vacancy workflow, applicant tools, 78 original assessment practice modules, local storage, optional Support/donation link and GitHub Issues feedback. Guest mode and file export/import work without any account service.

## Update your existing GitHub Pages repository

1. Export a local backup through Account and keep it private. Never commit the backup file.
2. Fetch and pull your repository in GitHub Desktop. Extract the ZIP into the repository root. Preserve `site/config.js` (including your donation link), `site/vacancies.json`, any custom `employer_sources.json` entries and `site/feedback-config.js` if previously configured. The new `site/cloud-config.js` is a separate file.
3. Commit and push. Run **Hourly vacancy search and publish** in Actions if desired. Your existing Pages address and hourly schedule stay the same. Refresh after deployment.

## One-time Firebase setup (free Spark plan)

Use an eligible Google account. If the service requires an adult account owner, arrange this with a parent or guardian. Do not enable billing or upgrade to Blaze. Free usage quotas apply; if exceeded, cloud operations can stop until quota resets. You do not need Cloud Storage, Cloud Functions, Analytics or a paid server.

1. Open https://console.firebase.google.com/ and create a Firebase project (e.g. Career Hub). Disable optional Google Analytics if you do not need it. Keep the Spark plan.
2. Open **Build → Authentication → Get started → Sign-in method**. Enable **Google**, select the required support email and save. A user's first Google sign-in creates their account; subsequent sign-ins reuse it.
3. In Authentication **Settings → Authorized domains**, add your actual GitHub Pages hostname (e.g. `your-username.github.io`, not the full URL or repository path). If you use a custom domain, add it as well.
4. Open **Build → Firestore Database → Create database**. Use the Standard edition, the default database, and an appropriate available EU location. Start in production mode (not open test mode).
5. Open the Firestore **Rules** tab. Replace the rules with the complete contents of `firestore.rules` from this repository and click **Publish**. These rules allow only a verified-email, signed-in user to get, write or delete the single backup belonging to their own Firebase UID. Listing all backups and accessing other users' documents are denied. No public database access is granted. Do not deploy with `allow read, write: if true`.
6. In Project overview or **Project settings → General → Your apps**, register a web app (`</>`). Do not enable Firebase Hosting; GitHub Pages continues hosting your website. Copy the generated Firebase web configuration object (not a service-account key). Open `site/cloud-config.js` in GitHub and replace its placeholder object with the generated object, retaining `window.CAREER_FIREBASE_CONFIG =` at the beginning. Example:

```js
window.CAREER_FIREBASE_CONFIG = {
  apiKey: 'YOUR_PUBLIC_WEB_API_KEY',
  authDomain: 'YOUR_PROJECT.firebaseapp.com',
  projectId: 'YOUR_PROJECT',
  appId: 'YOUR_WEB_APP_ID'
};
```

Keep the other fields supplied by the console if present. The web configuration is public by design; never publish admin/service-account keys, passwords, recovery codes or payment credentials. The Firestore rules, not the API key, control private data access.

7. Commit the config change and let GitHub deploy. Open Career Hub → Account → Continue with Google. Allow the popup. If it fails, check that Google sign-in and the correct authorised hostname were saved.
8. Add a harmless test task, open Account, click **Save to cloud**, then approve the confirmation. Sign in using the same Google account in a different browser profile, select **Restore from cloud**, and confirm merging. Verify the test task appears. Use a second test account to check its backup is separate. In Firestore's Rules Playground, verify a different UID and unauthenticated requests cannot read or write your backup. Do this before inviting other users.

## Backup behaviour and privacy

- The current workspace stays local by default. Cloud upload, merge/restore, and deletion happen only on explicit user confirmation. Sign-in does not upload anything. No automatic sync or background uploads in this version.
- Backups include applications, manually saved vacancies, hidden roles, practice results/history, CV drafts, profile, notes, plans and other data covered by the existing backup format. Backups are private to the signed-in Firebase account under the included rules. They are not end-to-end encrypted: project administrators with privileged access can access stored data. Inform users what is collected, retention and deletion arrangements; minimise personal details and avoid sensitive information. Do not store identification documents or financial information in these tools.
- Each account has one cloud snapshot (up to 750,000 UTF-8 bytes); save replaces the previous snapshot after confirmation. A Firestore transaction rejects a conflicting remote change during save/delete. Restore merges by existing local merge rules, so deletions from another device are not propagated. Export a local JSON copy before restoring if needed.
- The guest workspace is still shared by anyone using the same browser profile. Signing out does not clear it. Use separate browser profiles on shared devices; only upload or merge workspaces that belong to you. Login uses browser session persistence. Do not publish users' backups in GitHub, Issues or public logs.
- Manage your display name, sign out, or delete your cloud backup from Account. Account deletion requests can be handled by the project administrator in Firebase Authentication after deleting the corresponding backup document. Do not promise account deletion automatically; the website only deletes backup data.
- Firebase web SDK is downloaded on demand when configured; network access and a valid account are required. Cloud service errors leave local data available. If the backup is too large or quota is exhausted, use local export/import instead.

## Feedback and vacancy reports (GitHub)

Enable repository Issues under Settings → General. Watch the repo's Issues and enable email notifications in https://github.com/settings/notifications. The workflow sets `site/feedback-repo.js` using the actual GitHub repository name when publishing. Users open a prefilled GitHub issue and submit it themselves (GitHub account required). Issues are public; do not include personal or confidential data. Feedback submissions are not stored in Firebase. An optional configured private feedback endpoint can be used instead; see `site/feedback-config.js`. Without one, do not represent feedback as private.

## Scope and limitations

Legacy Supabase login, community database, automatic synchronisation and closed-site push notifications are disabled; they are not replaced by Firebase in this release. In-app reminders continue to work while the website is open. The old SQL files are retained only for historical compatibility, and no Supabase setup is required. The optional push workflow step has been removed. Hourly vacancies, cached public listings and existing employer feeds are unchanged; some sources have restricted access and no engine guarantees complete coverage.

The package includes the new account code and rules. Local/simulated browser checks do not verify live Google OAuth, Firestore permissions or delivery from your deployed site. Follow the setup and Rules Playground checks above. All assessment practice remains independently authored, not official recruitment tests.
