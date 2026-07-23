import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, setToken } from "../lib/api";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@medical.local");
  const [password, setPassword] = useState("changeme");
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      const { access_token } = await api.login(email, password);
      setToken(access_token);
      navigate("/");
    } catch {
      setError("Login failed");
    }
  }

  return (
    <div className="max-w-md mx-auto mt-20">
      <h1 className="text-2xl font-bold mb-6">Sign in</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <input
          className="w-full rounded-lg bg-slate-900 border border-slate-700 px-4 py-2"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
        />
        <input
          type="password"
          className="w-full rounded-lg bg-slate-900 border border-slate-700 px-4 py-2"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
        />
        {error && <p className="text-red-400 text-sm">{error}</p>}
        <button className="w-full bg-teal-600 hover:bg-teal-500 rounded-lg py-2 font-medium">
          Login
        </button>
      </form>
    </div>
  );
}
