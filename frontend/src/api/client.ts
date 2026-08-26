import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const apiClient = axios.create({ baseURL: API_BASE_URL });

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("hims_access_token");
  if (token && config.headers) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

let isRefreshing = false;
let queue: Array<() => void> = [];

apiClient.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("hims_refresh_token");
      if (!refreshToken) { forceLogout(); return Promise.reject(error); }

      if (isRefreshing) {
        return new Promise((resolve) => queue.push(() => resolve(apiClient(originalRequest))));
      }
      isRefreshing = true;
      try {
        const { data } = await axios.post(`${API_BASE_URL}/auth/refresh/`, { refresh: refreshToken });
        localStorage.setItem("hims_access_token", data.access);
        queue.forEach((cb) => cb());
        queue = [];
        return apiClient(originalRequest);
      } catch (e) {
        forceLogout();
        return Promise.reject(e);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

function forceLogout() {
  localStorage.removeItem("hims_access_token");
  localStorage.removeItem("hims_refresh_token");
  localStorage.removeItem("hims_user");
  window.location.href = "/login";
}
