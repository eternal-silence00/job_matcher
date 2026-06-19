import axios from "axios";

const API_URL = "http://localhost:8000";

export const tokens = {
  get access() {
    return localStorage.getItem("access_token");
  },
  get refresh() {
    return localStorage.getItem("refresh_token");
  },
  set({ access_token, refresh_token }) {
    if (access_token) localStorage.setItem("access_token", access_token);
    if (refresh_token) localStorage.setItem("refresh_token", refresh_token);
  },
  clear() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};

const api = axios.create({ baseURL: API_URL });

// добавляем access-токен в каждый запрос
api.interceptors.request.use((config) => {
  const token = tokens.access;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// --- авто-refresh на 401 ---
// Если access протух, ловим 401, обновляем токен через /auth/refresh и
// повторяем исходный запрос. Параллельные 401 не плодят несколько refresh:
// первый запускает обновление, остальные ждут его результата.

let isRefreshing = false;
let waiters = [];

function onRefreshed(newAccess) {
  waiters.forEach((cb) => cb(newAccess));
  waiters = [];
}

function forceLogout() {
  tokens.clear();
  if (window.location.pathname !== "/login") {
    window.location.href = "/login";
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const status = error.response?.status;

    // не трогаем не-401 и уже повторённые запросы
    if (status !== 401 || original._retry) {
      return Promise.reject(error);
    }
    // сам refresh вернул 401 — refresh-токен мёртв, выходим
    if (original.url?.includes("/auth/refresh")) {
      forceLogout();
      return Promise.reject(error);
    }
    const refreshToken = tokens.refresh;
    if (!refreshToken) {
      forceLogout();
      return Promise.reject(error);
    }

    original._retry = true;

    // если refresh уже идёт — встаём в очередь и ждём новый токен
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        waiters.push((newAccess) => {
          if (!newAccess) return reject(error);
          original.headers.Authorization = `Bearer ${newAccess}`;
          resolve(api(original));
        });
      });
    }

    isRefreshing = true;
    try {
      const { data } = await axios.post(`${API_URL}/auth/refresh`, {
        refresh_token: refreshToken,
      });
      tokens.set(data);
      onRefreshed(data.access_token);
      original.headers.Authorization = `Bearer ${data.access_token}`;
      return api(original);
    } catch (refreshError) {
      onRefreshed(null);
      forceLogout();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
