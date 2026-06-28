export function createSiteState() {
  const state = {
    siteData: null,
    dayItems: [],
    ownedEpicEquipment: new Set(),
    equipmentItems: [],
    filterMode: 'equipment',
    selectedPlayer: null,
  };

  return state;
}
