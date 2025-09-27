#!/usr/bin/env python3
"""
Quick HTTP test server - Access via browser
Run: python quick_test_server.py
Then go to: http://localhost:8080
"""
import os
import sys
import django
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from router_agent.agent import ROUTER_AGENT

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>AI Agent Tester</title>
                <style>
                    body { font-family: Arial; margin: 40px; }
                    .container { max-width: 600px; }
                    input, textarea { width: 100%; padding: 10px; margin: 10px 0; }
                    button { background: #007cba; color: white; padding: 12px 24px; border: none; border-radius: 4px; }
                    .result { background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 4px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🤖 AI Agent Tester</h1>
                    <form id="testForm">
                        <textarea id="requestText" placeholder="Enter emergency request..." rows="3"></textarea>
                        <button type="submit">Test Router Agent</button>
                    </form>
                    <div id="result"></div>
                </div>

                <script>
                document.getElementById('testForm').onsubmit = async function(e) {
                    e.preventDefault();
                    const text = document.getElementById('requestText').value;
                    const result = document.getElementById('result');

                    if (!text.trim()) {
                        result.innerHTML = '<div class="result">❌ Please enter a request</div>';
                        return;
                    }

                    result.innerHTML = '<div class="result">🤖 Processing...</div>';

                    try {
                        const response = await fetch('/test', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({request: text})
                        });

                        const data = await response.json();

                        result.innerHTML = `
                            <div class="result">
                                <h3>✅ Results:</h3>
                                <p><strong>📂 Category:</strong> ${data.category || 'Unknown'}</p>
                                <p><strong>⚡ Urgency:</strong> ${data.urgency || 'Unknown'}</p>
                                <p><strong>🎯 Confidence:</strong> ${(data.confidence || 0).toFixed(2)}</p>
                                <p><strong>🧠 Reasoning:</strong> ${data.reasoning || 'No reasoning'}</p>
                            </div>
                        `;
                    } catch (error) {
                        result.innerHTML = `<div class="result">❌ Error: ${error}</div>`;
                    }
                };
                </script>
            </body>
            </html>
            """

            self.wfile.write(html.encode())

    def do_POST(self):
        if self.path == '/test':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode())

                request_text = data.get('request', '')

                # Test router agent
                result = ROUTER_AGENT.run(request_text)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                response = json.dumps(result)
                self.wfile.write(response.encode())

            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()

                error_response = json.dumps({'error': str(e)})
                self.wfile.write(error_response.encode())

if __name__ == "__main__":
    server = HTTPServer(('localhost', 8080), TestHandler)
    print("🚀 Test server running at http://localhost:8080")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        server.shutdown()