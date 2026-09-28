// ==================== GLOBAL UTILITIES ====================

// Flash message auto-dismiss
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease forwards';
            setTimeout(() => message.remove(), 300);
        }, 5000);
    });
});

// Slide out animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ==================== SMOOTH SCROLLING ====================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ==================== FORM VALIDATION ====================

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateURL(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

// Add real-time validation to forms
document.querySelectorAll('input[type="email"]').forEach(input => {
    input.addEventListener('blur', function() {
        if (this.value && !validateEmail(this.value)) {
            this.style.borderColor = 'var(--danger)';
            showValidationError(this, 'Please enter a valid email address');
        } else {
            this.style.borderColor = 'var(--border-color)';
            hideValidationError(this);
        }
    });
});

document.querySelectorAll('input[type="url"]').forEach(input => {
    input.addEventListener('blur', function() {
        if (this.value && !validateURL(this.value)) {
            this.style.borderColor = 'var(--danger)';
            showValidationError(this, 'Please enter a valid URL');
        } else {
            this.style.borderColor = 'var(--border-color)';
            hideValidationError(this);
        }
    });
});

function showValidationError(element, message) {
    hideValidationError(element); // Remove existing error
    const error = document.createElement('div');
    error.className = 'validation-error';
    error.textContent = message;
    error.style.cssText = `
        color: var(--danger);
        font-size: 0.875rem;
        margin-top: 0.375rem;
        animation: fadeIn 0.3s ease;
    `;
    element.parentNode.appendChild(error);
}

function hideValidationError(element) {
    const error = element.parentNode.querySelector('.validation-error');
    if (error) error.remove();
}

// ==================== KEYBOARD SHORTCUTS ====================

document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K: Focus search (if exists)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"]');
        if (searchInput) searchInput.focus();
    }
    
    // Escape: Close modals
    if (e.key === 'Escape') {
        const modal = document.querySelector('.loading-modal.active');
        if (modal && !modal.dataset.preventClose) {
            modal.classList.remove('active');
        }
    }
});

// ==================== COPY TO CLIPBOARD ====================

function copyToClipboard(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    try {
        document.execCommand('copy');
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        showNotification('Failed to copy', 'danger');
    }
    document.body.removeChild(textarea);
}

// ==================== NOTIFICATION SYSTEM ====================

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)}"></i>
        <span>${message}</span>
    `;
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 2rem;
        padding: 1rem 1.5rem;
        background: rgba(30, 41, 59, 0.95);
        border: 1px solid var(--border-color);
        border-radius: 0.5rem;
        color: var(--text-primary);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        animation: slideIn 0.3s ease;
        backdrop-filter: blur(20px);
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        danger: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// ==================== LOADING INDICATOR ====================

function showLoading(message = 'Processing...') {
    const modal = document.getElementById('loadingModal');
    if (modal) {
        const text = modal.querySelector('.loading-text');
        if (text) text.textContent = message;
        modal.classList.add('active');
    }
}

function updateLoading(message) {
    const text = document.querySelector('.loading-text');
    if (text) text.textContent = message;
}

function hideLoading() {
    const modal = document.getElementById('loadingModal');
    if (modal) modal.classList.remove('active');
}

// ==================== TOOLTIPS ====================

function initTooltips() {
    document.querySelectorAll('[title]').forEach(element => {
        element.addEventListener('mouseenter', function(e) {
            const tooltip = document.createElement('div');
            tooltip.className = 'custom-tooltip';
            tooltip.textContent = this.getAttribute('title');
            tooltip.style.cssText = `
                position: fixed;
                background: rgba(17, 24, 39, 0.95);
                color: var(--text-primary);
                padding: 0.5rem 0.75rem;
                border-radius: 0.375rem;
                font-size: 0.875rem;
                z-index: 10001;
                pointer-events: none;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                border: 1px solid var(--border-color);
                backdrop-filter: blur(10px);
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                delete this._tooltip;
            }
        });
    });
}

// Initialize tooltips on page load
document.addEventListener('DOMContentLoaded', initTooltips);

// ==================== SCROLL ANIMATIONS ====================

function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.analysis-card, .history-card, .result-card').forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
}

// Add fade-in animation
const fadeInStyle = document.createElement('style');
fadeInStyle.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(fadeInStyle);

// Initialize scroll animations
document.addEventListener('DOMContentLoaded', observeElements);

// ==================== FILE SIZE FORMATTER ====================

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// ==================== DEBOUNCE FUNCTION ====================

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== LOCAL STORAGE HELPERS ====================

function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error('Failed to save to localStorage:', e);
        return false;
    }
}

function getFromLocalStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Failed to read from localStorage:', e);
        return defaultValue;
    }
}

function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
        return true;
    } catch (e) {
        console.error('Failed to remove from localStorage:', e);
        return false;
    }
}

