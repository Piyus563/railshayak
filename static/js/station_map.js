/**
 * RailSaathi Interactive Leaflet.js Station Map
 */

function initStationMap(mapElementId, stationLat, stationLng, stationName, facilitiesData, platformsData) {
  const mapElem = document.getElementById(mapElementId);
  if (!mapElem) return;

  // Initialize map centered at station coordinates
  const map = L.map(mapElementId, {
    center: [stationLat, stationLng],
    zoom: 18,
    zoomControl: true,
    scrollWheelZoom: false
  });

  // Add OpenStreetMap tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | RailSaathi Smart Station Map',
    maxZoom: 20
  }).addTo(map);

  // Custom Icon Factory
  function createCustomIcon(iconClass, bgGradient) {
    return L.divIcon({
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
  const allMarkers = [];

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

  const mainMarker = L.marker([stationLat, stationLng], { icon: mainStationIcon }).addTo(map);
  mainMarker.bindPopup(`
    <div style="padding: 6px; min-width: 180px;">
      <h6 style="margin: 0 0 4px 0; color: #0f2b48; font-weight: 700;">🚆 ${stationName}</h6>
      <p style="margin: 0; font-size: 12px; color: #64748b;">Central Concourse & Porch</p>
    </div>
  `);

  // Render Facilities Markers
  if (Array.isArray(facilitiesData)) {
    facilitiesData.forEach(function(facility) {
      const type = facility.facility_type;
      const conf = iconConfig[type] || { icon: 'fas fa-map-marker-alt', bg: 'linear-gradient(135deg, #2563eb, #1d4ed8)' };
      const icon = createCustomIcon(conf.icon, conf.bg);

      const lat = parseFloat(facility.latitude);
      const lng = parseFloat(facility.longitude);

      if (!isNaN(lat) && !isNaN(lng)) {
        const marker = L.marker([lat, lng], { icon: icon });
        const popupContent = `
          <div style="padding: 8px; min-width: 200px;">
            <div style="font-size: 11px; font-weight: 700; color: #2563eb; text-transform: uppercase; margin-bottom: 2px;">
              ${facility.facility_type_display || type}
            </div>
            <h6 style="margin: 0 0 6px 0; font-weight: 700; color: #0f2b48;">${facility.name}</h6>
            <p style="margin: 0 0 6px 0; font-size: 13px; color: #475569;">${facility.location_description || ''}</p>
            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #e2e8f0; padding-top: 6px;">
              <span style="font-size: 11px; color: #10b981; font-weight: 600;"><i class="fas fa-check-circle me-1"></i>Operational</span>
              ${facility.contact_number ? `<a href="tel:${facility.contact_number}" class="btn btn-sm btn-outline-primary" style="font-size: 11px; padding: 2px 8px;">Call ${facility.contact_number}</a>` : ''}
            </div>
          </div>
        `;
        marker.bindPopup(popupContent);
        marker.facilityType = type;
        markersGroup.addLayer(marker);
        allMarkers.push(marker);
      }
    });
  }

  // Filter Event Listeners
  const filterCheckboxes = document.querySelectorAll('.facility-filter-checkbox');
  filterCheckboxes.forEach(function(cb) {
    cb.addEventListener('change', function() {
      const checkedTypes = Array.from(document.querySelectorAll('.facility-filter-checkbox:checked')).map(c => c.value);
      markersGroup.clearLayers();
      allMarkers.forEach(function(marker) {
        if (checkedTypes.length === 0 || checkedTypes.includes(marker.facilityType) || checkedTypes.includes('ALL')) {
          markersGroup.addLayer(marker);
        }
      });
    });
  });

  return map;
}
