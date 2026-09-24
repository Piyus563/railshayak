function initStationMap(mapElementId, stationLat, stationLng, stationName, facilitiesData, platformsData, options) {
  const element = document.getElementById(mapElementId);
  if (!element) return null;
  if (element._railsaathiMap) return element._railsaathiMap;
  options = options || {};
  const status = document.getElementById(options.statusElementId || 'map-status');
  const setStatus = (message, type) => {
    if (!status) return;
    status.textContent = message;
    status.className = `small text-${type || 'muted'}`;
  };
  const coordinates = (latitude, longitude) => {
    const lat = Number(latitude); const lng = Number(longitude);
    return Number.isFinite(lat) && lat >= -90 && lat <= 90 && Number.isFinite(lng) && lng >= -180 && lng <= 180 ? [lat, lng] : null;
  };
  const escapeHtml = value => String(value == null ? '' : value).replace(/[&<>'"]/g, character => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[character]));
  if (typeof L === 'undefined') { setStatus('Map library unavailable.', 'danger'); return null; }
  const stationPosition = coordinates(stationLat, stationLng);
  if (!stationPosition) { element.innerHTML = '<div class="alert alert-warning m-3">Station coordinates are unavailable.</div>'; setStatus('Station coordinates unavailable.', 'danger'); return null; }

  const map = L.map(mapElementId, { center: stationPosition, zoom: 16, scrollWheelZoom: false });
  element._railsaathiMap = map;
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors | RailSaathi', maxZoom: 20 }).addTo(map);
  const markerGroup = L.layerGroup().addTo(map);
  const stationGroup = L.layerGroup().addTo(map);
  const markers = [];
  let userPosition = null;
  let userMarker = null;
  let accuracyCircle = null;
  let routeLine = null;
  const icons = {
    WASHROOM: ['fas fa-restroom', '#0284c7'], DRINKING_WATER: ['fas fa-tint', '#0891b2'], LIFT: ['fas fa-elevator', '#6d28d9'], ESCALATOR: ['fas fa-walking', '#4f46e5'], FOOD: ['fas fa-utensils', '#d97706'], WAITING_ROOM: ['fas fa-couch', '#059669'], PARKING: ['fas fa-car', '#475569'], MEDICAL: ['fas fa-hospital', '#dc2626'], HELP_DESK: ['fas fa-info-circle', '#1d4ed8'], CLOAK_ROOM: ['fas fa-luggage-cart', '#a21caf'], WHEELCHAIR_POINT: ['fas fa-wheelchair', '#1d4ed8'], COOLIE_PICKUP: ['fas fa-luggage-cart', '#b45309'], PLATFORM: ['fas fa-subway', '#f59e0b']
  };
  const iconFor = type => {
    const config = icons[type] || ['fas fa-location-dot', '#2563eb'];
    return L.divIcon({ className: 'custom-leaflet-marker', html: `<div style="width:34px;height:34px;background:${config[1]};border:2px solid #fff;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;box-shadow:0 3px 10px rgba(0,0,0,.25)"><i class="${config[0]}"></i></div>`, iconSize: [34, 34], iconAnchor: [17, 17], popupAnchor: [0, -18] });
  };
  const distanceKm = (a, b) => {
    const radians = value => value * Math.PI / 180; const lat = radians(b[0] - a[0]); const lng = radians(b[1] - a[1]);
    const part = Math.sin(lat / 2) ** 2 + Math.cos(radians(a[0])) * Math.cos(radians(b[0])) * Math.sin(lng / 2) ** 2;
    return 6371 * 2 * Math.atan2(Math.sqrt(part), Math.sqrt(1 - part));
  };
  const distanceText = km => km < 1 ? `${Math.round(km * 1000)} m` : `${km.toFixed(2)} km`;
  const navigate = marker => {
    if (!userPosition) { setStatus('Enable location before navigating to a marker.', 'warning'); return; }
    if (routeLine) map.removeLayer(routeLine);
    routeLine = L.polyline([userPosition, marker.getLatLng()], { color: '#2563eb', weight: 4, dashArray: '8 8' }).addTo(map);
    map.fitBounds(routeLine.getBounds(), { padding: [40, 40] });
    setStatus(`Straight-line distance: ${distanceText(distanceKm(userPosition, marker.getLatLng()))}. Road routing is not enabled.`, 'primary');
  };
  const navigateButton = id => `<button type="button" class="btn btn-sm btn-outline-primary map-navigate" data-marker-id="${id}">Navigate Here</button>`;
  const stationMarker = L.marker(stationPosition, { icon: iconFor('STATION') }).addTo(stationGroup);
  stationMarker.bindPopup(`<strong>🚉 ${escapeHtml(stationName)}</strong><br><span class="small">Station location</span>`);

  const applyFilters = () => {
    const checked = new Set(Array.from(document.querySelectorAll('.facility-filter-checkbox:checked')).map(input => input.value));
    markers.forEach(item => { if (checked.has('ALL') || checked.has(item.type)) markerGroup.addLayer(item.marker); else markerGroup.removeLayer(item.marker); });
  };
  const renderLayers = (facilities, platforms) => {
    markerGroup.clearLayers(); markers.length = 0;
    (Array.isArray(platforms) ? platforms : []).forEach(platform => {
      const position = coordinates(platform.latitude, platform.longitude); if (!position) return;
      const marker = L.marker(position, { icon: iconFor('PLATFORM') }); const id = `platform-${platform.id || platform.number}`;
      marker.bindPopup(`<strong>🚉 Platform ${escapeHtml(platform.number)}</strong><br>${escapeHtml(platform.description || 'Platform information')}<br><span class="small">Verified location</span><br>${navigateButton(id)}`);
      markers.push({ marker, type: 'PLATFORM', name: `Platform ${platform.number}`, search: `platform ${platform.number} ${platform.description || ''}`, id });
    });
    (Array.isArray(facilities) ? facilities : []).forEach(facility => {
      const position = coordinates(facility.latitude, facility.longitude); if (!position) return;
      const type = facility.facility_type || 'FACILITY'; const id = `facility-${facility.id}`; const state = facility.is_operational === false ? 'Maintenance' : 'Open';
      const distance = userPosition ? `<br><span class="small">Distance: ${distanceText(distanceKm(userPosition, position))}</span>` : '';
      const booking = type === 'COOLIE_PICKUP' ? `<br><a class="btn btn-sm btn-outline-warning mt-2" href="/bookings/book/?station=${encodeURIComponent(options.stationCode || stationName)}">Book Coolie</a>` : '';
      const marker = L.marker(position, { icon: iconFor(type) });
      marker.bindPopup(`<strong>${escapeHtml(facility.facility_type_display || type)}</strong><h6>${escapeHtml(facility.name)}</h6><div class="small">${escapeHtml(facility.location_description || '')}</div><div class="small text-${facility.is_operational === false ? 'danger' : 'success'}">Status: ${state}</div>${distance}<br>${navigateButton(id)}${booking}`);
      markers.push({ marker, type, name: facility.name, search: `${facility.name} ${facility.facility_type_display || type} ${facility.location_description || ''}`, id });
    });
    applyFilters();
    const bounds = L.latLngBounds([stationPosition].concat(markers.map(item => item.marker.getLatLng())));
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 18 });
    setStatus(markers.length ? `Map ready. ${markers.length} verified locations loaded.` : 'Map ready. No platform or facility coordinates are available.', markers.length ? 'success' : 'warning');
  };
  renderLayers(facilitiesData, platformsData);
  document.querySelectorAll('.facility-filter-checkbox').forEach(input => input.addEventListener('change', () => {
    if (input.value === 'ALL' && input.checked) document.querySelectorAll('.facility-filter-checkbox').forEach(item => { item.checked = true; });
    if (input.value !== 'ALL' && !input.checked) { const all = document.querySelector('.facility-filter-checkbox[value="ALL"]'); if (all) all.checked = false; }
    applyFilters();
  }));
  element.addEventListener('click', event => { const button = event.target.closest('.map-navigate'); const item = button && markers.find(entry => entry.id === button.dataset.markerId); if (item) navigate(item.marker); });

  const search = document.getElementById('map-search'); const results = document.getElementById('map-search-results');
  if (search && results) search.addEventListener('input', () => {
    results.replaceChildren(); const query = search.value.trim().toLowerCase(); if (!query) { results.hidden = true; return; }
    markers.filter(item => item.search.toLowerCase().includes(query)).slice(0, 8).forEach(item => { const result = document.createElement('button'); result.type = 'button'; result.className = 'list-group-item list-group-item-action small'; result.textContent = item.name; result.onclick = () => { map.setView(item.marker.getLatLng(), 19); item.marker.openPopup(); results.hidden = true; }; results.appendChild(result); });
    results.hidden = !results.children.length;
  });

  const locate = document.getElementById(options.locateButtonId || 'locate-me');
  if (locate) locate.addEventListener('click', () => {
    if (!window.isSecureContext && !['localhost', '127.0.0.1'].includes(window.location.hostname)) { setStatus('Location detection requires an HTTPS connection.', 'danger'); return; }
    if (!navigator.geolocation) { setStatus('Location detection is not supported by this browser.', 'danger'); return; }
    locate.disabled = true; setStatus('Detecting your location...', 'primary');
    navigator.geolocation.getCurrentPosition(position => {
      const point = coordinates(position.coords.latitude, position.coords.longitude); const accuracy = Number(position.coords.accuracy);
      if (!point || !Number.isFinite(accuracy) || accuracy <= 0) { setStatus('GPS returned invalid coordinates.', 'danger'); locate.disabled = false; return; }
      userPosition = point; if (userMarker) map.removeLayer(userMarker); if (accuracyCircle) map.removeLayer(accuracyCircle);
      accuracyCircle = L.circle(point, { radius: accuracy, color: '#2563eb', fillColor: '#2563eb', fillOpacity: .1 }).addTo(map);
      userMarker = L.circleMarker(point, { radius: 8, color: '#fff', weight: 3, fillColor: '#2563eb', fillOpacity: 1 }).addTo(map).bindPopup(`📍 Your Location<br>Accuracy: ${Math.round(accuracy)} m`);
      renderLayers(facilitiesData, platformsData); setStatus(`Location detected. Distance to station: ${distanceText(distanceKm(point, stationPosition))}.`, 'success'); locate.disabled = false;
    }, error => { setStatus({ 1: 'GPS permission denied.', 2: 'GPS unavailable.', 3: 'GPS detection timed out.' }[error.code] || 'Unable to detect GPS location.', 'danger'); locate.disabled = false; }, { enableHighAccuracy: true, timeout: 15000, maximumAge: 60000 });
  });
  const nearest = document.getElementById('find-nearest');
  if (nearest) nearest.addEventListener('click', () => {
    if (!userPosition) { setStatus('Enable location before finding the nearest facility.', 'warning'); return; }
    const type = document.getElementById('nearest-type')?.value; const matches = markers.filter(item => item.type === type);
    if (!matches.length) { setStatus('No verified location is available for that facility type.', 'warning'); return; }
    const item = matches.sort((a, b) => distanceKm(userPosition, a.marker.getLatLng()) - distanceKm(userPosition, b.marker.getLatLng()))[0]; map.setView(item.marker.getLatLng(), 19); item.marker.openPopup(); setStatus(`Nearest ${item.name}: ${distanceText(distanceKm(userPosition, item.marker.getLatLng()))}.`, 'success');
  });
  const refresh = () => {
    if (!options.dataUrl) return;
    fetch(options.dataUrl, { headers: { Accept: 'application/json' } }).then(response => { if (!response.ok) throw new Error(`Map API returned HTTP ${response.status}`); return response.json(); }).then(data => { if (!data || !Array.isArray(data.facilities) || !Array.isArray(data.platforms)) throw new Error('Map API returned malformed data'); facilitiesData = data.facilities; platformsData = data.platforms; renderLayers(facilitiesData, platformsData); setStatus(`Live data connected. Last updated: ${new Date().toLocaleTimeString()}.`, 'success'); }).catch(error => { console.error('RailSaathi map refresh failed:', error); setStatus(`Unable to load live map data: ${error.message}`, 'danger'); });
  };
  refresh(); if (options.dataUrl) window.setInterval(refresh, 30000); window.setTimeout(() => map.invalidateSize(), 100);
  return map;
}