export async function loadDayData(state, day) {
  const item = state.dayItems.find(entry => entry.date === day);
  if (!item) return null;
  const res = await fetch(`./${item.payload}`, { cache: 'no-store' });
  state.siteData = await res.json();
  return state.siteData;
}
