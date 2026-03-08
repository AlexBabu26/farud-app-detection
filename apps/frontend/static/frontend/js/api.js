const Api = (() => {
  async function request(method, url, body, opts = {}) {
    const authEnabled = opts.auth !== false;
    const headers = { "Content-Type": "application/json" };

    if (authEnabled) {
      const token = Auth.getAccessToken();
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });

    if (res.status === 204) return null;

    // If unauthorized, attempt refresh once
    if (res.status === 401 && authEnabled) {
      try {
        await Auth.refresh();
        return request(method, url, body, opts); // retry once after refresh
      } catch (e) {
        Auth.logout();
        window.location.href = "/login/";
        return;
      }
    }

    const text = await res.text();
    let data;
    try { data = text ? JSON.parse(text) : {}; } catch { data = { detail: text }; }

    if (!res.ok) {
      // Extract the friendliest error message available
      const msg = data?.detail
        || data?.error_message
        || data?.error?.message
        || (typeof data === "string" ? data : null)
        || `Request failed (HTTP ${res.status})`;
      throw new Error(msg);
    }
    return data;
  }

  function get(url, opts) { return request("GET", url, null, opts); }
  function post(url, body, opts) { return request("POST", url, body, opts); }
  function patch(url, body, opts) { return request("PATCH", url, body, opts); }
  function del(url, opts) { return request("DELETE", url, null, opts); }

  // Helper to extract array from paginated response
  function extractArray(data) {
    if (Array.isArray(data)) return data;
    if (data && Array.isArray(data.results)) return data.results;
    return [];
  }

  return { get, post, patch, del, extractArray };
})();

