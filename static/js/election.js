/* Election module JS (cards animation, voting helpers) */
(function () {
  'use strict';

  function onReady(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn);
    else fn();
  }

  onReady(function () {
    // Intersection animation for election/result cards
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.election-card, .position-results-card, .winner-card').forEach(function (card) {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
      observer.observe(card);
    });

    // Candidate selection highlight (detail page)
    document.querySelectorAll('.radio-input').forEach(function (input) {
      input.addEventListener('change', function () {
        var posId = this.name.replace('position_', '');
        document.querySelectorAll('[data-position-id="' + posId + '"]').forEach(function (el) {
          el.classList.remove('selected');
        });
        if (this.checked) {
          var card = this.closest('.candidate-card');
          if (card) card.classList.add('selected');
        }
      });
    });
  });
})();


