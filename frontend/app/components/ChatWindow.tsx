"use client";

import { useState } from "react";
import { sendChatMessage, ChatResponse } from "../../lib/api";

interface Turn {
  role: "user" | "assistant";
  content: string;
  trace?: ChatResponse["agent_trace"];
  sources?: string[];
}

export default function ChatWindow() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    if (!input.trim() || loading) return;
    const userMessage = input.trim();
    setTurns((prev) => [...prev, { role: "user", content: userMessage }]);
    setInput("");
    setLoading(true);
    try {
      const res = await sendChatMessage(userMessage, conversationId);
      setConversationId(res.conversation_id);
      setTurns((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, trace: res.agent_trace, sources: res.sources },
      ]);
    } catch (err) {
      setTurns((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong reaching the backend." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto">
      <div className="flex-1 overflow-y-auto space-y-4 p-4">
        {turns.map((t, i) => (
          <div key={i} className={t.role === "user" ? "text-right" : "text-left"}>
            <div
              className={`inline-block px-4 py-2 rounded-lg max-w-xl ${
                t.role === "user" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-900"
              }`}
            >
              {t.content}
            </div>
            {t.trace && (
              <div className="mt-1 text-xs text-gray-500">
                {t.trace.map((step, j) => (
                  <span key={j} className="mr-2">
                    ⚙ {step.agent}: {step.summary}
                  </span>
                ))}
              </div>
            )}
            {t.sources && t.sources.length > 0 && (
              <div className="mt-1 text-xs text-gray-400">Sources: {t.sources.join(", ")}</div>
            )}
          </div>
        ))}
        {loading && <div className="text-sm text-gray-400">Agents are working…</div>}
      </div>
      <div className="border-t p-4 flex gap-2">
        <input
          className="flex-1 border rounded-lg px-3 py-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about operations, trends, or forecasts…"
        />
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded-lg disabled:opacity-50"
          onClick={handleSend}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}
