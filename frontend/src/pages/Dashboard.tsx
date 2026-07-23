import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function DashboardPage() {
  const [user, setUser] = useState<{ email: string; role: string } | null>(null);

  useEffect(() => {
    api.me().then(setUser).catch(() => setUser(null));
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
      <p className="text-slate-400 mb-8">Medical Knowledge Assistant overview</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="Role" value={user?.role ?? "—"} />
        <Card title="Pipeline" value="OCR → Chunk → Embed → RAG" />
        <Card title="Status" value="Development" />
      </div>
    </div>
  );
}

function Card({ title, value }: { title: string; value: string }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{title}</p>
      <p className="text-lg font-semibold mt-1">{value}</p>
    </div>
  );
}
