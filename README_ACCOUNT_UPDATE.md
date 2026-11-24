# Career Hub — email accounts and deletion (incremental update)

This patch is based on Career_Hub_Cloud_Accounts_Update. Only four application/rules files are replaced; your existing cloud-config.js, config.js, vacancies.json and other project files are not included or overwritten.

## Firebase console
1. Open your existing Firebase project > Authentication > Sign-in method. Enable Email/Password (not email-link/passwordless). Keep Google enabled. Under Authentication settings > User actions, ensure users are allowed to sign up and delete accounts. No new project or billing required.
2. Firestore Database > Rules: replace the rules with the complete contents of the included firestore.rules and Publish. This assumes the dedicated Career Hub database with only career_backups as in the previous setup. If you added other collections/rules, merge carefully rather than replacing unrelated rules. Backups are readable/writable only by the verified owner; deletion is permitted to the owner even before email verification. All other collections remain denied. Merely committing the rules to GitHub does not publish them.
3. Authentication > Templates: check verification and password reset emails. Firebase handles these links. Users return to Career Hub after following a verification link and press I have verified my email. Free email quotas apply.

## GitHub
Extract the patch into the existing repository root, replacing only site/cloud-account.js, site/cloud-account.css, site/sw.js and firestore.rules. Commit and push. Run the existing Pages deployment workflow if needed. Hard refresh after deployment. The service worker cache version is updated. Preserve your Firebase configuration.

## Account behavior
Email/password sign-up, sign-in, password reset and Google sign-in. Email must be verified before cloud backup. The Delete account option requires typing DELETE and re-authenticating with the same account. The app deletes the cloud backup first and waits for acknowledgement, then deletes the Auth account. These two operations are not atomic: if Auth deletion fails the backup is already removed and the account can be retried; if backup deletion fails, the account is retained. Do not delete an account from the admin console before deleting its backup. Close other signed-in tabs/devices before deletion to avoid concurrent writes; client-side deletion cannot guarantee cleanup of concurrent writes or administrative deletions. Local workspace, exported files and public feedback issues are not deleted. Users may clear site data in their browser separately after exporting any desired records. No password is stored by the website.

## Live test checklist
Use disposable test data: register with email, verify, save a backup, reset password, sign in again; test Google sign-in; test deletion cancellation/wrong credentials, then correct deletion. Confirm Authentication > Users no longer contains the user and Firestore > Data no longer contains their backup document. Verify with Rules Playground that another UID and an unauthenticated visitor cannot read, write or delete that backup. Test email quotas and account configuration on the deployed site. Do not store real applicant data until these tests pass.

The project remains on the free Spark plan subject to quotas. This patch does not require Cloud Functions.
