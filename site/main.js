import { createSearchController } from './app.js';
import { createSiteState } from './site-state.js';
import { createRenderers } from './renderers.js';
import { loadDayData } from './day-loader.js';
import { setFilterMode, setFiltersOpen } from './ui-helpers.js';

const state = createSiteState();

const daySelect = document.getElementById('day-select');
const filtersToggle = document.getElementById('filters-toggle');
const filtersPanel = document.getElementById('filters-panel');
const filterEquipmentTab = document.getElementById('filter-equipment-tab');
const filterPlayerTab = document.getElementById('filter-player-tab');
const filterEquipmentPane = document.getElementById('filter-equipment-pane');
const filterPlayerPane = document.getElementById('filter-player-pane');
const playerSearchEl = document.getElementById('player-search');
const searchResultsEl = document.getElementById('search-results');
const equipmentFilterEl = document.getElementById('equipment-filter');
const equipmentClearEl = document.getElementById('equipment-clear');
const listEl = document.getElementById('group-list');
const titleEl = document.getElementById('title');
const subEl = document.getElementById('sub');
const bodyEl = document.getElementById('body');

const searchController = createSearchController({
  get groups() { return state.siteData?.groups || []; },
  input: playerSearchEl,
  resultsEl: searchResultsEl,
  listEl,
  onRenderGroup: (group, groupIndex, playerTag) => renderers.renderGroup(group, groupIndex, playerTag),
});

const renderers = createRenderers({
  state,
  elements: { equipmentFilterEl, listEl, titleEl, subEl, bodyEl, filtersPanel, filtersToggle, filterEquipmentTab, filterPlayerTab, filterEquipmentPane, filterPlayerPane, searchResultsEl },
  searchController,
  setFilterMode,
  setFiltersOpen,
});

async function loadDay(day) {
  await loadDayData(state, day);
  renderers.loadViewForDay();
}

async function init() {
  const manifestRes = await fetch('./data/manifest.json', { cache: 'no-store' });
  const manifest = await manifestRes.json();
  state.dayItems = (manifest.days || []).slice().sort((a, b) => a.date.localeCompare(b.date));
  daySelect.innerHTML = state.dayItems.map(item => `<option value="${item.date}">${item.date}</option>`).join('');
  const defaultDay = state.dayItems[state.dayItems.length - 1]?.date || '';
  daySelect.value = defaultDay;
  daySelect.addEventListener('change', () => {
    loadDay(daySelect.value).catch(err => {
      titleEl.textContent = 'Failed to load day';
      subEl.textContent = String(err);
      bodyEl.innerHTML = '<div class="error">Could not load the selected day.</div>';
    });
  });
  equipmentClearEl.addEventListener('click', () => {
    state.ownedEpicEquipment.clear();
    renderers.renderEquipmentFilter();
    renderers.renderList();
    if (state.siteData?.groups?.length) renderers.renderGroup(state.siteData.groups[0], 0);
  });
  filtersToggle.addEventListener('click', () => setFiltersOpen(filtersPanel, filtersToggle, filtersPanel.hidden));
  filterEquipmentTab.addEventListener('click', () => { state.filterMode = 'equipment'; setFilterMode({ filterEquipmentTab, filterPlayerTab, filterEquipmentPane, filterPlayerPane }, 'equipment'); });
  filterPlayerTab.addEventListener('click', () => { state.filterMode = 'player'; setFilterMode({ filterEquipmentTab, filterPlayerTab, filterEquipmentPane, filterPlayerPane }, 'player'); });
  playerSearchEl.addEventListener('input', () => {
    if (!playerSearchEl.value.trim()) state.selectedPlayer = null;
    renderers.renderSearchResults();
    renderers.renderList();
    if (playerSearchEl.value.trim()) {
      const query = playerSearchEl.value.trim().toLowerCase();
      const matchGroupIndex = state.siteData.groups.findIndex(group =>
        (group.players || []).some(player => player.name.toLowerCase().includes(query) || player.tag.toLowerCase().includes(query))
      );
      if (matchGroupIndex >= 0) renderers.renderGroup(state.siteData.groups[matchGroupIndex], matchGroupIndex);
    } else if (state.siteData?.groups?.length) {
      renderers.renderGroup(state.siteData.groups[0], 0);
    }
  });
  if (defaultDay) await loadDay(defaultDay);
}

init().catch(err => {
  titleEl.textContent = 'Failed to load site data';
  subEl.textContent = String(err);
  bodyEl.innerHTML = '<div class="error">Could not load the published JSON.</div>';
});
