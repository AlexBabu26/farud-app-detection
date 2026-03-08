const Auth = (() => {
  const ACCESS_KEY = "fad_access";
  const REFRESH_KEY = "fad_refresh";

  function setTokens(access, refresh) {
    if (access) localStorage.setItem(ACCESS_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
  }

  function getAccessToken() {
    return localStorage.getItem(ACCESS_KEY);
  }

  function getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
  }

  function hasAccessToken() {
    return !!getAccessToken();
  }

  function logout() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }

  async function login(username, password) {
    const data = await Api.post("/api/auth/token/", { username, password }, { auth: false });
    setTokens(data.access, data.refresh);
    return data;
  }

  async function refresh() {
    const refreshToken = getRefreshToken();
    if (!refreshToken) throw new Error("No refresh token.");
    const data = await Api.post("/api/auth/token/refresh/", { refresh: refreshToken }, { auth: false });
    setTokens(data.access, null);
    return data.access;
  }

  return { setTokens, getAccessToken, getRefreshToken, hasAccessToken, logout, login, refresh };
})();

