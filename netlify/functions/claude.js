// netlify/functions/claude.js  (faster, timeout-safe version)
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MODEL = "claude-haiku-4-5-20251001";
const MAX_ACTIVITIES = 1;   // one at a time keeps each call fast and under the time limit
const MAX_TOKENS = 900;

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") return json(405, { error: "Use POST." });

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) return json(500, { error: "ANTHROPIC_API_KEY not set on the server." });

  let payload;
  try { payload = JSON.parse(event.body || "{}"); }
  catch { return json(400, { error: "Bad request body." }); }

  let activities = Array.isArray(payload.activities) ? payload.activities : [];
  const meta = payload.meta || {};
  const style = payload.style === "single" ? "single" : "multi";
  if (activities.length === 0) return json(400, { error: "Enter at least one Activity." });

  let trimmed = false;
  if (activities.length > MAX_ACTIVITIES) { activities = activities.slice(0, MAX_ACTIVITIES); trimmed = true; }

  const system = buildSystemPrompt(style);
  const userMsg = buildUserPrompt(activities, meta, style);

  // Abort before Netlify's hard timeout so we always return clean JSON, never an HTML error page
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 9500);

  try {
    const resp = await fetch(ANTHROPIC_URL, {
      method: "POST",
      signal: controller.signal,
      headers: {
        "x-api-key": apiKey,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        system,
        messages: [{ role: "user", content: userMsg }],
      }),
    });
    clearTimeout(timer);

    const data = await resp.json();
    if (!resp.ok) {
      return json(resp.status, { error: data?.error?.message || "Anthropic API error." });
    }

    const text = (data.content || []).filter(b => b.type === "text").map(b => b.text).join("\n");
    const rows = parseRows(text);
    if (!rows) return json(502, { error: "AI response could not be parsed. Try fewer activities." });

    return json(200, { rows, trimmed, processed: activities.length });
  } catch (err) {
    clearTimeout(timer);
    if (err.name === "AbortError") {
      return json(504, { error: "AI took too long. Please generate fewer activities at a time (1-2), then add more." });
    }
    return json(500, { error: "Server error: " + err.message });
  }
};

function json(statusCode, obj) {
  return { statusCode, headers: { "content-type": "application/json" }, body: JSON.stringify(obj) };
}

function buildSystemPrompt(style) {
  return `You are a senior EHS / process-safety engineer writing an audit-grade HIRA for an Indian Campa Cola / RCPL carbonated soft drink plant (KHS/Krones lines, CIP caustic/acid, CO2 bulk, boiler/IBR, WTP/ETP/STP, electrical, forklift, confined space, work at height, contractor work).

For each activity: hazard source/energy -> undesired event -> impact. Use a 5x5 matrix (S,L 1-5; Risk=SxL; >=16 Extreme, >=10 High, >=5 Medium else Low). After controls give lower residual S,L. Cite real Indian refs where relevant (Factories Act/Rules, IBR, SMPV(U)/PESO, IS 3043, BOCW, ISO 45001, NBC 2016).

STYLE = ${style === "single" ? "ONE combined row per activity." : "one row per distinct major hazard (MAXIMUM 3 rows total)."}
Be concise and specific. Return ONLY valid JSON, no markdown:
{"rows":[{"area":"","activity":"","sub":"","situation":"","source":"","event":"","impact":"","persons":"","existing":"","s":1,"l":1,"addControls":"","rs":1,"rl":1,"ppe":"","permit":"","refs":"","owner":"","evidence":""}]}
s,l,rs,rl are integers 1-5. Maximum 3 rows total. Keep every field short (one line each).`;
}

function buildUserPrompt(activities, meta, style) {
  const lines = activities.map((a, i) =>
    `${i + 1}. Area: ${a.area || "(infer)"} | Activity: ${a.activity || ""} | Sub: ${a.sub || ""} | Mode: ${a.mode || "Routine"} | Condition: ${a.condition || "(none)"}`
  ).join("\n");
  return `Site: ${meta.site || "RCPL Kurnool - Campa Cola"} | Dept: ${meta.dept || ""} | By: ${meta.prepared || "EHS Team"}
Generate a ${style}-style HIRA for:
${lines}
Return ONLY the JSON object.`;
}

function parseRows(text) {
  if (!text) return null;
  let t = text.trim().replace(/^```(?:json)?/i, "").replace(/```$/i, "").trim();
  const s = t.indexOf("{"), e = t.lastIndexOf("}");
  if (s === -1 || e === -1) return null;
  try {
    const obj = JSON.parse(t.slice(s, e + 1));
    return Array.isArray(obj.rows) ? obj.rows : (Array.isArray(obj) ? obj : null);
  } catch { return null; }
}
