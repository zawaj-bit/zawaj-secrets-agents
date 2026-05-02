export default async function handler(req, res) {
        if (req.method !== 'POST') {
                  return res.status(405).json({ error: 'Method not allowed' });
        }

  const apiKey = process.env.ANTHROPIC_API_KEY;
        if (!apiKey) {
                  return res.status(200).json({ content: [{ text: 'Erreur: cle API non configuree.' }] });
        }

  try {
            const reqBody = req.body;
            reqBody.model = 'claude-haiku-4-5';
            reqBody.stream = false;
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
            console.log('Anthropic status:', response.status, 'type:', data?.type);
            return res.status(200).json(data);
  } catch (error) {
            console.error('Error:', error.message);
            return res.status(200).json({ content: [{ text: 'Erreur serveur: ' + error.message }] });
  }
}
