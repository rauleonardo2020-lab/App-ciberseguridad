import React, { useState } from "react";
import { useAuth } from "../state/AuthContext";
import { Link as RouterLink } from "react-router-dom";

export default function SignupPage() {
  const { signup } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await signup(email, password);
      window.alert("Cuenta creada, ahora puedes iniciar sesión");
    } catch (err: any) {
      window.alert(err?.response?.data?.detail || "Error al registrar");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto mt-24 px-4">
      <h1 className="text-2xl font-semibold mb-6">Registro</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <input className="w-full border rounded px-3 py-2" placeholder="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input className="w-full border rounded px-3 py-2" placeholder="Contraseña" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button disabled={loading} className="w-full bg-blue-600 text-white rounded px-4 py-2 disabled:opacity-50" type="submit">
          {loading ? "Creando..." : "Crear cuenta"}
        </button>
        <p className="text-sm">
          ¿Ya tienes cuenta? <RouterLink to="/login" className="text-blue-600">Inicia sesión</RouterLink>
        </p>
      </form>
    </div>
  );
}
