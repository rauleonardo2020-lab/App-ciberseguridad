import { useEffect, useMemo, useState } from "react";
import { useAuth } from "../state/AuthContext";
import api from "../lib/api";
import { ScanResult, ScanEntry } from "../types";

export default function DashboardPage() {
  const { logout } = useAuth();
  const [ip, setIp] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<ScanResult[]>([]);

  const fetchResults = async () => {
    const { data } = await api.get<ScanResult[]>("/scan/results");
    setResults(data);
  };

  useEffect(() => {
    fetchResults().catch(() => {
      window.alert("Error al cargar resultados");
    });
  }, []);

  const onScan = async () => {
    const ipTrim = ip.trim();
    if (!ipTrim) {
      window.alert("Ingresa una IP válida");
      return;
    }
    setLoading(true);
    try {
      await api.post("/scan/network", { ip: ipTrim });
      await fetchResults();
      window.alert("Escaneo iniciado");
    } catch (err: any) {
      const msg = err?.response?.data?.detail || "Error al escanear";
      window.alert(msg);
    } finally {
      setLoading(false);
    }
  };

  const flattened = useMemo(() => {
    const rows: { scanId: number; host: string; entry: ScanEntry }[] = [];
    for (const scan of results) {
      for (const host of Object.keys((scan as any).scan_payload || {})) {
        for (const entry of (scan as any).scan_payload[host] || []) {
          rows.push({ scanId: scan.id, host, entry });
        }
      }
    }
    return rows;
  }, [results]);

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-semibold">Escudo IA - Dashboard</h1>
        <button onClick={logout} className="border rounded px-3 py-2">Salir</button>
      </div>

      <div className="space-y-4">
        <div className="flex gap-2">
          <input className="flex-1 border rounded px-3 py-2" placeholder="Dirección IP (e.g., 127.0.0.1)" value={ip} onChange={(e) => setIp(e.target.value)} />
          <button className="bg-blue-600 text-white rounded px-4 py-2 disabled:opacity-50" onClick={onScan} disabled={loading}>
            {loading ? "Escaneando..." : "Escanear"}
          </button>
        </div>

        <hr />

        <h2 className="text-xl font-medium">Resultados</h2>
        {results.length === 0 ? (
          <p className="text-gray-500">No hay resultados aún.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm border">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-3 py-2 border">Scan ID</th>
                  <th className="px-3 py-2 border">Host</th>
                  <th className="px-3 py-2 border">Protocolo</th>
                  <th className="px-3 py-2 border">Puerto</th>
                  <th className="px-3 py-2 border">Estado</th>
                  <th className="px-3 py-2 border">Servicio</th>
                  <th className="px-3 py-2 border">Producto</th>
                  <th className="px-3 py-2 border">Versión</th>
                </tr>
              </thead>
              <tbody>
                {flattened.map((row, idx) => (
                  <tr key={`${row.scanId}-${idx}`} className="odd:bg-white even:bg-gray-50">
                    <td className="px-3 py-2 border">{row.scanId}</td>
                    <td className="px-3 py-2 border">{row.host}</td>
                    <td className="px-3 py-2 border">{row.entry.protocol}</td>
                    <td className="px-3 py-2 border">{row.entry.port}</td>
                    <td className="px-3 py-2 border">{row.entry.state || "-"}</td>
                    <td className="px-3 py-2 border">{row.entry.service || "-"}</td>
                    <td className="px-3 py-2 border">{row.entry.product || "-"}</td>
                    <td className="px-3 py-2 border">{row.entry.version || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