// ==================== DARK MODE PERSISTENCE ====================

// Save scroll position before page unload
window.addEventListener('beforeunload', () => {
    saveToLocalStorage('scrollPosition', window.scrollY);
});

// Restore scroll position on load
window.addEventListener('load', () => {
    const scrollPosition = getFromLocalStorage('scrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, scrollPosition);
        removeFromLocalStorage('scrollPosition');
    }
});

// ==================== PERFORMANCE MONITORING ====================

if ('performance' in window) {
    window.addEventListener('load', () => {
        setTimeout(() => {
            const perfData = performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`Page load time: ${pageLoadTime}ms`);
        }, 0);
    });
}

// ==================== ACCESSIBILITY ENHANCEMENTS ====================

// Add focus visible for keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        document.body.classList.add('user-is-tabbing');
    }
});

document.addEventListener('mousedown', () => {
    document.body.classList.remove('user-is-tabbing');
});

// Add focus styles
const focusStyle = document.createElement('style');
focusStyle.textContent = `
    body.user-is-tabbing *:focus {
        outline: 2px solid var(--accent-blue);
        outline-offset: 2px;
    }
    
    body:not(.user-is-tabbing) *:focus {
        outline: none;
    }
`;
document.head.appendChild(focusStyle);

// ==================== NETWORK STATUS INDICATOR ====================

window.addEventListener('online', () => {
    showNotification('Connection restored', 'success');
});

window.addEventListener('offline', () => {
    showNotification('No internet connection', 'warning');
});

// ==================== ERROR HANDLING ====================

window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    // Don't show notification for every error, only critical ones
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
});

// ==================== PRINT OPTIMIZATION ====================

window.addEventListener('beforeprint', () => {
    // Expand all collapsible sections for printing
    document.querySelectorAll('.result-detail-content').forEach(el => {
        el.dataset.originalDisplay = el.style.display;
        el.style.display = 'block';
    });
});

window.addEventListener('afterprint', () => {
    // Restore original state after printing
    document.querySelectorAll('.result-detail-content').forEach(el => {
        el.style.display = el.dataset.originalDisplay || 'none';
        delete el.dataset.originalDisplay;
    });
});

// ==================== EXPORT FUNCTIONALITY ====================

function exportResultsAsJSON() {
    const results = {
        timestamp: new Date().toISOString(),
        statistics: getStatistics(),
        results: getAllResults()
    };
    
    const dataStr = JSON.stringify(results, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `security-analysis-${Date.now()}.json`;
    link.click();
    
    URL.revokeObjectURL(url);
    showNotification('Results exported successfully', 'success');
}

function getStatistics() {
    // Extract statistics from the page
    const stats = {};
    document.querySelectorAll('.stat-box').forEach(box => {
        const label = box.querySelector('.stat-label')?.textContent.trim();
        const value = box.querySelector('.stat-value')?.textContent.trim();
        if (label && value) {
            stats[label] = value;
        }
    });
    return stats;
}

function getAllResults() {
    // Extract all results from the page
    const results = [];
    document.querySelectorAll('.result-card').forEach(card => {
        const title = card.querySelector('.result-title')?.textContent.trim();
        const threat = card.querySelector('.threat-badge')?.textContent.trim();
        const score = card.querySelector('.percentage')?.textContent.trim();
        const flags = Array.from(card.querySelectorAll('.flag-item')).map(
            flag => flag.textContent.trim()
        );
        
        results.push({ title, threat, score, flags });
    });
    return results;
}

// ==================== UTILITY FUNCTIONS ====================

// Truncate text with ellipsis
function truncateText(text, maxLength) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Get time ago
function timeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    
    const intervals = {
        year: 31536000,
        month: 2592000,
        week: 604800,
        day: 86400,
        hour: 3600,
        minute: 60
    };
    
    for (const [unit, secondsInUnit] of Object.entries(intervals)) {
        const interval = Math.floor(seconds / secondsInUnit);
        if (interval >= 1) {
            return `${interval} ${unit}${interval > 1 ? 's' : ''} ago`;
        }
    }
    
    return 'just now';
}

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', () => {
    console.log('🛡️ Security Analyzer initialized');
    console.log('Dark theme loaded successfully');
});

// Prevent console tampering (basic protection)
if (typeof console !== 'undefined') {
    console.log('%cStop!', 'color: red; font-size: 40px; font-weight: bold;');
    console.log('%cThis is a browser feature intended for developers.', 'font-size: 16px;');
    console.log('%cIf someone told you to copy/paste something here, it may be a scam.', 'font-size: 16px;');
}

// Export functions to global scope for use in inline scripts
window.copyToClipboard = copyToClipboard;
window.showNotification = showNotification;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.updateLoading = updateLoading;
window.formatFileSize = formatFileSize;
window.exportResultsAsJSON = exportResultsAsJSON;