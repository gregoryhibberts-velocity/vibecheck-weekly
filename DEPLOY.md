# VibeCheck Weekly on Render (free) + Neon + Resend + Cloudflare cron
1. Neon (free): create project "vibecheck-weekly"; copy the pooled connection string -> DATABASE_URL.
2. Render (free, no card): New > Blueprint from this repo (render.yaml), fill the sync:false env vars. Add custom domain vibecheck.itsvelocitygroup.com.
3. Cloudflare DNS (zone itsvelocitygroup.com): CNAME vibecheck -> vibecheck-weekly.onrender.com, DNS only (grey cloud).
4. Cloudflare Workers (free): cd cron && npx wrangler deploy && npx wrangler secret put CRON_SECRET
5. Resend (free): add domain vibecheck.itsvelocitygroup.com, add the 3-4 records it shows (send.vibecheck MX+TXT, resend._domainkey.vibecheck TXT). EMAIL_PROVIDER=resend, EMAIL_API_KEY=re_...
6. Stripe: webhook https://vibecheck.itsvelocitygroup.com/api/stripe/webhook (checkout.session.completed, customer.subscription.deleted) -> STRIPE_WEBHOOK_SECRET.
