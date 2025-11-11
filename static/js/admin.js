/* Admin UI JavaScript - consolidated */
(function () {
  'use strict';

  function qs(selector, root) {
    return (root || document).querySelector(selector);
  }

  function getCsrfToken() {
    var el = qs('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }

  function getResetTemplateUrl() {
    // Look for a container that provides the URL template with "/0/" placeholder
    var host = qs('[data-reset-url-template]');
    return host ? host.getAttribute('data-reset-url-template') : null;
  }

  function openPasswordModal(username, password) {
    var overlay = qs('#pwModal');
    if (!overlay) return;
    var u = qs('.js-username', overlay);
    var p = qs('.js-password', overlay);
    if (u) u.textContent = username || '';
    if (p) p.textContent = password || '';
    overlay.style.display = 'flex';
  }

  function closePasswordModal() {
    var overlay = qs('#pwModal');
    if (overlay) overlay.style.display = 'none';
  }

  function copyPassword() {
    var pwEl = qs('#pwModal .js-password');
    if (!pwEl) return;
    var pw = pwEl.textContent || '';
    navigator.clipboard.writeText(pw).then(function () {
      var btn = qs('#copyPwBtn');
      if (!btn) return;
      var old = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(function () { btn.textContent = old; }, 1500);
    });
  }

  function buildResetUrl(userId) {
    var tpl = getResetTemplateUrl();
    if (tpl && tpl.indexOf('/0/') !== -1) {
      return tpl.replace('/0/', '/' + String(userId) + '/');
    }
    // Fallback: try to append userId at the end
    return (tpl || '') + String(userId) + '/';
  }

  function resetPassword(userId, username) {
    if (!window.confirm('Reset password for ' + username + '?')) return;
    var url = buildResetUrl(userId);
    if (!url) {
      alert('Reset URL not found.');
      return;
    }
    fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': getCsrfToken() }
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data && data.success) {
          openPasswordModal(data.username, data.new_password);
        } else {
          alert('Error: ' + ((data && data.error) || 'Unknown error'));
        }
      })
      .catch(function (err) { alert('Request failed: ' + err); });
  }

  // Expose needed functions for inline handlers already present in templates
  window.resetPassword = resetPassword;
  window.openPasswordModal = openPasswordModal;
  window.closePasswordModal = closePasswordModal;
  window.copyPassword = copyPassword;
})();


