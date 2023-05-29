export async function throwOnFetchError(response: Response) {
  if (response.ok) {
    return;
  }

  const json = await response.json();
  if (json?.error) {
    throw new Error(json.error);
  }
  throw new Error(`HTTP error status: ${response.status}`);
}
