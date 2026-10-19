#!/bin/bash
# Local end-to-end run against real Postgres + mocked Stripe/ActiveCampaign/Resend.
cd "$(dirname "$0")/.."
export DATABASE_URL="postgresql://vc@/vibecheck?host=/tmp/pg&port=55432" ALLOW_PRIVATE_TARGETS=1 BASE_URL=http://localhost:3000 PORT=3000 STRIPE_PRICE_UNLOCK=price_unlock \
  CRON_SECRET=test-cron-secret STRIPE_SECRET_KEY=sk_test_mock STRIPE_WEBHOOK_SECRET=whsec_test STRIPE_PRICE_SOLO=price_solo STRIPE_PRICE_PRO=price_pro \
  STRIPE_API_BASE=http://127.0.0.1:4010 ACTIVECAMPAIGN_API_URL=http://127.0.0.1:4010/ac ACTIVECAMPAIGN_API_KEY=ac_mock ACTIVECAMPAIGN_LIST_ID=3 \
  EMAIL_PROVIDER=resend EMAIL_API_KEY=re_mock EMAIL_API_BASE=http://127.0.0.1:4010 EMAIL_FROM="AppCheck <test@localhost>"
psql -h /tmp/pg -p 55432 -U vc -d postgres -qc "DROP DATABASE IF EXISTS vibecheck" -c "CREATE DATABASE vibecheck"
rm -f tests/mock_calls.jsonl
.venv/bin/python tests/mock_services.py & M=$!
(cd fixture && python3 -m http.server 8099 --bind 127.0.0.1 >/dev/null 2>&1) & F=$!
.venv/bin/python server.py & S=$!
sleep 2; .venv/bin/python tests/e2e.py; R=$?
[ "$KEEP" = 1 ] || kill $M $F $S
exit $R
