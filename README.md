# BeanLedger Marketing Site

This public repository hosts the static marketing page for BeanLedger at:

<https://beanledger.maples7.com/>

The source site was migrated from the private `Maples7/BeanLedger` repository's `docs/` directory so GitHub Pages can serve it publicly without making the app source public.

## Local Check

```bash
npm run site:lint
python3 -m http.server 4171
```

Then open <http://127.0.0.1:4171/>.

## GitHub Pages

Use repository settings:

1. Settings -> Pages.
2. Source: **Deploy from a branch**.
3. Branch: `main`, folder `/root`.
4. Custom domain: `beanledger.maples7.com`.
5. Enable HTTPS after GitHub finishes certificate provisioning.

DNS should point `beanledger.maples7.com` to `maples7.github.io` with a CNAME record.