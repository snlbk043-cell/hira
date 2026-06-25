# RCPL Campa Cola – Smart HIRA Generator (with Claude AI)

## What's inside
```
hira-site/
├── index.html                     <- your webpage (Claude button added)
├── netlify.toml                   <- tells Netlify where the function is
└── netlify/
    └── functions/
        └── claude.js              <- reads ANTHROPIC_API_KEY, calls Claude
```

## Deploy (drag & drop – easiest)
1. Go to https://app.netlify.com  ->  open your existing site.
2. Open the **Deploys** tab.
3. Drag the **whole `hira-site` folder** onto the deploy area
   ("Drag and drop your site output folder here").
   IMPORTANT: drop the FOLDER, not just index.html — the
   `netlify/functions` folder must go up too.

## Add the API key (you already did this – just confirm)
- Site configuration -> Environment variables
- Key: `ANTHROPIC_API_KEY`
- Value: your key from https://console.anthropic.com
- Scope must include **Functions** (your screenshot already shows this ✅)

## After adding the key you MUST redeploy
- Deploys -> Trigger deploy -> **Deploy site**
- (Environment variables only take effect on a NEW deploy.)

## Use it
1. Open your site, type Activity / Sub Activity rows.
2. Click **✨ Generate with Claude AI**.
3. Claude analyses each activity and fills the HIRA table.
4. Edit any cell, then Download Excel / CSV / PDF as before.

## If you still see "ANTHROPIC_API_KEY not set"
- You added the key but did NOT redeploy -> Trigger deploy again.
- Or the function folder wasn't uploaded -> re-drag the whole folder.

## Change the model (optional)
Edit `netlify/functions/claude.js`, line with `const MODEL = ...`.
