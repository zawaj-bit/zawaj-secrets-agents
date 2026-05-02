export default async function handler(req, res) {
              // Headers CORS — obligatoire pour Safari iOS (preflight + requêtes réelles)
  res.setHeader('Access-Control-Allow-Origin', '*');
              res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
              res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Preflight OPTIONS — Safari envoie ça avant chaque POST cross-origin
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
                  reqBody.model = 'claude-haiku-4-5-20251001';
                  reqBody.stream = true;

                console.log('Model:', reqBody.model, 'Stream:', reqBody.stream, 'Messages:', reqBody.messages?.length);

                const response = await fetch('https://api.anthropic.com/v1/messages', {
                                  method: 'POST',
                                  headers: {
                                                      'Content-Type': 'application/json',
                                                      'x-api-key': apiKey,
                                                      'anthropic-version': '2023-06-01',
                                  },
                                  body: JSON.stringify(reqBody),
                });

                console.log('Anthropic status:', response.status);

                res.writeHead(response.status, {
                                  'Content-Type': response.headers.get('content-type') || 'text/event-stream',
                                  'Cache-Control': 'no-cache',
                                  'Connection': 'keep-alive',
                });

                const reader = response.body.getReader();
                  while (true) {
                                    const { done, value } = await reader.read();
                                    if (done) break;
                                    res.write(value);
                  }
                  res.end();

  } catch (error) {
                  console.error('Proxy error:', error.message);
                  try {
                                    res.writeHead(200, { 'Content-Type': 'text/event-stream' });
                                    res.write('data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Erreur serveur: ' + error.message + '"}}\n\n');
                                    res.write('data: [DONE]\n\n');
                                    res.end();
                  } catch (e) {}
  }
}
