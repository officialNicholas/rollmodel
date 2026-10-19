// The website's few absolute values, all in one place. Every page reads them from here (and tools/site_build.py writes them into
// the pages for anyone without JavaScript). All of them are public by design: the Supabase address and key ship inside the game.
window.RM_CONFIG = Object.freeze({
  // the game's Supabase project, for the account pages (forgot, reset, confirm)
  SUPABASE_URL: 'https://nbemerxgukwwtrfgirfl.supabase.co',
  SUPABASE_KEY: 'sb_publishable_9fux5IpOiTei0HvScvqI1g_iAwSCHPc',
  // where players write to us
  SUPPORT_EMAIL: 'support@playrollmodel.com',
  // the game on the App Store (https://apps.apple.com/...). Empty: the button says "Coming soon to the App Store"
  APP_STORE_URL: '',
  // the website's own address, once the domain is bought (e.g. https://playrollmodel.com, no slash at the end). Only the share
  // previews need it (they want full addresses); every link on the site is relative. Empty: share previews use relative ones
  SITE_URL: ''
});
