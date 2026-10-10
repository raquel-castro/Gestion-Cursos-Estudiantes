const API_BASE_URL = "http://localhost:8000";

async function request(method, url, options = {}) {
    const { params, data } = options;
    const query = params
        ? new URLSearchParams(
            Object.entries(params)
                .filter(([, value]) => value !== undefined && value !== null && value !== "")
                .map(([key, value]) => [key, String(value)])
        ).toString()
        : "";

    const response = await fetch(
        `${API_BASE_URL}${url}${query ? `?${query}` : ""}`,
        {
            method,
            headers: data !== undefined
                ? { "Content-Type": "application/json" }
                : undefined,
            body: data !== undefined ? JSON.stringify(data) : undefined
        }
    );

    const contentType = response.headers.get("content-type") || "";
    const responseData = contentType.includes("application/json")
        ? await response.json()
        : await response.text();

    if (!response.ok) {
        const error = new Error(responseData?.detail || "Error en la solicitud.");
        error.response = {
            status: response.status,
            data: responseData
        };
        throw error;
    }

    return {
        status: response.status,
        data: responseData
    };
}

const api = {
    get: (url, options) => request("GET", url, options),
    post: (url, data) => request("POST", url, { data }),
    put: (url, data) => request("PUT", url, { data }),
    delete: (url, options) => request("DELETE", url, options)
};

export default api;
