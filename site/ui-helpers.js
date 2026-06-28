export function setFiltersOpen(filtersPanel, filtersToggle, open) {
  filtersPanel.hidden = !open;
  filtersToggle.setAttribute('aria-expanded', String(open));
}

export function setFilterMode({ filterEquipmentTab, filterPlayerTab, filterEquipmentPane, filterPlayerPane }, mode) {
  filterEquipmentTab.classList.toggle('active', mode === 'equipment');
  filterPlayerTab.classList.toggle('active', mode === 'player');
  filterEquipmentPane.classList.toggle('hidden', mode !== 'equipment');
  filterPlayerPane.classList.toggle('hidden', mode !== 'player');
}
