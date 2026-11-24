// Public website configuration. Only public/publishable keys belong here.
// Do not include service_role keys, passwords, SMTP credentials or bank details.
window.CAREER_CONFIG = {
  supabaseUrl: '',
  supabasePublishableKey: '',
  githubSignIn: true, // enable corresponding OAuth provider in Supabase before use
  googleSignIn: false,
  emailSignIn: false, // requires a configured email service for general public sign-ups
  donationUrl: '' // optional HTTPS hosted donation page; approved eligible account holder
};
