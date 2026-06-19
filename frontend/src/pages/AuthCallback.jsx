import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { tokens } from "../api.js";

export default function AuthCallback() {
  const navigate = useNavigate();
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");
    if (accessToken) {
      tokens.set({ access_token: accessToken, refresh_token: refreshToken });
      navigate("/dashboard", { replace: true });
    } else {
      navigate("/login", { replace: true });
    }
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center text-gray-500">
      Завершаем вход...
    </div>
  );
}
