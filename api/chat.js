export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'API key not configured' });
  }

  try {
    const reqBody = req.body || {};
    // Force model to a valid one
    if (!reqBody.model || reqBody.model.includes('claude')) {
      reqBody.model = 'claude-3-5-sonnet-20241022';
    }
    
    console.log('Calling Anthropic with model:', reqBody.model, 'messages count:', reqBody.messages?.length);

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify(reqBody)
    });

    const data = await response.json();
    console.log('Anthropic response status:', response.status, 'error:', JSON.stringify(data?.error));
    
    // Always return 200 to avoid dashboard treating API errors as connection errors
    return res.status(200).json(data);
  } catch (error) {
    console.error('Handler error:', error.message);
    return res.status(200).json({ 
      error: { type: 'api_error', message: error.message },
      content: [{ type: 'text', text: 'Erreur de connexion: ' + error.message }]
    });
  }
}
