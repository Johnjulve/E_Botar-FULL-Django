/* Users module JS (profile helpers, history interactions) */
(function () {
  'use strict';

  function onReady(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }

  onReady(function () {
    // Profile: toggle password section
    var toggleBtn = document.getElementById('togglePw');
    var section = document.getElementById('pwSection');
    if (toggleBtn && section) {
      toggleBtn.addEventListener('click', function () {
        var open = section.style.display !== 'none';
        section.style.display = open ? 'none' : 'block';
      });
    }
  });
})();


