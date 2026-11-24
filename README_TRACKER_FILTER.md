# Career Hub — automatic tracker exclusion

Replace `site/index.html` and `site/sw.js` in the repository, then commit and push. This patch is based on the Complete Applicant Upgrade and the Automatic Load Update. It does not replace cloud-account.js, workspace.js, configuration, or Firebase rules. If you have not installed the automatic load update, install that first.

- Find apprenticeships excludes tracked vacancies by default, including saved roles and every application status.
- Saving a role immediately removes its card from the default list. The dashboard's Untracked opportunities count excludes tracked roles too.
- The optional Show roles already in my tracker checkbox temporarily includes them. Reset filters restores the default exclusion.
- Removing an application from the tracker returns it to the normal vacancy list if it still exists and matches the other filters. Manual Hide remains independent.
- Matches by vacancy ID, or by normalized listing/application link and matching role details. For manually entered applications without a link, matches exact employer, role and location (ignoring case and repeated whitespace). Ambiguous manual entries may need the correct link or location.
- No public vacancies or private applications are deleted. Other users' listings are unaffected. Employer directories and public SEO pages remain complete.

Validated inline JavaScript and service worker syntax; exercised filtering, saving, showing tracked roles, changed feed IDs, restored local storage, removal, manual entry and dashboard count in a local Chromium test with simulated browser storage. Live Firebase and GitHub Pages deployment were not tested.
