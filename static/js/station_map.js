/**
 * RailSaathi Interactive Leaflet.js Station Map
 */

<<<<<<< HEAD
function initStationMap(mapElementId, stationLat, stationLng, stationName, facilitiesData, platformsData, options) {
  const mapElem = document.getElementById(mapElementId);
  if (!mapElem) return;

  options = options || {};
  const statusElement = document.getElementById(options.statusElementId || 'map-status');
  const setStatus = function(message, type) {
    if (!statusElement) return;
    statusElement.textContent = message;
    statusElement.className = `small text-${type || 'muted'}`;
  };

  if (typeof L === 'undefined') {
    mapElem.innerHTML = '<div class="alert alert-danger m-3">The map library could not be loaded. Please check your internet connection and reload.</div>';
    setStatus('Map library unavailable.', 'danger');
    return;
  }

  const initialLat = parseFloat(stationLat);
  const initialLng = parseFloat(stationLng);
  if (!Number.isFinite(initialLat) || !Number.isFinite(initialLng)) {
    mapElem.innerHTML = '<div class="alert alert-danger m-3">Station location is not available.</div>';
    setStatus('Station coordinates unavailable.', 'danger');
    return;
  }

  // Initialize map centered at station coordinates
  const map = L.map(mapElementId, {
    center: [initialLat, initialLng],
    zoom: 18,
    zoomControl: true,
    scrollWheelZoom: false
  });

  // Add OpenStreetMap tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | RailSaathi Smart Station Map',
    maxZoom: 20
=======
function initStationMap(mapElementId, stationLat, stationLng, stationName, facilitiesData, platformsData) {
  const mapElem = document.getElementById(mapElementId);
  if (!mapElem) return;

  // Initialize map
  const map = L.map(mapElementId, {
    center: [stationLat, stationLng],
    zoom: 17,
    zoomControl: true,
    scrollWheelZoom: true
  });

  // OpenStreetMap tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | RailSaathi',
    maxZoom: 20,
    tileSize: 256,
    zoomOffset: 0
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
  }).addTo(map);

  // Custom Icon Factory
  function createCustomIcon(iconClass, bgGradient) {
    return L.divIcon({
<<<<<<< HEAD
      className: 'custom-leaflet-marker',
      html: `<div style="
        width: 38px;
        height: 38px;
        background: ${bgGradient};
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff;
        font-size: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border: 2px solid #ffffff;
      "><i class="${iconClass}"></i></div>`,
      iconSize: [38, 38],
      iconAnchor: [19, 19],
      popupAnchor: [0, -20]
    });
  }

  // Color mappings by facility type
  const iconConfig = {
    'WASHROOM': { icon: 'fas fa-restroom', bg: 'linear-gradient(135deg, #0284c7, #0369a1)' },
    'DRINKING_WATER': { icon: 'fas fa-tint', bg: 'linear-gradient(135deg, #06b6d4, #0891b2)' },
    'LIFT': { icon: 'fas fa-elevator', bg: 'linear-gradient(135deg, #8b5cf6, #6d28d9)' },
    'ESCALATOR': { icon: 'fas fa-walking', bg: 'linear-gradient(135deg, #6366f1, #4f46e5)' },
    'FOOD': { icon: 'fas fa-utensils', bg: 'linear-gradient(135deg, #f59e0b, #d97706)' },
    'WAITING_ROOM': { icon: 'fas fa-couch', bg: 'linear-gradient(135deg, #10b981, #059669)' },
    'PARKING': { icon: 'fas fa-car', bg: 'linear-gradient(135deg, #64748b, #475569)' },
    'MEDICAL': { icon: 'fas fa-hospital', bg: 'linear-gradient(135deg, #ef4444, #dc2626)' },
    'HELP_DESK': { icon: 'fas fa-info-circle', bg: 'linear-gradient(135deg, #0f2b48, #1e40af)' },
    'CLOAK_ROOM': { icon: 'fas fa-luggage-cart', bg: 'linear-gradient(135deg, #d946ef, #a21caf)' },
    'WHEELCHAIR_POINT': { icon: 'fas fa-wheelchair', bg: 'linear-gradient(135deg, #2563eb, #1d4ed8)' },
  };

  const markersGroup = L.layerGroup().addTo(map);
  let allMarkers = [];
  let userMarker = null;
  let userAccuracy = null;

  const escapeHtml = function(value) {
    return String(value == null ? '' : value).replace(/[&<>'"]/g, function(character) {
      return {'&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'}[character];
    });
  };

  // Add Station Central Marker
  const mainStationIcon = L.divIcon({
    className: 'station-main-marker',
    html: `<div style="
      width: 48px;
      height: 48px;
      background: linear-gradient(135deg, #0f2b48, #2563eb);
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #ffffff;
      font-size: 22px;
      box-shadow: 0 6px 18px rgba(15, 43, 72, 0.4);
      border: 3px solid #ffffff;
    "><i class="fas fa-train"></i></div>`,
    iconSize: [48, 48],
    iconAnchor: [24, 24],
    popupAnchor: [0, -25]
  });

  const mainMarker = L.marker([initialLat, initialLng], { icon: mainStationIcon }).addTo(map);
  mainMarker.bindPopup(`
    <div style="padding: 6px; min-width: 180px;">
      <h6 style="margin: 0 0 4px 0; color: #0f2b48; font-weight: 700;">🚆 ${escapeHtml(stationName)}</h6>
      <p style="margin: 0; font-size: 12px; color: #64748b;">Central Concourse & Porch</p>
    </div>
  `);

  function createPlatformIcon() {
    return L.divIcon({
      className: 'platform-leaflet-marker',
      html: '<div style="width:32px;height:32px;background:#f59e0b;border:2px solid #fff;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;box-shadow:0 3px 10px rgba(0,0,0,.25)"><i class="fas fa-subway"></i></div>',
      iconSize: [32, 32], iconAnchor: [16, 16], popupAnchor: [0, -16]
    });
  }

  function renderLayers(nextFacilities, nextPlatforms) {
    markersGroup.clearLayers();
    allMarkers = [];

    (Array.isArray(nextPlatforms) ? nextPlatforms : []).forEach(function(platform) {
      const lat = parseFloat(platform.latitude);
      const lng = parseFloat(platform.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lng)) return;
      const marker = L.marker([lat, lng], {icon: createPlatformIcon()});
      marker.facilityType = 'PLATFORM';
      marker.bindPopup(`<strong>Platform ${escapeHtml(platform.number)}</strong><br>${escapeHtml(platform.description || 'Platform information')}`);
      marker.addTo(markersGroup);
    });

    (Array.isArray(nextFacilities) ? nextFacilities : []).forEach(function(facility) {
      const type = facility.facility_type;
      const conf = iconConfig[type] || { icon: 'fas fa-map-marker-alt', bg: 'linear-gradient(135deg, #2563eb, #1d4ed8)' };
      const icon = createCustomIcon(conf.icon, conf.bg);

      const lat = parseFloat(facility.latitude);
      const lng = parseFloat(facility.longitude);

      if (Number.isFinite(lat) && Number.isFinite(lng)) {
        const marker = L.marker([lat, lng], { icon: icon });
        const popupContent = `
          <div style="padding: 8px; min-width: 200px;">
            <div style="font-size: 11px; font-weight: 700; color: #2563eb; text-transform: uppercase; margin-bottom: 2px;">
              ${escapeHtml(facility.facility_type_display || type)}
            </div>
            <h6 style="margin: 0 0 6px 0; font-weight: 700; color: #0f2b48;">${escapeHtml(facility.name)}</h6>
            <p style="margin: 0 0 6px 0; font-size: 13px; color: #475569;">${escapeHtml(facility.location_description)}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #e2e8f0; padding-top: 6px;">
              <span style="font-size: 11px; color: ${facility.is_operational === false ? '#dc2626' : '#10b981'}; font-weight: 600;"><i class="fas ${facility.is_operational === false ? 'fa-times-circle' : 'fa-check-circle'} me-1"></i>${facility.is_operational === false ? 'Maintenance' : 'Operational'}</span>
              ${facility.contact_number ? `<a href="tel:${escapeHtml(facility.contact_number)}" class="btn btn-sm btn-outline-primary" style="font-size: 11px; padding: 2px 8px;">Call ${escapeHtml(facility.contact_number)}</a>` : ''}
            </div>
          </div>
        `;
        marker.bindPopup(popupContent);
=======
      className: '',
      html: `<div style="
        width:38px;height:38px;background:${bgGradient};
        border-radius:50%;display:flex;align-items:center;
        justify-content:center;color:#fff;font-size:15px;
        box-shadow:0 4px 12px rgba(0,0,0,0.35);border:2px solid #fff;
      "><i class="${iconClass}"></i></div>`,
      iconSize: [38, 38],
      iconAnchor: [19, 19],
      popupAnchor: [0, -22]
    });
  }

  const iconConfig = {
    'WASHROOM':        { icon: 'fas fa-restroom',     bg: 'linear-gradient(135deg,#0284c7,#0369a1)' },
    'DRINKING_WATER':  { icon: 'fas fa-tint',          bg: 'linear-gradient(135deg,#06b6d4,#0891b2)' },
    'LIFT':            { icon: 'fas fa-elevator',      bg: 'linear-gradient(135deg,#8b5cf6,#6d28d9)' },
    'ESCALATOR':       { icon: 'fas fa-walking',       bg: 'linear-gradient(135deg,#6366f1,#4f46e5)' },
    'FOOD':            { icon: 'fas fa-utensils',      bg: 'linear-gradient(135deg,#f59e0b,#d97706)' },
    'WAITING_ROOM':    { icon: 'fas fa-couch',         bg: 'linear-gradient(135deg,#10b981,#059669)' },
    'PARKING':         { icon: 'fas fa-car',           bg: 'linear-gradient(135deg,#64748b,#475569)' },
    'MEDICAL':         { icon: 'fas fa-hospital',      bg: 'linear-gradient(135deg,#ef4444,#dc2626)' },
    'HELP_DESK':       { icon: 'fas fa-info-circle',   bg: 'linear-gradient(135deg,#0f2b48,#1e40af)' },
    'CLOAK_ROOM':      { icon: 'fas fa-luggage-cart',  bg: 'linear-gradient(135deg,#d946ef,#a21caf)' },
    'WHEELCHAIR_POINT':{ icon: 'fas fa-wheelchair',    bg: 'linear-gradient(135deg,#2563eb,#1d4ed8)' },
  };

  // Station central marker
  const mainIcon = L.divIcon({
    className: '',
    html: `<div style="
      width:48px;height:48px;
      background:linear-gradient(135deg,#0f2b48,#2563eb);
      border-radius:12px;display:flex;align-items:center;
      justify-content:center;color:#fff;font-size:22px;
      box-shadow:0 6px 18px rgba(15,43,72,0.45);border:3px solid #fff;
    "><i class="fas fa-train"></i></div>`,
    iconSize: [48, 48],
    iconAnchor: [24, 24],
    popupAnchor: [0, -28]
  });

  L.marker([stationLat, stationLng], { icon: mainIcon })
    .addTo(map)
    .bindPopup(`<div style="padding:6px;min-width:180px;">
      <h6 style="margin:0 0 4px;color:#0f2b48;font-weight:700;">🚆 ${stationName}</h6>
      <p style="margin:0;font-size:12px;color:#64748b;">Central Concourse & Porch</p>
    </div>`);

  // Platform markers
  if (Array.isArray(platformsData)) {
    platformsData.forEach(function(p) {
      const lat = parseFloat(p.latitude);
      const lng = parseFloat(p.longitude);
      if (!isNaN(lat) && !isNaN(lng)) {
        const platIcon = L.divIcon({
          className: '',
          html: `<div style="
            width:34px;height:34px;
            background:linear-gradient(135deg,#0ea5e9,#0284c7);
            border-radius:8px;display:flex;align-items:center;
            justify-content:center;color:#fff;font-weight:800;font-size:13px;
            box-shadow:0 3px 10px rgba(0,0,0,0.25);border:2px solid #fff;
          ">P${p.number}</div>`,
          iconSize: [34, 34],
          iconAnchor: [17, 17],
          popupAnchor: [0, -20]
        });
        L.marker([lat, lng], { icon: platIcon })
          .addTo(map)
          .bindPopup(`<div style="padding:6px;min-width:160px;">
            <h6 style="margin:0 0 4px;color:#0f2b48;font-weight:700;">Platform ${p.number}</h6>
            <p style="margin:0;font-size:12px;color:#64748b;">${p.description || ''}</p>
          </div>`);
      }
    });
  }

  // Facility markers
  const markersGroup = L.layerGroup().addTo(map);
  const allMarkers = [];

  if (Array.isArray(facilitiesData)) {
    facilitiesData.forEach(function(facility) {
      const type = facility.facility_type;
      const conf = iconConfig[type] || { icon: 'fas fa-map-marker-alt', bg: 'linear-gradient(135deg,#2563eb,#1d4ed8)' };
      const lat = parseFloat(facility.latitude);
      const lng = parseFloat(facility.longitude);

      if (!isNaN(lat) && !isNaN(lng)) {
        const marker = L.marker([lat, lng], { icon: createCustomIcon(conf.icon, conf.bg) });
        marker.bindPopup(`
          <div style="padding:8px;min-width:200px;">
            <div style="font-size:11px;font-weight:700;color:#2563eb;text-transform:uppercase;margin-bottom:2px;">
              ${facility.facility_type_display || type}
            </div>
            <h6 style="margin:0 0 6px;font-weight:700;color:#0f2b48;">${facility.name}</h6>
            <p style="margin:0 0 6px;font-size:13px;color:#475569;">${facility.location_description || ''}</p>
            <div style="display:flex;justify-content:space-between;align-items:center;border-top:1px solid #e2e8f0;padding-top:6px;">
              <span style="font-size:11px;color:#10b981;font-weight:600;"><i class="fas fa-check-circle"></i> Operational</span>
              ${facility.contact_number ? `<a href="tel:${facility.contact_number}" style="font-size:11px;color:#2563eb;font-weight:600;">📞 ${facility.contact_number}</a>` : ''}
            </div>
          </div>
        `);
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
        marker.facilityType = type;
        markersGroup.addLayer(marker);
        allMarkers.push(marker);
      }
    });
<<<<<<< HEAD
    applyFilters();
  }

  function applyFilters() {
    const checkedTypes = Array.from(document.querySelectorAll('.facility-filter-checkbox:checked')).map(c => c.value);
    const showAll = checkedTypes.includes('ALL');
    allMarkers.forEach(function(marker) {
      if (showAll || checkedTypes.includes(marker.facilityType)) markersGroup.addLayer(marker);
      else markersGroup.removeLayer(marker);
    });
  }

  renderLayers(facilitiesData, platformsData);

  // Filter Event Listeners
  const filterCheckboxes = document.querySelectorAll('.facility-filter-checkbox');
  filterCheckboxes.forEach(function(cb) {
    cb.addEventListener('change', function() {
      if (cb.value === 'ALL' && cb.checked) {
        document.querySelectorAll('.facility-filter-checkbox').forEach(c => c.checked = true);
      } else if (cb.value !== 'ALL' && !cb.checked) {
        const allCheckbox = document.querySelector('.facility-filter-checkbox[value="ALL"]');
        if (allCheckbox) allCheckbox.checked = false;
=======
  }

  // Filter logic — fixed: ALL checkbox controls all, individual checkboxes work independently
  const filterCheckboxes = document.querySelectorAll('.facility-filter-checkbox');
  const allCheckbox = document.querySelector('.facility-filter-checkbox[value="ALL"]');

  function applyFilters() {
    const checkedTypes = Array.from(
      document.querySelectorAll('.facility-filter-checkbox:not([value="ALL"]):checked')
    ).map(c => c.value);

    const showAll = allCheckbox && allCheckbox.checked;
    markersGroup.clearLayers();
    allMarkers.forEach(function(marker) {
      if (showAll || checkedTypes.includes(marker.facilityType)) {
        markersGroup.addLayer(marker);
      }
    });
  }

  filterCheckboxes.forEach(function(cb) {
    cb.addEventListener('change', function() {
      if (cb.value === 'ALL') {
        // Sync all individual checkboxes to match ALL state
        document.querySelectorAll('.facility-filter-checkbox:not([value="ALL"])').forEach(function(c) {
          c.checked = cb.checked;
        });
      } else {
        // If any individual unchecked, uncheck ALL
        const allIndividual = document.querySelectorAll('.facility-filter-checkbox:not([value="ALL"])');
        const allChecked = Array.from(allIndividual).every(c => c.checked);
        if (allCheckbox) allCheckbox.checked = allChecked;
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
      }
      applyFilters();
    });
  });

<<<<<<< HEAD
  const locateButton = document.getElementById(options.locateButtonId || 'locate-me');
  if (locateButton && navigator.geolocation) {
    locateButton.addEventListener('click', function() {
      setStatus('Finding your location...', 'primary');
      navigator.geolocation.getCurrentPosition(function(position) {
        const latLng = [position.coords.latitude, position.coords.longitude];
        if (userMarker) map.removeLayer(userMarker);
        if (userAccuracy) map.removeLayer(userAccuracy);
        userMarker = L.circleMarker(latLng, {radius: 8, color: '#fff', weight: 3, fillColor: '#2563eb', fillOpacity: 1}).addTo(map).bindPopup('Your current location').openPopup();
        userAccuracy = L.circle(latLng, {radius: position.coords.accuracy, color: '#2563eb', fillColor: '#2563eb', fillOpacity: 0.1, weight: 1}).addTo(map);
        map.setView(latLng, 18);
        setStatus('Your location is shown on the map.', 'success');
      }, function() {
        setStatus('Location permission was unavailable.', 'danger');
      }, {enableHighAccuracy: true, timeout: 10000, maximumAge: 30000});
    });
  }

  const refresh = function() {
    if (!options.dataUrl) return;
    fetch(options.dataUrl, {headers: {'Accept': 'application/json'}})
      .then(function(response) { if (!response.ok) throw new Error('Map data unavailable'); return response.json(); })
      .then(function(data) {
        renderLayers(data.facilities || [], data.platforms || []);
        setStatus(`Live data updated at ${new Date().toLocaleTimeString()}.`, 'success');
      })
      .catch(function() { setStatus('Showing last available map data.', 'warning'); });
  };
  refresh();
  if (options.dataUrl) window.setInterval(refresh, 30000);

  window.setTimeout(function() { map.invalidateSize(); }, 100);

=======
>>>>>>> dd5170b (Initial RailSaathi deployment-ready commit)
  return map;
}
