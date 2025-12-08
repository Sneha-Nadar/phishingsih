import { API } from "./api";

export async function checkURL(url) {
  const res = await fetch(`${API}/analyze/url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  return res.json();
}
