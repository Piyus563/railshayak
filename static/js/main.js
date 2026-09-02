/**
 * RailSaathi Frontend JavaScript & Dynamic Helpers
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize tooltips & popovers
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Dynamic Fare Calculator for Book Coolie Form
  const bagsInput = document.getElementById('bagsInput');
  const baseFareElem = document.getElementById('displayBaseFare');
  const extraFareElem = document.getElementById('displayExtraFare');
  const totalFareElem = document.getElementById('displayTotalFare');

  function calculateFare() {
    if (!bagsInput || !totalFareElem) return;
    const bags = parseInt(bagsInput.value) || 1;
    const base = 100;
    const extraBags = Math.max(0, bags - 1);
    const extraFare = extraBags * 50;
    const total = base + extraFare;

    if (baseFareElem) baseFareElem.textContent = `₹${base}`;
    if (extraFareElem) extraFareElem.textContent = `₹${extraFare}`;
    if (totalFareElem) totalFareElem.textContent = `₹${total}`;
  }

  if (bagsInput) {
    bagsInput.addEventListener('input', calculateFare);
    bagsInput.addEventListener('change', calculateFare);
    calculateFare();
  }

  // Station selector dynamically updating platform list
  const stationSelect = document.getElementById('stationSelect');
  const platformSelect = document.getElementById('platformSelect');

  if (stationSelect && platformSelect) {
    stationSelect.addEventListener('change', function() {
      const stationId = this.value;
      if (!stationId) return;

      // Update URL param if on station list/booking page
      const currentUrl = new URL(window.location.href);
      const selectedOption = stationSelect.options[stationSelect.selectedIndex];
      const stationCode = selectedOption.getAttribute('data-code');
      if (stationCode) {
        currentUrl.searchParams.set('station', stationCode);
        // Only reload if user is switching station on coolie wizard to refresh coolie list
        if (window.location.pathname.includes('/bookings/book/')) {
          window.location.href = currentUrl.toString();
        }
      }
    });
  }

  // Auto-dismiss alerts after 6 seconds
  const autoAlerts = document.querySelectorAll('.alert-dismissible');
  autoAlerts.forEach(function(alert) {
    setTimeout(function() {
      const bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    }, 6000);
  });
});
