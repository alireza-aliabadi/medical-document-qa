import { FormEvent, useState } from "react";
import { api } from "../lib/api";

export default function ChatPage() {
  const [message, setMessage] = useState("");
  const [answer, setAnswer] = useState("");
  const [citations, setCitations] = useState<Array<{ excerpt: string; page_number: number | null }>>([]);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await api.chat(message);
      setAnswer(result.answer);
      setCitations(result.citations ?? []);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Medical Chat</h1>
      <form onSubmit={onSubmit} className="flex gap-2 mb-6">
        <input
          className="flex-1 rounded-lg bg-slate-900 border border-slate-700 px-4 py-2"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask a medical question..."
        />
        <button disabled={loading} className="bg-teal-600 hover:bg-teal-500 px-4 py-2 rounded-lg">
          {loading ? "..." : "Ask"}
        </button>
      </form>
      {answer && (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4 mb-4">
          <p>{answer}</p>
        </div>
      )}
      {citations.length > 0 && (
        <div>
          <h2 className="font-semibold mb-2">Citations</h2>
          <ul className="space-y-2 text-sm text-slate-300">
            {citations.map((c, i) => (
              <li key={i} className="border-l-2 border-teal-600 pl-3">
                p.{c.page_number ?? "?"} — {c.excerpt}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
