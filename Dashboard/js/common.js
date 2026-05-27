/**
 * TrafficIQ Common Scripts
 * Contains shared functionality across all dashboard pages.
 */

document.addEventListener("DOMContentLoaded", () => {
    // 1. Initialize Clock
    initClock();

    // 2. Active Sidebar State
    highlightActiveSidebar();

    // 3. Auth Check (optional: already in auth.js but good to have a backup)
    if (typeof checkAuth === 'function') {
        checkAuth();
    }
});

/**
 * Updates the clock element in the header
 */
function initClock() {
    const clockElement = document.getElementById("clock");
    if (!clockElement) return;

    function updateClock() {
    const now = new Date();
    const istTime = now.toLocaleTimeString("en-IN", {
        timeZone: "Asia/Kolkata",
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
    clockElement.innerHTML = istTime;
}

    updateClock();
    setInterval(updateClock, 1000);
}

/**
 * Automatically highlights the active link in the sidebar based on current URL
 */
function highlightActiveSidebar() {
    const currentPath = window.location.pathname.split("/").pop() || "index.html";
    const sidebarLinks = document.querySelectorAll(".sidebar nav ul li a");

    sidebarLinks.forEach(link => {
        const href = link.getAttribute("href");
        const parentLi = link.parentElement;
        
        if (href === currentPath) {
            parentLi.classList.add("active");
        } else {
            parentLi.classList.remove("active");
        }
    });
}

/**
 * Global Error Handler for Fetch
 */
window.handleFetchError = function(error, componentName) {
    console.error(`[${componentName}] Fetch Error:`, error);
    // Potentially show a toast or notification
}
