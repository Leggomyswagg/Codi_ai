const Anthropic = require('@anthropic-ai/sdk');

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { description, target = 'website', features = [] } = req.body || {};

  if (!description || !description.trim()) {
    return res.status(400).json({ error: 'Description is required' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'ANTHROPIC_API_KEY is not configured in Vercel environment variables.' });
  }

  const client = new Anthropic({ apiKey });

  const featuresLine = features.length > 0
    ? `\nRequired features: ${features.join(', ')}`
    : '';

  const prompt = `You are Codi AI. Generate a complete, working ${target} starter project for this idea:

"${description.trim()}"
${featuresLine}

Return ONLY valid JSON (no markdown fences, no explanation text) using this exact structure:
{
  "summary": "One sentence describing what was generated",
  "files": [
    { "name": "index.html", "content": "..." },
    { "name": "style.css",  "content": "..." },
    { "name": "app.js",     "content": "..." },
    { "name": "README.md",  "content": "..." }
  ]
}

Rules:
- Every file must be complete and immediately usable
- Use modern, clean UI design with good UX and real interactivity
- No placeholder text — include realistic sample data and working functionality
- The project should work by just opening index.html in a browser (no build step)
- Link style.css and app.js from index.html with relative paths`;

  const message = await client.messages.create({
    model: 'claude-sonnet-4-6',
    max_tokens: 8000,
    system: 'You are Codi AI, an expert web developer. Always respond with valid JSON only — no markdown, no prose.',
    messages: [{ role: 'user', content: prompt }],
  });

  const raw = message.content[0].text.trim();

  let result;
  try {
    result = JSON.parse(raw);
  } catch {
    const match = raw.match(/\{[\s\S]*\}/);
    if (!match) {
      return res.status(500).json({ error: 'AI returned an unexpected format. Please try again.' });
    }
    try {
      result = JSON.parse(match[0]);
    } catch {
      return res.status(500).json({ error: 'Failed to parse generated project. Please try again.' });
    }
  }

  return res.status(200).json(result);
};
