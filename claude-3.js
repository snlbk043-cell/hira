// netlify/functions/claude.js
// Serverless proxy: keeps ANTHROPIC_API_KEY secret on the server and
// returns AI-generated HIRA rows as strict JSON for the front-end table.

const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MODEL = "claude-sonnet-4-6"; // change here if you want a different model

exports.handler = async (event) => {
  // Only allow POST
  if (event.httpMethod !== "POST") {
    return json(405, { error: "Method not allowed. Use POST." });
  }

  // 1) Check the key exists on the server
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return json(500, {
      error:
        "ANTHROPIC_API_KEY not found on server. In Netlify: Site configuration -> Environment variables -> add ANTHROPIC_API_KEY (scope: Functions), then Deploys -> Trigger deploy -> Deploy site.",
    });
  }

  // 2) Read the activities the user typed
  let payload;
  try {
    payload = JSON.parse(event.body || "{}");
  } catch {
    return json(400, { error: "Bad request body (not valid JSON)." });
  }

  const activities = Array.isArray(payload.activities) ? payload.activities : [];
  const meta = payload.meta || {};
  const style = payload.style === "single" ? "single" : "multi";

  if (activities.length === 0) {
    return json(400, { error: "No activities provided. Enter at least one Activity / Sub Activity." });
  }

  // 3) Build the prompt
  const system = buildSystemPrompt(style);
  const userMsg = buildUserPrompt(activities, meta, style);

  // 4) Call Anthropic
  try {
    const resp = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: {
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: 8000,
        system,
        messages: [{ role: "user", content: userMsg }],
      }),
    });

    const data = await resp.json();

    if (!resp.ok) {
      return json(resp.status, {
        error: data?.error?.message || "Anthropic API returned an error.",
        details: data,
      });
    }

    // 5) Extract text and parse the JSON the model returned
    const text = (data.content || [])
      .filter((b) => b.type === "text")
      .map((b) => b.text)
      .join("\n");

    const rows = parseRows(text);
    if (!rows) {
      return json(502, {
        error: "Model did not return valid JSON. Try again or reduce the number of activities.",
        raw: text.slice(0, 1500),
      });
    }

    return json(200, { rows });
  } catch (err) {
    return json(500, { error: "Server error calling Anthropic: " + err.message });
  }
};

/* ---------- helpers ---------- */

function json(statusCode, obj) {
  return {
    statusCode,
    headers: { "content-type": "application/json" },
    body: JSON.stringify(obj),
  };
}

function buildSystemPrompt(style) {
  return `You are a senior EHS / process-safety engineer preparing a formal, audit-grade HIRA (Hazard Identification & Risk Assessment) for an Indian Carbonated Soft Drink / beverage (Campa Cola, RCPL) manufacturing plant.

You understand: KHS/Krones filling & labelling lines, CIP with caustic/acid, CO2 bulk storage & unloading, syrup room, boiler (IBR), compressors, WTP/ETP/STP/ZLD, HT/MCC electrical, HSD/LDO yard, warehouse/forklift, confined space, work at height, LOTO, hot work, and contractor work.

For each activity given, identify the real hazard pathway: hazard source/energy -> undesired event -> impact. Use a 5x5 risk matrix (S = severity 1-5, L = likelihood 1-5, Risk = S x L). Risk Level: >=16 Extreme, >=10 High, >=5 Medium, else Low. After additional controls give residual S, L (residual must be lower).

Cite realistic Indian legal/standard references where relevant: Factories Act 1948, AP/Karnataka Factories Rules, IBR, SMPV(U)/PESO for CO2, IS 3043 earthing, IS 2925, BOCW Act, ISO 45001:2018, NBC 2016, CGWA/CPCB for effluent.

Output STYLE = ${style === "single" ? "ONE combined row per activity (merge the main hazards)." : "MULTIPLE rows per activity - one row for each distinct major hazard event."}

Return ONLY valid JSON. No markdown, no backticks, no commentary. Schema:
{"rows":[{
"area":string,"activity":string,"sub":string,
"situation":string,"source":string,"event":string,"impact":string,
"persons":string,"existing":string,
"s":number,"l":number,
"addControls":string,
"rs":number,"rl":number,
"ppe":string,"permit":string,"refs":string,"owner":string,
"evidence":string
}]}

Rules: s,l,rs,rl are integers 1-5. Keep each text field concise but specific to a beverage plant (no generic filler). Do not include risk scores or levels in text fields (they are computed). Maximum 60 rows total.`;
}

function buildUserPrompt(activities, meta, style) {
  const lines = activities
    .map(
      (a, i) =>
        `${i + 1}. Area/Equipment: ${a.area || "(infer)"} | Activity: ${a.activity || ""} | Sub-activity: ${a.sub || ""} | Job Mode: ${a.mode || "Routine Operation"} | Site condition: ${a.condition || "(none given)"}`
    )
    .join("\n");

  return `Site/Unit: ${meta.site || "RCPL Kurnool – Campa Cola"}
Department: ${meta.dept || ""}
Prepared by: ${meta.prepared || "EHS Team"}
Risk philosophy: ${meta.riskMode || "realistic"}

Generate a HIRA (${style} style) for these activities:
${lines}

Return ONLY the JSON object described in your instructions.`;
}

function parseRows(text) {
  if (!text) return null;
  let t = text.trim();
  // strip code fences if the model added them despite instructions
  t = t.replace(/^```(?:json)?/i, "").replace(/```$/i, "").trim();
  // grab the outermost JSON object
  const start = t.indexOf("{");
  const end = t.lastIndexOf("}");
  if (start === -1 || end === -1) return null;
  try {
    const obj = JSON.parse(t.slice(start, end + 1));
    if (Array.isArray(obj.rows)) return obj.rows;
    if (Array.isArray(obj)) return obj;
    return null;
  } catch {
    return null;
  }
}
