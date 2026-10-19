// Free Cloudflare Worker (Cron Triggers). Every 10 min: ping /api/health so the Render free instance stays warm.
// Mondays 14:00 UTC: call the weekly rescan endpoint with the CRON_SECRET (stored as a Worker secret).
export default {
  async scheduled(event, env, ctx) {
    const base = env.BASE_URL || "https://vibecheck.itsvelocitygroup.com";
    if (event.cron === "0 14 * * 1") {
      for (let i = 0; i < 3; i++) {  // retry: the first call may hit a cold start
        const r = await fetch(base + "/api/cron/weekly", { headers: { Authorization: "Bearer " + env.CRON_SECRET } });
        console.log("weekly", r.status); if (r.ok) return;
        await new Promise(res => setTimeout(res, 30000));
      }
    } else {
      const r = await fetch(base + "/api/health"); console.log("ping", r.status);
    }
  },
};
