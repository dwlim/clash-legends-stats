import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createSearchController } from '../site/app.js';

function makeDom() {
  return {
    input: { value: '' },
    resultsEl: { innerHTML: 'x', hidden: false },
    listEl: { dataset: {} },
  };
}

const groups = [
  { label: 'Group A', players: [{ name: 'Alice', tag: '#A1' }, { name: 'Bob', tag: '#B1' }] },
  { label: 'Group B', players: [{ name: 'Carol', tag: '#C1' }] },
];

test('player search filters the left list to the matched group', () => {
  const dom = makeDom();
  const controller = createSearchController({ groups, ...dom });
  dom.input.value = 'car';
  const visible = controller.renderList();
  assert.equal(visible.length, 1);
  assert.equal(visible[0].label, 'Group B');
});

test('clicking a search result fills the input and closes the dropdown', () => {
  const dom = makeDom();
  let selected = null;
  const controller = createSearchController({
    groups,
    ...dom,
    onRenderGroup: (group, index, tag) => { selected = { group: group.label, index, tag }; },
  });
  const player = controller.selectResult(1, '#C1');
  assert.equal(player.name, 'Carol');
  assert.equal(dom.input.value, 'Carol');
  assert.equal(dom.resultsEl.hidden, true);
  assert.equal(dom.resultsEl.innerHTML, '');
  assert.deepEqual(selected, { group: 'Group B', index: 1, tag: '#C1' });
});

test('clearing the search restores all groups', () => {
  const dom = makeDom();
  const controller = createSearchController({ groups, ...dom });
  dom.input.value = 'alice';
  assert.equal(controller.renderList().length, 1);
  const visible = controller.clearSearch();
  assert.equal(dom.input.value, '');
  assert.equal(visible.length, 2);
  assert.equal(dom.resultsEl.hidden, true);
});
