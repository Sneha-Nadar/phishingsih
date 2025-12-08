import { API } from "./api";

export async function checkImage(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API}/analyze/image`, {
    method: "POST",
    body: form,
  });

  return res.json();
}
