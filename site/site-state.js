export function createSiteState() {
  const state = {
    siteData: null,
    dayItems: [],
    ownedEpicEquipment: new Set(),
    filterMode: 'equipment',
    selectedPlayer: null,
  };

  return state;
}
