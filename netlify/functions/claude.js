// netlify/functions/claude.js  (ultra-lean: 1 activity, 1 short row, fastest model)
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";
const MODEL = "claude-haiku-4-5-20251001";
const MAX_TOKENS = 500;

exports.handler = async (event) => {
  if (event.httpMethod !== "POST") return json(405, { error: "Use POST." });
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) return json(500, { error: "ANTHROPIC_API_KEY not set on the server." });

  let payload;
  try { payload = JSON.parse(event.body || "{}"); }
  catch { return json(400, { error: "Bad request body." }); }

  let activities = Array.isArray(payload.activities) ? payload.activities : [];
  const meta = payload.meta || {};
  if (activities.length === 0) return json(400, { error: "Enter at least one Activity." });
  const a = activities[0];

  const system = `You are an EHS engineer doing HIRA for an Indian Campa Cola/RCPL soft-drink plant. For the activity, give ONE concise risk row. Use a 5x5 matrix (S,L 1-5; residual rs,rl lower). Return ONLY this JSON, no markdown, every field one short line:
{"rows":[{"area":"","activity":"","sub":"","situation":"","source":"","event":"","impact":"","persons":"","existing":"","s":3,"l":3,"addControls":"","rs":2,"rl":1,"ppe":"","permit":"","refs":"","owner":"","evidence":""}]}
Integers 1-5 for s,l,rs,rl. One row only. Be brief.`;

  const user = `Area: ${a.area || "(infer)"} | Activity: ${a.activity || ""} | Sub: ${a.sub || ""} | Mode: ${a.mode || "Routine"} | Condition: ${a.condition || "(none)"}. Site: ${meta.site || "RCPL Kurnool Campa Cola"}. Return ONLY the JSON.`;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 9800);

  try {
    const resp = await fetch(ANTHROPIC_URL, {
      method: "POST",
      signal: controller.signal,
      headers: { "x-api-key": apiKey, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({ model: MODEL, max_tokens: MAX_TOKENS, system, messages: [{ role: "user", content: user }] }),
    });
    clearTimeout(timer);

    const data = await resp.json();
    if (!resp.ok) return json(resp.status, { error: data?.error?.message || "Anthropic API error." });

    const text = (data.content || []).filter(b => b.type === "text").map(b => b.text).join("\n");
    const rows = parseRows(text);
    if (!rows) return json(502, { error: "Could not parse AI response. Try again." });
    return json(200, { rows, processed: 1 });
  } catch (err) {
    clearTimeout(timer);
    if (err.name === "AbortError") return json(504, { error: "Still too slow on the free plan. The next step is a background function." });
    return json(500, { error: "Server error: " + err.message });
  }
};

function json(statusCode, obj) {
  return { statusCode, headers: { "content-type": "application/json" }, body: JSON.stringify(obj) };
}
function parseRows(text) {
  if (!text) return null;
  let t = text.trim().replace(/^```(?:json)?/i, "").replace(/```$/i, "").trim();
  const s = t.indexOf("{"), e = t.lastIndexOf("}");
  if (s === -1 || e === -1) return null;
  try { const o = JSON.parse(t.slice(s, e + 1)); return Array.isArray(o.rows) ? o.rows : (Array.isArray(o) ? o : null); }
  catch { return null; }
}
