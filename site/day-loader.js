export async function loadDayData(state, day) {
  const item = state.dayItems.find(entry => entry.date === day);
  if (!item) return null;
  const res = await fetch(`./${item.payload}`, { cache: 'no-store' });
  state.siteData = await res.json();
  state.equipmentItems = Array.from(new Set((state.siteData.groups || []).flatMap(group => (group.example?.sections?.heroes || []).flatMap(hero => (hero.equipment || []).map(eq => eq.name))))).sort();
  state.ownedEpicEquipment = new Set();
  return state.siteData;
}
