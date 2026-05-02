export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(200).json({ content: [{ text: 'Erreur: clé API non configurée sur le serveur.' }] });
  }

  try {
    const reqBody = req.body;
    // Force model if not provided
    if (!reqBody.model) {
      reqBody.model = 'claude-3-5-sonnet-20241022';
    }
    console.log('Model:', reqBody.model, 'Messages:', reqBody.messages?.length);

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(reqBody)
    });

    const data = await response.json();
    console.log('Anthropic status:', response.status, 'error:', data?.error);
    // Always return 200 so dashboard doesn't show connection error
    return res.status(200).json(data);
  } catch (error) {
    console.error('Error:', error.message);
    return res.status(200).json({ content: [{ text: 'Erreur serveur: ' + error.message }] });
  }
}
