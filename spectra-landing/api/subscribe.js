export default async function handler(req, res) {
  // CORS
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(200).end();

  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const { email } = req.body ?? {};
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: "Invalid email" });
  }

  const apiKey = process.env.RESEND_API_KEY;
  const audienceId = process.env.RESEND_AUDIENCE_ID;

  if (!apiKey || !audienceId) {
    return res.status(500).json({ error: "Server misconfigured" });
  }

  // Add contact to Resend audience
  const createRes = await fetch(
    `https://api.resend.com/audiences/${audienceId}/contacts`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: email.trim().toLowerCase(),
        unsubscribed: false,
      }),
    }
  );

  const alreadyExists = createRes.status === 409;
  if (!createRes.ok && !alreadyExists) {
    const err = await createRes.json().catch(() => ({}));
    console.error("Resend error:", err);
    return res.status(500).json({ error: "Failed to subscribe" });
  }

  // Fetch total count
  let count = 0;
  try {
    const listRes = await fetch(
      `https://api.resend.com/audiences/${audienceId}/contacts`,
      { headers: { Authorization: `Bearer ${apiKey}` } }
    );
    if (listRes.ok) {
      const { data } = await listRes.json();
      count = Array.isArray(data) ? data.length : 0;
    }
  } catch {
    // count stays 0, not critical
  }

  return res.status(200).json({ success: true, count, alreadyExists });
}
