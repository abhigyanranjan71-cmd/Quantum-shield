/**
 * QuantumShield Client Script
 * Responsive interactions, mobile drawer, and HTMX animation hooks
 */

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Sidebar Drawer Toggle
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('sidebar');

  if (mobileMenuBtn && sidebar) {
    mobileMenuBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      sidebar.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== mobileMenuBtn) {
        sidebar.classList.remove('open');
      }
    });
  }

  // HTMX Event Animation Hooks
  document.body.addEventListener('htmx:beforeRequest', function(evt) {
    // Optional request pre-flight hook
  });

  document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Fade in dynamic updates
    if (evt.detail.target) {
      evt.detail.target.style.opacity = '0';
      evt.detail.target.style.transition = 'opacity 0.3s ease';
      requestAnimationFrame(() => {
        evt.detail.target.style.opacity = '1';
      });
    }
  });
});
