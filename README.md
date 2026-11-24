# Career Hub — daily updates

1. Export your personal tracker from the old site. Do not upload the export to GitHub.
2. Create an empty public GitHub repository called `career-hub` with default branch `main`. Clone using GitHub Desktop, then copy all contents of this package (including `.github` and `.gitignore`) into the clone. Commit and push.
3. In GitHub repository Settings > Pages > Build and deployment > Source, select GitHub Actions.
4. In Actions, select Daily vacancy search and publish > Run workflow > main > Run workflow. After deployment, open the link in Settings > Pages.
5. Import your tracker backup locally into the new website.

The daily schedule is 07:17 Europe/London. GitHub can delay scheduled runs and may disable schedules after 60 days without repository activity.

Optional: only if you have permission to store and publicly redistribute results under your search API plan, add a repository Actions secret named BRAVE_SEARCH_API_KEY. Check costs and eligibility first. Leave it unset for no-key directory searches. Do not commit credentials.

Source failures and partial results are reported; not every employer can be found and web leads are not confirmed openings. The existing public-page parsers require live verification. Use only sources that permit your intended automated collection and publication.
