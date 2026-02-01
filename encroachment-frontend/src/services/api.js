const API_BASE = "http://127.0.0.1:5000";

export const processAll = async () => {
  const res = await fetch(`${API_BASE}/process-all`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error("Processing failed");
  }

  return res.json();
};
