/**
 * Admin Module JavaScript
 * Consolidated scripts for E-Botar Admin Module
 */

// ==================== UTILITY FUNCTIONS ====================

/**
 * Get CSRF token from cookies
 */
function getCsrfToken() {
    const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfEl) return csrfEl.value;
    
    // Fallback: get from cookie
    const value = `; ${document.cookie}`;
    const parts = value.split(`; csrftoken=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

/**
 * Get cookie value by name
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
}

// ==================== MODAL HANDLERS ====================

/**
 * Initialize all modal handlers
 */
function initializeModals() {
    // Position modals
    initializePositionModals();
    
    // Election modals
    initializeElectionModals();
    
    // Course modals
    initializeCourseModals();
    
    // Department modals
    initializeDepartmentModals();
    
    // Candidate modals
    initializeCandidateModals();
}

// ==================== POSITION MODALS ====================

function initializePositionModals() {
    const deleteModal = document.getElementById('deletePositionModal');
    const editModal = document.getElementById('editPositionModal');
    const assocModal = document.getElementById('associatePositionModal');
    
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            document.getElementById('deletePositionId').value = btn.getAttribute('data-pid');
            document.getElementById('deletePositionName').innerText = btn.getAttribute('data-pname');
        });
    }
    
    if (editModal) {
        editModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            document.getElementById('editPositionForm').action = btn.getAttribute('data-edit-url');
            document.getElementById('editPosName').value = btn.getAttribute('data-name');
            document.getElementById('editPosType').value = btn.getAttribute('data-type');
            document.getElementById('editPosActive').checked = (btn.getAttribute('data-active') === '1');
        });
    }
    
    if (assocModal) {
        assocModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            const positionId = btn.getAttribute('data-position-id');
            document.getElementById('assocPositionName').innerText = btn.getAttribute('data-position-name');
            document.getElementById('assocPositionType').innerText = btn.getAttribute('data-position-type');
            document.getElementById('assocElectionTitle').innerText = btn.getAttribute('data-election-title');
            
            const form = document.getElementById('associatePositionForm');
            const baseUrl = form.getAttribute('data-base-url') || window.location.origin;
            form.action = baseUrl + '/admin-ui/positions/' + positionId + '/associate/';
        });
    }
}

// ==================== ELECTION MODALS ====================

function initializeElectionModals() {
    const deleteModal = document.getElementById('deleteElectionModal');
    const editModal = document.getElementById('editElectionModal');
    
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            document.getElementById('deleteElectionId').value = btn.getAttribute('data-eid');
            document.getElementById('deleteElectionTitle').innerText = btn.getAttribute('data-title');
        });
    }
    
    if (editModal) {
        editModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            const url = btn.getAttribute('data-edit-url');
            document.getElementById('editElectionForm').action = url;
            document.getElementById('editElectionId').value = btn.getAttribute('data-id');
            document.getElementById('pauseElectionId').value = btn.getAttribute('data-id');
            document.getElementById('resumeElectionId').value = btn.getAttribute('data-id');
            document.getElementById('endNowElectionId').value = btn.getAttribute('data-id');
            
            const sy = btn.getAttribute('data-start-year');
            const ey = btn.getAttribute('data-end-year');
            document.getElementById('editElectionStartYear').value = sy || '';
            document.getElementById('editElectionEndYear').value = ey || '';
            document.getElementById('editElectionStart').value = btn.getAttribute('data-start');
            document.getElementById('editElectionEnd').value = btn.getAttribute('data-end');
            
            const isActive = (btn.getAttribute('data-active') === '1');
            document.getElementById('editElectionActive').checked = isActive;
            
            // Toggle Pause/Resume visibility
            document.getElementById('pauseForm').style.display = isActive ? 'inline-block' : 'none';
            document.getElementById('resumeForm').style.display = isActive ? 'none' : 'inline-block';
            
            updateComputedTitle();
        });
        
        // Year input listeners
        ['editElectionStartYear', 'editElectionEndYear'].forEach(function(id) {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', function() {
                    const sy = parseInt(document.getElementById('editElectionStartYear').value || 0, 10);
                    const ey = sy ? sy + 1 : '';
                    if (id === 'editElectionStartYear' && sy) {
                        document.getElementById('editElectionEndYear').value = ey;
                    }
                    updateComputedTitle();
                });
            }
        });
        
        // Create election year inputs
        ['createElectionStartYear', 'createElectionEndYear'].forEach(function(id) {
            const el = document.getElementById(id);
            if (el) {
                el.addEventListener('input', function() {
                    const sy = parseInt(document.getElementById('createElectionStartYear').value || 0, 10);
                    const ey = sy ? sy + 1 : '';
                    if (id === 'createElectionStartYear' && sy) {
                        document.getElementById('createElectionEndYear').value = ey;
                    }
                    updateCreateComputedTitle();
                });
            }
        });
    }
}

function updateComputedTitle() {
    const sy = parseInt(document.getElementById('editElectionStartYear').value || 0, 10);
    const ey = parseInt(document.getElementById('editElectionEndYear').value || 0, 10);
    const out = document.getElementById('computedElectionTitle');
    if (out) {
        out.innerText = (sy && ey) ? 'SY ' + sy + '-' + ey : '';
    }
}

function updateCreateComputedTitle() {
    const sy = parseInt(document.getElementById('createElectionStartYear').value || 0, 10);
    const ey = parseInt(document.getElementById('createElectionEndYear').value || 0, 10);
    const out = document.getElementById('computedCreateTitle');
    if (out) {
        out.innerText = (sy && ey) ? 'SY ' + sy + '-' + ey : '';
    }
}

// ==================== COURSE MODALS ====================

function initializeCourseModals() {
    const editModal = document.getElementById('editCourseModal');
    const deleteModal = document.getElementById('deleteCourseModal');
    
    if (editModal) {
        editModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            const courseId = btn.getAttribute('data-course-id');
            document.getElementById('editCourseId').value = courseId;
            document.getElementById('editCourseForm').action = window.location.origin + '/admin-ui/courses/' + courseId + '/edit/';
            document.getElementById('editCourseName').value = btn.getAttribute('data-name');
            document.getElementById('editCourseCode').value = btn.getAttribute('data-code');
            document.getElementById('editCourseDept').value = btn.getAttribute('data-department');
            document.getElementById('editCourseDesc').value = btn.getAttribute('data-description') || '';
        });
    }
    
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            document.getElementById('deleteCourseId').value = btn.getAttribute('data-course-id');
            document.getElementById('deleteCourseName').innerText = btn.getAttribute('data-name');
        });
    }
}

// ==================== DEPARTMENT MODALS ====================

function initializeDepartmentModals() {
    const editModal = document.getElementById('editDepartmentModal');
    const deleteModal = document.getElementById('deleteDepartmentModal');
    
    if (editModal) {
        editModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            const deptId = btn.getAttribute('data-dept-id');
            document.getElementById('editDepartmentId').value = deptId;
            document.getElementById('editDepartmentForm').action = window.location.origin + '/admin-ui/departments/' + deptId + '/edit/';
            document.getElementById('editDepartmentName').value = btn.getAttribute('data-name');
            document.getElementById('editDepartmentCode').value = btn.getAttribute('data-code');
            document.getElementById('editDepartmentDesc').value = btn.getAttribute('data-description') || '';
        });
    }
    
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            document.getElementById('deleteDepartmentId').value = btn.getAttribute('data-dept-id');
            document.getElementById('deleteDepartmentName').innerText = btn.getAttribute('data-name');
        });
    }
}

// ==================== CANDIDATE MODALS ====================

function initializeCandidateModals() {
    const deleteModal = document.getElementById('deleteCandidateModal');
    const editModal = document.getElementById('editCandidateModal');
    
    if (deleteModal) {
        deleteModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            document.getElementById('deleteCandidateId').value = btn.getAttribute('data-candidate-id');
            document.getElementById('deleteCandidateName').innerText = btn.getAttribute('data-candidate-name');
            document.getElementById('deleteReason').value = '';
        });
    }
    
    if (editModal) {
        editModal.addEventListener('show.bs.modal', function(e) {
            const btn = e.relatedTarget;
            const name = btn.getAttribute('data-candidate-name');
            const partyId = btn.getAttribute('data-party-id') || '';
            const isActive = btn.getAttribute('data-is-active') === '1';
            const editUrl = btn.getAttribute('data-edit-url');
            
            document.getElementById('editCandidateName').value = name;
            const select = document.getElementById('editParty');
            if (select) select.value = partyId;
            document.getElementById('editIsActive').checked = isActive;
            document.getElementById('quickEditForm').action = editUrl;
        });
    }
}

// ==================== DRAG AND DROP ====================

/**
 * Initialize drag and drop for positions reordering
 */
function initializePositionsDragDrop() {
    const tbody = document.getElementById('positionsTbody');
    if (!tbody) return;
    
    let dragging;
    
    tbody.querySelectorAll('tr').forEach(tr => {
        tr.draggable = true;
        
        tr.addEventListener('dragstart', e => {
            dragging = tr;
            tr.classList.add('table-active');
        });
        
        tr.addEventListener('dragend', e => {
            dragging = null;
            tr.classList.remove('table-active');
            sendPositionsOrder();
        });
        
        tr.addEventListener('dragover', e => {
            e.preventDefault();
            const target = e.currentTarget;
            if (dragging && target !== dragging) {
                const rect = target.getBoundingClientRect();
                const after = (e.clientY - rect.top) / (rect.bottom - rect.top) > .5;
                tbody.insertBefore(dragging, after ? target.nextSibling : target);
            }
        });
    });
}

function sendPositionsOrder() {
    const tbody = document.getElementById('positionsTbody');
    if (!tbody) return;
    
    const order = Array.from(tbody.querySelectorAll('tr')).map(tr => tr.getAttribute('data-id'));
    const url = window.location.origin + '/admin-ui/positions/reorder/';
    
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ order })
    })
    .then(r => r.json())
    .then(data => {
        if (!data.success) {
            alert('Reorder failed: ' + (data.error || 'Unknown error'));
        } else {
            location.reload();
        }
    })
    .catch(err => {
        console.error(err);
        alert('Reorder failed');
    });
}

// ==================== PASSWORD MODAL ====================

function openPasswordModal(username, password) {
    const overlay = document.getElementById('pwModal');
    if (!overlay) {
        console.error('Password modal element not found!');
        return;
    }
    
    overlay.querySelector('.js-username').textContent = username;
    overlay.querySelector('.js-password').textContent = password;
    overlay.classList.add('show');
    
    // Prevent body scroll when modal is open
    document.body.style.overflow = 'hidden';
    
    // Focus on the modal for accessibility
    overlay.focus();
}

function closePasswordModal() {
    const overlay = document.getElementById('pwModal');
    if (!overlay) {
        console.error('Password modal element not found!');
        return;
    }
    
    overlay.classList.remove('show');
    
    // Restore body scroll
    document.body.style.overflow = '';
}

function copyPassword() {
    const pw = document.querySelector('#pwModal .js-password').textContent;
    navigator.clipboard.writeText(pw).then(() => {
        const btn = document.getElementById('copyPwBtn');
        const old = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => btn.textContent = old, 1500);
    });
}

function resetPassword(userId, username, urlFromBtn) {
    if (!confirm('Reset password for ' + username + '?')) return;
    // Prefer URL provided by button's data attribute (exact Django reverse)
    const url = urlFromBtn || (window.location.origin + '/admin-ui/users/' + userId + '/reset-password/');
    
    fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    })
    .then(async r => {
        const contentType = r.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            const text = await r.text();
            throw new Error('Non-JSON response (' + r.status + '): ' + (r.url || url) + '\n' + text.slice(0, 200));
        }
        return r.json();
    })
    .then(data => {
        if (data.success) {
            openPasswordModal(data.username, data.new_password);
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(err => alert('Request failed: ' + err));
}

// ==================== USER EDIT MODAL ====================

/**
 * Open the edit user modal and populate with user data
 */
function openEditModal(userId) {
    const modal = document.getElementById('editUserModal');
    const form = document.getElementById('editUserForm');
    const modalTitle = document.getElementById('editUserModalLabel');
    
    if (!modal || !form || !modalTitle) {
        console.error('Edit user modal elements not found!');
        return;
    }
    
    // Fetch user data
    fetch(window.location.pathname + '?get_user_data=' + userId, {
        credentials: 'same-origin',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    })
        .then(async r => {
            const contentType = r.headers.get('content-type') || '';
            if (!contentType.includes('application/json')) {
                const text = await r.text();
                throw new Error('Non-JSON response (' + r.status + '): ' + (r.url || window.location.pathname) + '\n' + text.slice(0, 200));
            }
            return r.json();
        })
        .then(data => {
            if (data.success) {
                // Populate form fields
                form.querySelector('[name="user_id"]').value = data.user.id;
                form.querySelector('[name="first_name"]').value = data.user.first_name || '';
                form.querySelector('[name="last_name"]').value = data.user.last_name || '';
                form.querySelector('[name="email"]').value = data.user.email || '';
                form.querySelector('[name="student_id"]').value = data.profile.student_id || '';
                form.querySelector('[name="year_level"]').value = data.profile.year_level || '';
                form.querySelector('[name="course"]').value = data.profile.course_id || '';
                form.querySelector('[name="is_active"]').checked = data.user.is_active;
                form.querySelector('[name="is_staff"]').checked = data.user.is_staff;
                form.querySelector('[name="is_superuser"]').checked = data.user.is_superuser;
                form.querySelector('[name="is_verified"]').checked = data.profile.is_verified;
                
                modalTitle.textContent = 'Edit User - ' + data.user.username;
                
                // Show modal
                const bsModal = new bootstrap.Modal(modal);
                bsModal.show();
            } else {
                alert('Error loading user data: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(err => {
            console.error('Error fetching user data:', err);
            alert('Request failed: ' + err);
        });
}

/**
 * Close the edit user modal
 */
function closeEditModal() {
    const modal = document.getElementById('editUserModal');
    const bsModal = bootstrap.Modal.getInstance(modal);
    if (bsModal) {
        bsModal.hide();
    }
}

/**
 * Save user edit via AJAX
 */
function saveUserEdit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCsrfToken(),
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'application/json'
        }
    })
    .then(async r => {
        const contentType = r.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
            const text = await r.text();
            throw new Error('Non-JSON response (' + r.status + '): ' + (r.url || form.action) + '\n' + text.slice(0, 200));
        }
        return r.json();
    })
    .then(data => {
        if (data.success) {
            closeEditModal();
            location.reload(); // Reload to show updated data
        } else {
            alert('Error saving user: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(err => {
        console.error('Error saving user:', err);
        alert('Request failed: ' + err);
    });
}

/**
 * Initialize user management event listeners
 */
function initializeUserManagement() {
    // Reset password buttons
    document.querySelectorAll('.reset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            const username = this.getAttribute('data-username');
            const resetUrl = this.getAttribute('data-reset-url');
            resetPassword(userId, username, resetUrl);
        });
    });
    
    // Edit user buttons
    document.querySelectorAll('.edit-user-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id');
            openEditModal(userId);
        });
    });
    
    // Edit user form submit
    const editForm = document.getElementById('editUserForm');
    if (editForm) {
        editForm.addEventListener('submit', saveUserEdit);
    }
    
    // Close modals on Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closePasswordModal();
            closeEditModal();
        }
    });

    // Initialize search autocomplete
    initializeUserSearchAutocomplete();
}

// ==================== DEPARTMENT DELETION ====================

function initializeDepartmentDeletion() {
    const reassignRadio = document.getElementById('reassignCourses');
    const departmentSelect = document.getElementById('departmentSelect');
    
    if (reassignRadio && departmentSelect) {
        reassignRadio.addEventListener('change', function() {
            departmentSelect.style.display = this.checked ? 'block' : 'none';
        });
    }
    
    const form = document.getElementById('deleteForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            const selectedAction = document.querySelector('input[name="action"]:checked');
            if (!selectedAction) {
                e.preventDefault();
                alert('Please select an action before proceeding.');
                return false;
            }
            
            if (selectedAction.value === 'reassign_courses') {
                const selectedDept = document.getElementById('new_department_id').value;
                if (!selectedDept) {
                    e.preventDefault();
                    alert('Please select a department to reassign courses to.');
                    return false;
                }
            }
        });
    }
}

// ==================== INITIALIZATION ====================

/**
 * Initialize all admin module functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize modals
    initializeModals();
    
    // Initialize drag and drop for positions
    initializePositionsDragDrop();
    
    // Initialize department deletion handling
    initializeDepartmentDeletion();
    
    // Initialize user management (edit, reset password)
    initializeUserManagement();
});

// Export functions for global access
window.AdminModule = {
    getCsrfToken,
    getCookie,
    openPasswordModal,
    closePasswordModal,
    copyPassword,
    resetPassword,
    openEditModal,
    closeEditModal,
    saveUserEdit,
    updateComputedTitle,
    updateCreateComputedTitle
};

// ==================== USER SEARCH AUTOCOMPLETE ====================

function initializeUserSearchAutocomplete() {
    const searchInput = document.querySelector('input[name="search"]');
    if (!searchInput) return;
    
    // Ensure parent is relatively positioned for absolute dropdown
    const parent = searchInput.parentElement;
    if (parent && getComputedStyle(parent).position === 'static') {
        parent.style.position = 'relative';
    }
    
    const menu = document.createElement('div');
    menu.className = 'list-group shadow-sm';
    menu.style.position = 'absolute';
    menu.style.top = '100%';
    menu.style.left = '0';
    menu.style.right = '0';
    menu.style.zIndex = '1050';
    menu.style.maxHeight = '260px';
    menu.style.overflowY = 'auto';
    menu.style.display = 'none';
    menu.setAttribute('role', 'listbox');
    parent.appendChild(menu);
    
    let currentIndex = -1;
    let items = [];
    let lastQuery = '';
    
    const hideMenu = () => {
        menu.style.display = 'none';
        menu.innerHTML = '';
        currentIndex = -1;
        items = [];
    };
    
    const showMenu = () => {
        if (items.length === 0) {
            hideMenu();
            return;
        }
        menu.style.display = 'block';
    };
    
    const renderResults = (results) => {
        menu.innerHTML = '';
        items = results.map((r, idx) => {
            const a = document.createElement('button');
            a.type = 'button';
            a.className = 'list-group-item list-group-item-action';
            a.textContent = r.text;
            a.setAttribute('role', 'option');
            a.addEventListener('click', () => {
                searchInput.value = r.display_name || r.username || r.text;
                hideMenu();
                // Submit the filter form immediately
                const form = searchInput.closest('form');
                if (form) form.requestSubmit ? form.requestSubmit() : form.submit();
            });
            menu.appendChild(a);
            return a;
        });
        showMenu();
    };
    
    const debounce = (fn, ms) => {
        let t;
        return (...args) => {
            clearTimeout(t);
            t = setTimeout(() => fn.apply(null, args), ms);
        };
    };
    
    const fetchResults = debounce((q) => {
        if (!q || q.length < 2) { hideMenu(); return; }
        if (q === lastQuery) return; // skip duplicate
        lastQuery = q;
        const url = '/admin-ui/users/autocomplete/?q=' + encodeURIComponent(q);
        fetch(url, {
            credentials: 'same-origin',
            headers: { 'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json' }
        })
        .then(r => r.json())
        .then(data => renderResults((data && data.results) || []))
        .catch(() => hideMenu());
    }, 200);
    
    searchInput.addEventListener('input', () => fetchResults(searchInput.value.trim()));
    searchInput.addEventListener('focus', () => {
        if (items.length > 0) showMenu();
    });
    document.addEventListener('click', (e) => {
        if (!parent.contains(e.target)) hideMenu();
    });
    
    // Keyboard navigation
    searchInput.addEventListener('keydown', (e) => {
        if (menu.style.display === 'none') return;
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            currentIndex = (currentIndex + 1) % items.length;
            items.forEach((el, i) => el.classList.toggle('active', i === currentIndex));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            currentIndex = (currentIndex - 1 + items.length) % items.length;
            items.forEach((el, i) => el.classList.toggle('active', i === currentIndex));
        } else if (e.key === 'Enter' && currentIndex >= 0) {
            e.preventDefault();
            items[currentIndex].click();
        } else if (e.key === 'Escape') {
            hideMenu();
        }
    });
}

