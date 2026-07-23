import { useEffect, useState } from "react";
import { api } from "../lib/api";

export default function PlatformPage() {
  const [dashboard, setDashboard] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    api.dashboard().then(setDashboard).catch(() => setDashboard(null));
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">AI Platform</h1>
      <p className="text-slate-400 mb-6">Model registry, datasets, and evaluation metrics</p>
      <pre className="rounded-xl border border-slate-800 bg-slate-900 p-4 text-sm overflow-auto">
        {JSON.stringify(dashboard, null, 2)}
      </pre>
    </div>
  );
}
