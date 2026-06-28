export function createRenderers({ state, elements, searchController, setFilterMode, setFiltersOpen }) {
  const { equipmentFilterEl, listEl, titleEl, subEl, bodyEl, filtersPanel, filtersToggle, filterEquipmentTab, filterPlayerTab, filterEquipmentPane, filterPlayerPane } = elements;

  function setText(el, value) {
    if (el) el.textContent = value;
  }

  function renderEquipmentFilter() {
    const items = state.equipmentItems || [];
    if (!equipmentFilterEl) return;
    equipmentFilterEl.innerHTML = items.length
      ? items.map(item => `<label><input type="checkbox" ${state.ownedEpicEquipment.has(item) ? 'checked' : ''} data-item="${item}"> ${item}</label>`).join('')
      : '<div class="muted">No equipment found for this day.</div>';
    equipmentFilterEl.querySelectorAll('input[type="checkbox"]').forEach(input => {
      input.addEventListener('change', () => {
        if (input.checked) state.ownedEpicEquipment.add(input.dataset.item); else state.ownedEpicEquipment.delete(input.dataset.item);
        renderList();
      });
    });
  }

  function renderGroup(group, groupIndex, playerTag = null) {
    state.selectedPlayer = { tag: playerTag };
    if (!group) return;
    setText(titleEl, group.label);
    setText(subEl, `${group.uniqueUsers} players · ${group.players.length} tracked entries`);
    const rows = (group.players || [])
      .filter(player => !state.selectedPlayer || player.tag === state.selectedPlayer.tag)
      .map(player => `<tr><td>${player.name}</td></tr>`).join('');
    bodyEl.innerHTML = `<table><tbody>${rows}</tbody></table>`;
  }

  function renderList() {
    const visibleGroups = searchController.renderList();
    listEl.innerHTML = visibleGroups.length ? visibleGroups.map((group, visibleIndex) => {
      const originalIndex = state.siteData.groups.indexOf(group);
      return `<button class="group-btn ${visibleIndex === 0 ? 'active' : ''}" data-index="${originalIndex}">${group.label}</button>`;
    }).join('') : (state.siteData.groups.length ? '<div class="error">No groups match the selected equipment.</div>' : '<div class="muted">No groups available.</div>');
    listEl.querySelectorAll('.group-btn').forEach(btn => btn.addEventListener('click', () => renderGroup(state.siteData.groups[Number(btn.dataset.index)], Number(btn.dataset.index))));
  }

  function renderSearchResults() {
    searchController.renderSearchResults();
    searchResultsEl?.querySelectorAll('.search-result').forEach(btn => btn.addEventListener('click', () => {
      const groupIndex = Number(btn.dataset.groupIndex);
      const playerTag = btn.dataset.playerTag;
      const group = state.siteData.groups[groupIndex];
      searchController.selectResult(groupIndex, playerTag);
      renderGroup(group, groupIndex, playerTag);
    }));
  }

  function loadViewForDay() {
    renderEquipmentFilter();
    renderList();
    setFilterMode({ filterEquipmentTab, filterPlayerTab, filterEquipmentPane, filterPlayerPane }, state.filterMode);
    setFiltersOpen(filtersPanel, filtersToggle, false);
    renderSearchResults();
    if (state.siteData.groups.length) renderGroup(state.siteData.groups[0], 0);
  }

  return { renderEquipmentFilter, renderGroup, renderList, renderSearchResults, loadViewForDay };
}
