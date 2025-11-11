/**
 * Profile Page JavaScript
 * Handles profile editing, department/course selection, password changes, etc.
 * 
 * Dependencies: Bootstrap 5, Fetch API
 */

// ========================================
// CONFIGURATION
// ========================================

const ProfileConfig = {
    API_ENDPOINTS: {
        COURSES_BY_DEPARTMENT: '/api/courses/',
        GENERATE_STUDENT_ID: '/api/generate-student-id/'
    },
    SELECTORS: {
        DEPARTMENT_SELECT: '#department',
        COURSE_SELECT: '#course',
        STUDENT_ID_INPUT: '#student_id',
        GENERATE_STUDENT_ID_BTN: '#generateStudentId',
        PASSWORD_TOGGLE_BTN: '#togglePw',
        PASSWORD_SECTION: '#pwSection',
        USERNAME_INPUT: 'input[name="username"]',
        USERNAME_CHANGE_BTN: 'button[onclick="toggleUsernameChange()"]'
    }
};

// ========================================
// UTILITY FUNCTIONS
// ========================================

/**
 * Display a message alert to the user
 * @param {string} message - The message to display
 * @param {string} type - 'success' or 'error'
 */
function showMessage(message, type) {
    console.log('[MESSAGE]', type, message);
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
    messageDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const form = document.querySelector('form');
    if (form) {
        form.insertBefore(messageDiv, form.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.remove();
            }
        }, 5000);
    }
}

/**
 * Get CSRF token from the page
 * @returns {string} CSRF token value
 */
function getCSRFToken() {
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfInput ? csrfInput.value : '';
}

// ========================================
// DEPARTMENT & COURSE DROPDOWN HANDLER
// ========================================

