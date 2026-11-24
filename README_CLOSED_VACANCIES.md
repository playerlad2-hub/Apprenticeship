# Closed vacancy update

Copy only the files in this ZIP into the existing repository. This is an incremental update on top of the email-account update; it does not include configuration, Firebase rules, personal data or the vacancy JSON. Commit, push and run the hourly workflow. Refresh the website after deployment.

Find apprenticeships defaults to All vacancies. The status dropdown also offers Hide closed / no longer listed, Closed vacancies only and No longer listed only. Other filters and hide animations are unchanged. Closed adverts have a historical link rather than an Apply now button.

The hourly job now retains records in its existing GitHub Actions cache for up to 365 days after last seen. Expired or explicitly closed roles are marked Closed. Roles absent from a successfully completed source are marked No longer listed, not definitively closed. Partial/failed sources retain previous entries as unverified. Reappearance in a fresh feed can reopen a listing. Archive coverage starts with available cached records; vacancies discarded before this update cannot necessarily be recovered. GitHub may evict its caches.

No live network or Firebase changes are required for this patch.
