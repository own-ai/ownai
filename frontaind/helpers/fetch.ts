export async function throwOnFetchError(response: Response) {
  if (response.ok) {
    return;
  }

  let json;
  try {
    json = await response.json();
  } catch {}
  if (json?.error) {
    throw new Error(json.error);
  }
  throw new Error(
    `HTTP error status: ${response.status}\nWe're sorry for that. Please see the server log for more information and contact us if you need help.`,
  );
}
