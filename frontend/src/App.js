import React, { useState, useEffect, useRef } from 'react';
import './index.css';

function getSessionId() {
  let sid = sessionStorage.getItem('sessionId');
  if (!sid) {
    sid = crypto.randomUUID(); // secure, RFC‑4122 v4 UUID :contentReference[oaicite:1]{index=1}
    sessionStorage.setItem('sessionId', sid);
  }
  return sid;
}

function App() {
  const [input, setInput] = useState('');
  const [chatLog, setChatLog] = useState([]);
  const [loading, setLoading] = useState(false);
  const sessionId = useRef('');

  useEffect(() => {
    sessionId.current = getSessionId();
  }, []);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setChatLog(prev => [...prev, { type: 'user', text: input }]);
    setInput('');
    setLoading(true);

    try {
      console.log(sessionId.current)
      const res = await fetch('https://c858-14-97-202-30.ngrok-free.app/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId.current,
          message: input,
        }),
      });
      const data = await res.json();
      setChatLog(prev => [...prev, { type: 'bot', text: data.result }]);
    } catch {
      setChatLog(prev => [...prev, { type: 'bot', text: 'Error contacting API' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-100 p-4">
      <div className="max-w-xl w-full mx-auto bg-white rounded shadow flex flex-col flex-1">
        <div className="px-4 py-2 border-b">
          <h2 className="text-lg font-semibold">Chatbot</h2>
        </div>
        <div className="flex-1 px-4 py-2 overflow-y-auto space-y-2">
          {chatLog.map((msg, i) => (
            <div key={i} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`rounded-lg p-2 max-w-[80%] ${
                msg.type === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-800'
              }`}>
                {msg.text}
              </div>
            </div>
          ))}
          {loading && <div className="text-gray-500 italic">…typing</div>}
        </div>
        <form onSubmit={sendMessage} className="flex p-4 space-x-2 border-t">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            className="flex-1 border rounded px-3 py-2 focus:outline-none focus:ring"
            placeholder="Type your message..."
          />
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;
