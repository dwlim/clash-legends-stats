export function createRenderers({ state, elements, searchController, setFilterMode, setFiltersOpen }) {
  const { equipmentFilterEl, listEl, titleEl, subEl, bodyEl, filtersPanel, filtersToggle, filterEquipmentTab, filterPlayerTab, filterEquipmentPane, filterPlayerPane } = elements;

  function renderEquipmentFilter() {
    const items = ['Queen', 'King', 'Warden'];
    equipmentFilterEl.innerHTML = items.map(item => `<label><input type="checkbox" ${state.ownedEpicEquipment.has(item) ? 'checked' : ''} data-item="${item}"> ${item}</label>`).join('');
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
    titleEl.textContent = group.label;
    subEl.textContent = `${group.uniqueUsers} players · ${group.players.length} tracked entries`;
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
    }).join('') : '<div class="error">No groups match the selected equipment.</div>';
    listEl.querySelectorAll('.group-btn').forEach(btn => btn.addEventListener('click', () => renderGroup(state.siteData.groups[Number(btn.dataset.index)], Number(btn.dataset.index))));
  }

  function renderSearchResults() {
    searchController.renderSearchResults();
    searchResultsEl.querySelectorAll('.search-result').forEach(btn => btn.addEventListener('click', () => {
      const groupIndex = Number(btn.dataset.groupIndex);
      const playerTag = btn.dataset.playerTag;
      const group = state.siteData.groups[groupIndex];
      searchController.selectResult(groupIndex, playerTag);
      renderGroup(group, groupIndex, playerTag);
    }));
  }

  function loadViewForDay() {
    renderList();
    renderEquipmentFilter();
    setFilterMode({ filterEquipmentTab, filterPlayerTab, filterEquipmentPane, filterPlayerPane }, state.filterMode);
    setFiltersOpen(filtersPanel, filtersToggle, false);
    renderSearchResults();
    if (state.siteData.groups.length) renderGroup(state.siteData.groups[0], 0);
  }

  return { renderEquipmentFilter, renderGroup, renderList, renderSearchResults, loadViewForDay };
}
