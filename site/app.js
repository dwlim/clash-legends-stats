export function createSearchController({ groups, input, resultsEl, listEl, onRenderGroup }) {
  const getGroups = typeof groups === 'function' ? groups : () => groups;
  let selectedPlayer = null;

  function renderList() {
    const query = (input.value || '').trim().toLowerCase();
    const sourceGroups = getGroups();
    const searchGroupIndexes = query
      ? new Set(
          sourceGroups.flatMap((group, groupIndex) =>
            (group.players || []).some(player => player.name.toLowerCase().includes(query) || player.tag.toLowerCase().includes(query))
              ? [groupIndex]
              : []
          )
        )
      : null;

    const visibleGroups = sourceGroups.filter((group, groupIndex) => {
      if (searchGroupIndexes && !searchGroupIndexes.has(groupIndex)) return false;
      return true;
    });

    listEl.dataset.visibleGroups = JSON.stringify(visibleGroups.map(group => group.label));
    return visibleGroups;
  }

  function renderSearchResults() {
    const query = (input.value || '').trim().toLowerCase();
    const sourceGroups = getGroups();
    if (!query || !sourceGroups.length) {
      resultsEl.innerHTML = '';
      resultsEl.hidden = true;
      return [];
    }

    const matches = [];
    sourceGroups.forEach((group, groupIndex) => {
      (group.players || []).forEach(player => {
        if (player.name.toLowerCase().includes(query) || player.tag.toLowerCase().includes(query)) {
          matches.push({ groupIndex, player });
        }
      });
    });

    resultsEl.hidden = false;
    resultsEl.innerHTML = matches.slice(0, 8).map(match => `
      <button class="search-result" type="button" data-group-index="${match.groupIndex}" data-player-tag="${match.player.tag}">
        ${match.player.name}
      </button>
    `).join('') || '<div class="empty">No players found.</div>';
    return matches;
  }

  function selectResult(groupIndex, playerTag) {
    const sourceGroups = getGroups();
    const group = sourceGroups[groupIndex];
    const player = (group.players || []).find(p => p.tag === playerTag) || null;
    if (player) input.value = player.name;
    selectedPlayer = player;
    resultsEl.innerHTML = '';
    resultsEl.hidden = true;
    renderList();
    if (typeof onRenderGroup === 'function') onRenderGroup(group, groupIndex, playerTag);
    return player;
  }

  function clearSearch() {
    input.value = '';
    selectedPlayer = null;
    resultsEl.innerHTML = '';
    resultsEl.hidden = true;
    return renderList();
  }

  return {
    renderList,
    renderSearchResults,
    selectResult,
    clearSearch,
    get selectedPlayer() {
      return selectedPlayer;
    },
  };
}
