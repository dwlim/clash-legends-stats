export function setFiltersOpen(filtersPanel, filtersToggle, open) {
  if (filtersPanel) filtersPanel.hidden = !open;
  if (filtersToggle) filtersToggle.setAttribute('aria-expanded', String(open));
}

export function setFilterMode({ filterEquipmentTab, filterPlayerTab, filterEquipmentPane, filterPlayerPane }, mode) {
  if (filterEquipmentTab) filterEquipmentTab.classList.toggle('active', mode === 'equipment');
  if (filterPlayerTab) filterPlayerTab.classList.toggle('active', mode === 'player');
  if (filterEquipmentPane) filterEquipmentPane.classList.toggle('hidden', mode !== 'equipment');
  if (filterPlayerPane) filterPlayerPane.classList.toggle('hidden', mode !== 'player');
}
