import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

const persisted = typeof localStorage !== "undefined" ? localStorage.getItem("token") : null;
if (persisted) {
  (api.defaults.headers.common as any)["Authorization"] = `Bearer ${persisted}`;
}

export const setAuthToken = (token?: string) => {
  if (token) {
    (api.defaults.headers.common as any)["Authorization"] = `Bearer ${token}`;
  } else {
    delete (api.defaults.headers.common as any)["Authorization"];
  }
};

export default api;
