import React, { useState } from "react";
import { useAuth } from "../state/AuthContext";
import { Link as RouterLink, useLocation } from "react-router-dom";

export default function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const location = useLocation() as any;

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
    } catch (err: any) {
      window.alert(err?.response?.data?.detail || "Error al iniciar sesión");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-24 px-4">
      <h1 className="text-2xl font-semibold mb-6">Iniciar sesión</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <input className="w-full border rounded px-3 py-2" placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="w-full border rounded px-3 py-2" placeholder="Contraseña" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button disabled={loading} className="w-full bg-blue-600 text-white rounded px-4 py-2 disabled:opacity-50" type="submit">
          {loading ? "Entrando..." : "Entrar"}
        </button>
        <p className="text-sm">
          ¿No tienes cuenta? <RouterLink to="/signup" className="text-blue-600">Regístrate</RouterLink>
        </p>
        {location.state?.from && <p className="text-xs text-gray-500">Por favor inicia sesión para continuar</p>}
      </form>
    </div>
  );
}