const DepartmentCourseHandler = {
    departmentSelect: null,
    courseSelect: null,
    currentDepartmentId: null,
    currentCourseId: null,
    
    /**
     * Initialize the department/course handler
     */
    init: function() {
        console.log('[DEPT-COURSE] Initializing...');
        
        this.departmentSelect = document.querySelector(ProfileConfig.SELECTORS.DEPARTMENT_SELECT);
        this.courseSelect = document.querySelector(ProfileConfig.SELECTORS.COURSE_SELECT);
        
        if (!this.departmentSelect || !this.courseSelect) {
            console.error('[DEPT-COURSE] ERROR: Selects not found');
            return;
        }
        
        // Store initial values
        this.currentDepartmentId = this.departmentSelect.value;
        this.currentCourseId = this.courseSelect.value;
        
        console.log('[DEPT-COURSE] Initial state:', {
            departmentId: this.currentDepartmentId,
            courseId: this.currentCourseId,
            courseDisabled: this.courseSelect.disabled
        });
        
        // Set up event listener
        this.departmentSelect.addEventListener('change', this.handleDepartmentChange.bind(this));
        
        console.log('[DEPT-COURSE] Event listener attached');
    },
    
    /**
     * Handle department selection change
     * @param {Event} event - Change event
     */
    handleDepartmentChange: function(event) {
        const departmentId = event.target.value;
        
        console.log('[DEPT-COURSE] Department changed:', {
            oldValue: this.currentDepartmentId,
            newValue: departmentId
        });
        
        this.currentDepartmentId = departmentId;
        
        // Clear and reset course dropdown
        this.clearCourseDropdown();
        
        if (departmentId) {
            this.loadCourses(departmentId);
        } else {
            this.courseSelect.disabled = true;
            console.log('[DEPT-COURSE] No department selected, course dropdown disabled');
        }
    },
    
    /**
     * Clear the course dropdown
     */
    clearCourseDropdown: function() {
        console.log('[DEPT-COURSE] Clearing course dropdown');
        this.courseSelect.innerHTML = '<option value="">Select Course</option>';
        this.courseSelect.value = '';
        this.currentCourseId = '';
    },
    
    /**
     * Load courses for the selected department
     * @param {string|number} departmentId - Department ID
     */
    loadCourses: function(departmentId) {
        console.log('[DEPT-COURSE] Loading courses for department:', departmentId);
        
        // Enable dropdown and show loading state
        this.courseSelect.disabled = false;
        this.courseSelect.innerHTML = '<option value="">Loading courses...</option>';
        
        const url = ProfileConfig.API_ENDPOINTS.COURSES_BY_DEPARTMENT + departmentId + '/';
        console.log('[DEPT-COURSE] Fetching from:', url);
        
        fetch(url)
            .then(response => {
                console.log('[DEPT-COURSE] Response status:', response.status);
                if (!response.ok) {
                    throw new Error('HTTP error! status: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log('[DEPT-COURSE] API Response:', data);
                
                if (data.success) {
                    this.populateCourses(data.courses);
                } else {
                    console.error('[DEPT-COURSE] API returned error:', data.error);
                    showMessage('Error loading courses: ' + data.error, 'error');
                    this.clearCourseDropdown();
                    this.courseSelect.disabled = true;
                }
            })
            .catch(error => {
                console.error('[DEPT-COURSE] Fetch error:', error);
                showMessage('Error loading courses. Please try again.', 'error');
                this.clearCourseDropdown();
                this.courseSelect.disabled = true;
            });
    },
    
    /**
     * Populate the course dropdown with courses
     * @param {Array} courses - Array of course objects
     */
    populateCourses: function(courses) {
        console.log('[DEPT-COURSE] Populating', courses.length, 'courses');
        
        // Clear and add default option
        this.courseSelect.innerHTML = '<option value="">Select Course</option>';
        
        if (courses.length === 0) {
            console.warn('[DEPT-COURSE] No courses found for this department');
            this.courseSelect.innerHTML = '<option value="">No courses available</option>';
            this.courseSelect.disabled = true;
            return;
        }
        
        // Add each course
        courses.forEach(course => {
            const option = document.createElement('option');
            option.value = course.id;
            option.textContent = course.name + ' (' + course.code + ')';
            
            // Re-select if this was the previous selection
            if (course.id == this.currentCourseId) {
                option.selected = true;
                console.log('[DEPT-COURSE] Re-selected course:', course.id);
            }
            
            this.courseSelect.appendChild(option);
        });
        
        this.courseSelect.disabled = false;
        console.log('[DEPT-COURSE] Courses loaded successfully');
    }
};

// ========================================
// PASSWORD TOGGLE
// ========================================

/**
 * Initialize password change section toggle
 */
function initPasswordToggle() {
    console.log('[PASSWORD] Initializing toggle');
    
    const btn = document.querySelector(ProfileConfig.SELECTORS.PASSWORD_TOGGLE_BTN);
    const section = document.querySelector(ProfileConfig.SELECTORS.PASSWORD_SECTION);
    
    if (!btn || !section) {
        console.error('[PASSWORD] Toggle elements not found');
        return;
    }
    
    btn.addEventListener('click', function() {
        const isOpen = section.style.display !== 'none';
        section.style.display = isOpen ? 'none' : 'block';
        btn.textContent = isOpen ? 'Change Password' : 'Hide Password Change';
        console.log('[PASSWORD] Toggled:', !isOpen ? 'open' : 'closed');
    });
}

// ========================================
// USERNAME CHANGE
// ========================================

/**
 * Toggle username edit mode
 * This function is called from onclick in HTML
 */
function toggleUsernameChange() {
    console.log('[USERNAME] Toggle clicked');
    
    const usernameInput = document.querySelector(ProfileConfig.SELECTORS.USERNAME_INPUT);
    const changeBtn = document.querySelector(ProfileConfig.SELECTORS.USERNAME_CHANGE_BTN);
    
    if (!usernameInput || !changeBtn) {
        console.error('[USERNAME] Elements not found');
        return;
    }
    
    if (usernameInput.disabled) {
        // Enable edit mode
        usernameInput.disabled = false;
        usernameInput.focus();
        changeBtn.innerHTML = '<i class="fas fa-save"></i> Save';
        changeBtn.classList.remove('btn-outline-info');
        changeBtn.classList.add('btn-success');
        console.log('[USERNAME] Edit mode enabled');
    } else {
        // Validate and confirm
        const newUsername = usernameInput.value.trim();
        console.log('[USERNAME] Validating:', newUsername);
        
        if (newUsername.length < 3) {
            alert('Username must be at least 3 characters long.');
            return;
        }
        if (!/^[a-zA-Z0-9._-]+$/.test(newUsername)) {
            alert('Username can only contain letters, numbers, dots, underscores, and hyphens.');
            return;
        }
        
        if (confirm('Are you sure you want to change your username to "' + newUsername + '"? This will affect your login.')) {
            usernameInput.disabled = true;
            changeBtn.innerHTML = '<i class="fas fa-edit"></i> Change';
            changeBtn.classList.remove('btn-success');
            changeBtn.classList.add('btn-outline-info');
            
            const successMsg = document.createElement('div');
            successMsg.className = 'alert alert-success alert-dismissible fade show mt-2';
            successMsg.innerHTML = `
                <i class="fas fa-check-circle me-2"></i>
                Username will be updated when you save your profile.
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            usernameInput.parentNode.parentNode.appendChild(successMsg);
            
            setTimeout(() => {
                if (successMsg.parentNode) {
                    successMsg.remove();
                }
            }, 3000);
            
            console.log('[USERNAME] Username change confirmed');
        } else {
            // Reset to original value - get from data attribute or keep current
            console.log('[USERNAME] Change cancelled');
        }
    }
}

// Make toggleUsernameChange available globally for onclick
window.toggleUsernameChange = toggleUsernameChange;

// ========================================
// STUDENT ID GENERATION
// ========================================

/**
 * Initialize student ID generation button
 */
function initStudentIdGeneration() {
    console.log('[STUDENT-ID] Initializing');
    
    const generateBtn = document.querySelector(ProfileConfig.SELECTORS.GENERATE_STUDENT_ID_BTN);
    
    if (!generateBtn) {
        console.log('[STUDENT-ID] Generate button not found (may be regular user)');
        return;
    }
    
    generateBtn.addEventListener('click', function() {
        console.log('[STUDENT-ID] Generate clicked');
        
        const studentIdInput = document.querySelector(ProfileConfig.SELECTORS.STUDENT_ID_INPUT);
        
        if (!studentIdInput) {
            console.error('[STUDENT-ID] Input not found');
            return;
        }
        
        // Simple client-side generation
        const currentYear = new Date().getFullYear();
        const randomNum = Math.floor(Math.random() * 90000) + 10000;
        const studentId = currentYear + '-' + randomNum;
        
        studentIdInput.value = studentId;
        console.log('[STUDENT-ID] Generated:', studentId);
    });
}

// ========================================
// INITIALIZATION
// ========================================

/**
 * Initialize all profile page components
 */
function initProfilePage() {
    console.log('[PROFILE] Page loaded, initializing all components...');
    
    try {
        // Initialize all components
        initPasswordToggle();
        initStudentIdGeneration();
        DepartmentCourseHandler.init();
        
        console.log('[PROFILE] All components initialized successfully');
    } catch (error) {
        console.error('[PROFILE] Initialization error:', error);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProfilePage);
} else {
    // DOM already loaded
    initProfilePage();
}

