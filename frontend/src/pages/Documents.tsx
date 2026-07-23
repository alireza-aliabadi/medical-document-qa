import { useEffect, useState } from "react";
import { api, getToken } from "../lib/api";

type Doc = { id: string; filename: string; status: string };

export default function DocumentsPage() {
  const [docs, setDocs] = useState<Doc[]>([]);

  useEffect(() => {
    api.documents().then(setDocs).catch(() => setDocs([]));
  }, []);

  async function upload(file: File) {
    const form = new FormData();
    form.append("file", file);
    const response = await fetch("/api/v1/documents/upload", {
      method: "POST",
      headers: { Authorization: `Bearer ${getToken()}` },
      body: form,
    });
    if (response.ok) {
      const doc = await response.json();
      setDocs((prev) => [doc, ...prev]);
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Documents</h1>
      <label className="inline-block mb-6 cursor-pointer bg-teal-700 hover:bg-teal-600 px-4 py-2 rounded-lg">
        Upload PDF
        <input type="file" accept=".pdf" className="hidden" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
      </label>
      <ul className="space-y-2">
        {docs.map((d) => (
          <li key={d.id} className="rounded-lg border border-slate-800 bg-slate-900 px-4 py-3 flex justify-between">
            <span>{d.filename}</span>
            <span className="text-teal-400 text-sm">{d.status}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
