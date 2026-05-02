export default async function handler(req, res) {
          if (req.method !== 'POST') {
                      return res.status(405).json({ error: 'Method not allowed' });
          }

  const apiKey = process.env.ANTHROPIC_API_KEY;
          if (!apiKey) {
                      res.writeHead(200, { 'Content-Type': 'text/event-stream' });
                      res.write('data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Erreur: cle API non configuree."}}\n\n');
                      res.write('data: [DONE]\n\n');
                      return res.end();
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
                          body: JSON.stringify(reqBody)
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
              console.error('Error:', error.message);
              try {
                            res.writeHead(200, { 'Content-Type': 'text/event-stream' });
                            res.write('data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"Erreur serveur: ' + error.message + '"}}\n\n');
                            res.write('data: [DONE]\n\n');
                            res.end();
              } catch(e) {}
  }
}
