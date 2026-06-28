export async function loadManifest() {
  const manifestRes = await fetch('./data/manifest.json', { cache: 'no-store' });
  return manifestRes.json();
}

export async function loadDayPayload(item) {
  const res = await fetch(`./${item.payload}`, { cache: 'no-store' });
  return res.json();
}

export function sortDayItems(days = []) {
  return (days || []).slice().sort((a, b) => a.date.localeCompare(b.date));
}
