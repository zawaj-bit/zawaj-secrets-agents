export default async function handler(req, res) {
            // Headers CORS — obligatoire pour Safari iOS
  res.setHeader('Access-Control-Allow-Origin', '*');
            res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
            res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Preflight OPTIONS
  if (req.method === 'OPTIONS') {
                return res.status(200).end();
  }

  if (req.method !== 'POST') {
                return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.ANTHROPIC_API_KEY;
            if (!apiKey) {
                          return res.status(500).json({ error: 'ANTHROPIC_API_KEY non configurée sur le serveur.' });
            }

  try {
                const reqBody = req.body;
                // Modèle fixé côté serveur — stream désactivé pour compatibilité mobile
              reqBody.model = 'claude-haiku-4-5-20251001';
                reqBody.stream = false;

              const response = await fetch('https://api.anthropic.com/v1/messages', {
                              method: 'POST',
                              headers: {
                                                'Content-Type': 'application/json',
                                                'x-api-key': apiKey,
                                                'anthropic-version': '2023-06-01',
                              },
                              body: JSON.stringify(reqBody),
              });

              const data = await response.json();
                return res.status(response.status).json(data);

  } catch (error) {
                console.error('Proxy error:', error.message);
                return res.status(500).json({ error: 'Erreur serveur: ' + error.message });
  }
}
