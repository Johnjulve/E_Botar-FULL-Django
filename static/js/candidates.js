/* Candidates module JS (application form interactions) */
(function () {
  'use strict';

  function onReady(fn) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else { fn(); }
  }

  onReady(function () {
    var form = document.querySelector('form');
    if (!form) return;

    var photoInput = form.querySelector('input[type="file"][name]');
    var preview = document.getElementById('photo-preview');
    var uploadArea = document.querySelector('.file-upload-area');
    var useProfile = form.querySelector('input[type="checkbox"][name="use_profile_picture"]');
    var partySelect = form.querySelector('select[name="party"]');
    var partyName = form.querySelector('[name="party_name"]');

    /* File upload preview */
    if (photoInput && preview) {
      photoInput.addEventListener('change', function (e) {
        var file = e.target.files && e.target.files[0];
        if (!file) { preview.innerHTML = ''; return; }
        var reader = new FileReader();
        reader.onload = function (ev) {
          preview.innerHTML = '<img src="' + ev.target.result + '" class="preview-image" alt="Photo preview">';
        };
        reader.readAsDataURL(file);
      });
    }

    /* Drag & drop */
    if (uploadArea && photoInput) {
      uploadArea.addEventListener('dragover', function (e) { e.preventDefault(); uploadArea.classList.add('dragover'); });
      uploadArea.addEventListener('dragleave', function (e) { e.preventDefault(); uploadArea.classList.remove('dragover'); });
      uploadArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        var files = e.dataTransfer && e.dataTransfer.files;
        if (files && files.length > 0) {
          photoInput.files = files;
          photoInput.dispatchEvent(new Event('change'));
        }
      });
      uploadArea.addEventListener('click', function () { photoInput && photoInput.click(); });
    }

    /* Use profile picture toggle */
    if (useProfile && uploadArea && photoInput) {
      useProfile.addEventListener('change', function (e) {
        var checked = !!e.target.checked;
        uploadArea.style.opacity = checked ? '0.5' : '1';
        uploadArea.style.pointerEvents = checked ? 'none' : 'auto';
        photoInput.required = !checked;
      });
    }

    /* Party selection toggle */
    if (partySelect && partyName) {
      partySelect.addEventListener('change', function (e) {
        if (e.target.value) {
          partyName.disabled = true; partyName.value = ''; partyName.placeholder = 'Custom party name disabled (using selected party)';
        } else {
          partyName.disabled = false; partyName.placeholder = 'Custom Party Name (if not selecting from list)';
        }
      });
    }

    /* Form validation */
    form.addEventListener('submit', function (e) {
      var isValid = true;
      var requiredSelectors = ['select[name="position"]', 'select[name="election"]', 'textarea[name="manifesto"]'];
      requiredSelectors.forEach(function (sel) {
        var field = form.querySelector(sel);
        if (field && !String(field.value || '').trim()) {
          isValid = false; field.classList.add('is-invalid');
        } else if (field) { field.classList.remove('is-invalid'); }
      });

      if (useProfile && photoInput && !useProfile.checked && (!photoInput.files || photoInput.files.length === 0)) {
        isValid = false;
        alert('Please upload a photo or select to use your profile picture.');
      }

      if (!isValid) { e.preventDefault(); }
    });
  });
})();


