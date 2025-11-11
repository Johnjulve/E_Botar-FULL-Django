/* Admin extra: review applications helpers */
(function () {
  'use strict';
  function onReady(fn) { if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn); else fn(); }

  onReady(function () {
    // Auto-refresh every 30 seconds if there are pending application cards
    if (document.querySelector('.application-card')) {
      setInterval(function(){ location.reload(); }, 30000);
    }

    // Approve confirmation
    document.querySelectorAll('.btn-approve').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        if (!window.confirm('Are you sure you want to approve this application? This will create a candidate record.')) {
          e.preventDefault();
        }
      });
    });
  });
})();


