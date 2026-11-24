// Sachet portal: loads the Sachet Python package into the browser (Pyodide) and runs it locally.
(function () {
  const $ = (id) => document.getElementById(id);
  const runBtn = $('run');
  const loading = $('loading');
  const out = $('result');
  let py = null;
  let examples = null;

  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const list = (items, empty) => items && items.length
    ? '<ul>' + items.map((i) => '<li>' + esc(i) + '</li>').join('') + '</ul>'
    : '<p class="none">' + esc(empty) + '</p>';

  async function boot() {
    try {
      py = await loadPyodide();
      const files = await (await fetch('py/manifest.json')).json();
      py.FS.mkdirTree('/home/pyodide/sachet');
      for (const f of files) {
        const text = await (await fetch('py/sachet/' + f)).text();
        py.FS.writeFile('/home/pyodide/sachet/' + f, text);
      }
      py.runPython('import sys, json\nsys.path.insert(0, "/home/pyodide")\nimport sachet.portal as portal');
      runBtn.disabled = false;
      runBtn.textContent = 'Check the rewrite';
      loading.hidden = true;
      document.documentElement.dataset.ready = '1';
    } catch (e) {
      loading.textContent = 'Could not load the checker: ' + e.message + '. Please reload the page.';
      runBtn.textContent = 'Unavailable';
    }
  }

  function call(fn, args) {
    py.globals.set('_args', py.toPy(args));
    return JSON.parse(py.runPython('json.dumps(portal.' + fn + '(**_args), ensure_ascii=False)'));
  }

  function render(r, args) {
    if (!r.ok) { out.hidden = false; out.innerHTML = '<p class="hint bad">' + esc(r.error) + '</p>'; return; }
    const f = r.facts, m = r.meaning;
    const problems = [...m.flipped, ...f.invented, ...f.missing, ...m.missing].length;
    const channel = r.channel === 'sms' ? 'an SMS' : 'a radio / phone / full message';
    const verdict = r.passed
      ? '<div class="verdict ok">✅ No missing, invented or flipped facts found<small>Checked as ' + channel + '. A person should still review it before it is broadcast.</small></div>'
      : '<div class="verdict bad">❌ ' + problems + ' problem' + (problems === 1 ? '' : 's') + ' found<small>Checked as ' + channel + '. Fix the items below before using this rewrite.</small></div>';
    const read = r.detected_in_source;
    const statuses = Object.entries(read.statuses).map(([k, v]) => (v.length ? v.join('/') + ' ' : '') + k);
    const integrity = r.source_integrity.corrupted
      ? '<p class="hint bad">⚠️ The official text looks corrupted (' + r.source_integrity.broken_words.length + ' broken words, e.g. <span class="mono">' + esc(r.source_integrity.broken_words.slice(0, 3).join(' · ')) + '</span>). Text copied from some PDFs loses Nepali conjunct letters. Retype or fix it before relying on this check.</p>'
      : '';
    const toml = call('case_toml', { source: args.source, rewrite: args.rewrite, channel: args.channel, names: args.names, note: '' });
    const body = 'Contributed from the Sachet portal. Please add the link to the official alert.\n\n```toml\n' + toml + '```\n';
    const issueUrl = 'https://github.com/sanjaygdrrad/sachet-eval/issues/new?title=' + encodeURIComponent('Test case: ') + '&body=' + encodeURIComponent(body);
    const contribute = issueUrl.length < 7500
      ? '<a href="' + esc(issueUrl) + '" target="_blank" rel="noopener">Suggest this as a test case on GitHub ↗</a> (you review everything before submitting; please only share public alerts)'
      : 'This example is too long for a pre-filled GitHub issue. Copy the texts into a new issue on GitHub instead.';

    out.hidden = false;
    out.innerHTML = verdict + integrity +
      '<div class="groups">' +
      '<div class="group flip"><h3>⚠️ Meaning flipped</h3>' + list(m.flipped, 'None') + '</div>' +
      '<div class="group invented"><h3>Invented (not in the official alert)</h3>' + list(f.invented, 'None') + '</div>' +
      '<div class="group missing"><h3>Missing</h3>' + list([...f.missing, ...m.missing], 'None') + '</div>' +
      '<div class="group kept"><h3>Kept (' + (f.kept.length + m.kept.length) + ')</h3>' + list([...f.kept, ...m.kept], 'Nothing to check yet') + '</div>' +
      '</div>' +
      '<p class="read"><strong>What Sachet read in the official alert:</strong> numbers <code>' + esc(read.numbers.join(', ') || 'none') + '</code> · hazard: ' + esc(read.hazards.join(', ') || 'not stated') +
      ' · status: ' + esc(statuses.join(', ') || 'not stated') + ' · trend: ' + esc(read.trends.join(', ') || 'not stated') +
      ' · action: ' + esc(read.actions.join(', ') || 'not stated') + ' · places checked: ' + r.names_checked + '</p>' +
      '<p class="contribute">' + contribute + '</p>';
    out.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  $('form').addEventListener('submit', (e) => {
    e.preventDefault();
    if (!py) return;
    const args = {
      source: $('source').value, rewrite: $('rewrite').value,
      channel: document.querySelector('input[name=channel]:checked').value,
      names: $('names').value, may_drop: $('may_drop').value, may_add: $('may_add').value, sms_numbers: $('sms_numbers').value,
    };
    render(call('check', args), args);
  });

  document.querySelectorAll('[data-example]').forEach((b) => b.addEventListener('click', async () => {
    examples = examples || await (await fetch('examples.json')).json();
    const ex = examples[b.dataset.example];
    $('source').value = examples.source;
    $('rewrite').value = ex.rewrite;
    $('names').value = examples.names;
    document.querySelector('input[name=channel][value=' + ex.channel + ']').checked = true;
    if (py) $('form').requestSubmit();
  }));

  boot();
})();
