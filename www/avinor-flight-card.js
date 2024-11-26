class AvinorFlightCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._hass = null;
    this.updateTimeout = null; // For debouncing updates
    this.loading = false; // For tracking loading state
    this.lastUpdated = null; // For tracking when data was last updated
  }

  setConfig(config) {
    // Set default configuration
    this.config = {
      title: config.title || 'Avinor Flydata',
      entity: config.entity || null,
    };

    if (!this.config.entity) {
      throw new Error('Vennligst spesifiser en entity.');
    }

    this.render();
  }

  set hass(hass) {
    this._hass = hass;
    if (this.shadowRoot) {
      const entity = this._hass.states[this.config.entity];
      if (!entity) {
        return;
      }
      // Check if data has been updated
      if (entity.last_updated !== this.lastUpdated) {
        this.lastUpdated = entity.last_updated;
        this.loading = false; // Data has been updated
        this.updateData();
      }
    }
  }

  render() {
    const card = document.createElement('ha-card');
    card.header = this.config.title;

    const style = document.createElement('style');
    style.textContent = `
      /* Set the card's background color to the default ha-card theme background color */
      ha-card {
        background-color: var(--ha-card-background, var(--card-background-color, white));
      }
      .controls {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        margin: 10px;
      }
      .control-item {
        margin: 5px;
        position: relative;
      }
      .control-item label {
        font-weight: bold;
        margin-bottom: 5px;
        display: block;
      }
      .control-item select, .control-item input[type="text"] {
        width: 150px;
        padding: 8px 12px;
        border: 1px solid var(--primary-text-color);
        border-radius: 20px;
        background-color: transparent;
        color: var(--primary-text-color); /* Use theme's font color */
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
        font-size: 14px;
        outline: none;
        transition: border-color 0.3s;
      }
      .control-item select:hover, .control-item input[type="text"]:hover {
        border-color: var(--primary-color);
      }
      .control-item select:focus, .control-item input[type="text"]:focus {
        border-color: var(--primary-color);
      }
      /* Arrow for dropdown menus */
      .control-item select {
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" fill="%23ffffff" viewBox="0 0 24 24"><path d="M7 10l5 5 5-5z"/></svg>');
        background-repeat: no-repeat;
        background-position: right 10px center;
        background-size: 16px;
      }
      /* Hide default arrow */
      .control-item select::-ms-expand {
        display: none;
      }
      .flight-table {
        width: 100%;
        border-collapse: collapse;
      }
      .flight-table th, .flight-table td {
        border: 1px dotted rgba(0, 0, 0, 0.5);
        padding: 8px;
      }
      .flight-table th {
        background-color: var(--ha-card-header-background, #000); /* Use theme variable or default to #000 */
        color: var(--ha-card-header-color, #fff); /* Use theme variable or default to #fff */
        font-weight: bold;
        text-align: left;
        position: sticky;
        top: 0;
        z-index: 1;
      }
      .flight-table tbody tr {
        cursor: default;
      }
      .flight-table td {
        vertical-align: top;
      }
      .loader {
        border: 8px solid #f3f3f3;
        border-top: 8px solid #3498db;
        border-radius: 50%;
        width: 60px;
        height: 60px;
        animation: spin 1s linear infinite;
        margin: auto;
      }
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      .loader-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
      }
      .table-container {
        max-height: 400px;
        overflow-y: auto;
      }
      .table-container::-webkit-scrollbar {
        display: none;
      }
      .table-container {
        -ms-overflow-style: none;
        scrollbar-width: none;
      }
    `;

    const content = document.createElement('div');
    content.innerHTML = `
      <div class="controls">
        <div class="control-item">
          <label>Flyplass:</label>
          <select id="airport">
            <!-- First three airports -->
            <option value="TOS" selected>Tromsø (TOS)</option>
            <option value="OSL">Oslo (OSL)</option>
            <option value="BGO">Bergen (BGO)</option>
            <!-- Additional airports in alphabetical order -->
            <option value="AES">Ålesund (AES)</option>
            <option value="ALF">Alta (ALF)</option>
            <option value="ANX">Andenes (ANX)</option>
            <option value="BDU">Bardufoss (BDU)</option>
            <option value="BOO">Bodø (BOO)</option>
            <option value="BNN">Brønnøysund (BNN)</option>
            <option value="EVE">Harstad/Narvik (EVE)</option>
            <option value="FDE">Førde (FDE)</option>
            <option value="FRO">Florø (FRO)</option>
            <option value="HAU">Haugesund (HAU)</option>
            <option value="HFT">Hammerfest (HFT)</option>
            <option value="HOV">Ørsta/Volda (HOV)</option>
            <option value="HVG">Honningsvåg (HVG)</option>
            <option value="KKN">Kirkenes (KKN)</option>
            <option value="KRS">Kristiansand (KRS)</option>
            <option value="KSU">Kristiansund (KSU)</option>
            <option value="LKL">Lakselv (LKL)</option>
            <option value="LYR">Longyearbyen (LYR)</option>
            <option value="MEH">Mehamn (MEH)</option>
            <option value="MJF">Mosjøen (MJF)</option>
            <option value="MOL">Molde (MOL)</option>
            <option value="OSY">Namsos (OSY)</option>
            <option value="RET">Røst (RET)</option>
            <option value="RRS">Røros (RRS)</option>
            <option value="RVK">Rørvik (RVK)</option>
            <option value="SDN">Sandane (SDN)</option>
            <option value="SKN">Stokmarknes (SKN)</option>
            <option value="SOJ">Sørkjosen (SOJ)</option>
            <option value="SOG">Sogndal (SOG)</option>
            <option value="SSJ">Sandnessjøen (SSJ)</option>
            <option value="SVG">Stavanger (SVG)</option>
            <option value="SVJ">Svolvær (SVJ)</option>
            <option value="TRD">Trondheim (TRD)</option>
            <option value="TRF">Sandefjord Torp (TRF)</option>
            <option value="VDS">Vadsø (VDS)</option>
            <option value="VRY">Værøy (VRY)</option>
          </select>
        </div>
        <div class="control-item">
          <label>Retning:</label>
          <select id="direction">
            <option value="A">Ankomst</option>
            <option value="D">Avgang</option>
          </select>
        </div>
        <div class="control-item">
          <label>Tid fra (timer):</label>
          <select id="timeFrom">
            <option value="-3">-3</option>
            <option value="-2">-2</option>
            <option value="-1">-1</option>
            <option value="0" selected>0</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7">7</option>
          </select>
        </div>
        <div class="control-item">
          <label>Tid til (timer):</label>
          <select id="timeTo">
            <option value="0">0</option>
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4</option>
            <option value="5">5</option>
            <option value="6">6</option>
            <option value="7" selected>7</option>
            <option value="8">8</option>
            <option value="9">9</option>
            <option value="10">10</option>
            <option value="11">11</option>
            <option value="12">12</option>
          </select>
        </div>
        <div class="control-item">
          <label>Søk:</label>
          <input type="text" id="searchText" placeholder="Skriv inn søketekst">
        </div>
      </div>
      <div id="loaderContainer" class="loader-container" style="display: none;">
        <div class="loader"></div>
      </div>
      <div class="table-container">
        <table class="flight-table" id="flightTable">
          <thead id="tableHeader">
            <!-- Table headers will be inserted here -->
          </thead>
          <tbody id="flightData">
            <!-- Flight data will be inserted here -->
          </tbody>
        </table>
      </div>
    `;

    card.appendChild(style);
    card.appendChild(content);
    this.shadowRoot.appendChild(card);

    // Set default airport to Tromsø (TOS)
    this.shadowRoot.getElementById('airport').value = 'TOS';

    // Add event listeners to input fields to trigger updates
    const inputs = ['airport', 'direction', 'timeFrom', 'timeTo', 'searchText'];
    inputs.forEach((id) => {
      const element = this.shadowRoot.getElementById(id);
      element.addEventListener('change', () => this.scheduleUpdate());
      element.addEventListener('input', () => this.scheduleUpdate());
    });
  }

  scheduleUpdate() {
    // Debounce updates to avoid rapid consecutive calls
    if (this.updateTimeout) {
      clearTimeout(this.updateTimeout);
    }
    this.updateTimeout = setTimeout(() => {
      this.updateParameters();
    }, 500); // Adjust the delay as needed
  }

  updateParameters() {
    const airport = this.shadowRoot.getElementById('airport').value;
    const direction = this.shadowRoot.getElementById('direction').value;
    const timeFrom = this.shadowRoot.getElementById('timeFrom').value;
    const timeTo = this.shadowRoot.getElementById('timeTo').value;
    const searchText = this.shadowRoot.getElementById('searchText').value;

    // Set loading state
    this.loading = true;
    this.updateData(); // Update the display to show the loader

    // Update the sensor's parameters using a service call
    this._hass.callService('avinor_flight_data', 'update_parameters', {
      entity_id: this.config.entity,
      airport: airport,
      direction: direction,
      time_from: timeFrom,
      time_to: timeTo,
      search_text: searchText,
    });
  }

  updateData() {
    const loaderContainer = this.shadowRoot.getElementById('loaderContainer');
    const flightTable = this.shadowRoot.getElementById('flightTable');

    if (this.loading) {
      // Show loader, hide table
      loaderContainer.style.display = 'flex';
      flightTable.parentElement.style.display = 'none';
      return;
    } else {
      // Hide loader, show table
      loaderContainer.style.display = 'none';
      flightTable.parentElement.style.display = 'block';
    }

    const entity = this._hass.states[this.config.entity];
    if (!entity) {
      return;
    }

    const flights = entity.attributes.flights || [];
    let flightRows = '';

    if (flights.length > 0) {
      // Define the headers based on the data structure
      const headers = ['flight_id', 'airline', 'airport', 'schedule_time', 'status', 'dom_int']; // New order
      const headerNames = {
        'flight_id': 'Fly',
        'airline': 'Selskap',
        'schedule_time': 'Rutetid',
        'status': 'Status',
        'airport': 'Fra/Til',
        'dom_int': 'Dom/Int',
      };
      const headerRow = headers.map((header) => `<th>${headerNames[header] || this.capitalize(header)}</th>`).join('');
      this.shadowRoot.getElementById('tableHeader').innerHTML = `<tr>${headerRow}</tr>`;

      // Airline code to name mapping (unchanged from previous versions)
      const airlineNames = {
        'A3': 'Aegean',
        'BT': 'Air Baltic',
        'AF': 'Air France',
        'JU': 'Air Serbia',
        'OS': 'Austrian Airlines',
        '0B': 'Blue Air',
        'BA': 'British Airways',
        'AB': 'Braathens Regional Airlines',
        'SN': 'Brussels Airlines',
        'OU': 'Croatia Airlines',
        'DX': 'Danish Air Transport (DAT)',
        'EK': 'Emirates',
        'E4': 'Enter Air',
        'ET': 'Ethiopian Airlines',
        'EW': 'Eurowings',
        'AY': 'Finnair',
        'IB': 'Iberia',
        'FI': 'Icelandair',
        'KL': 'KLM',
        'LM': 'Loganair',
        'LO': 'LOT',
        'LH': 'Lufthansa',
        'LG': 'Luxair',
        'N0': 'Norse Atlantic Airways',
        'D8': 'Norwegian',
        'DY': 'Norwegian',
        'PC': 'Pegasus Airlines',
        'QR': 'Qatar Airways',
        'FR': 'Ryanair',
        'RK': 'Ryanair',
        'SK': 'SAS',
        'XQ': 'SunExpress',
        'LX': 'Swiss International Air Lines',
        'TP': 'TAP Portugal',
        'TG': 'Thai Airways International',
        'TK': 'Turkish Airlines',
        'VY': 'Vueling',
        'V7': 'Volotea',
        'WF': 'Widerøe',
        'W6': 'Wizz Air',
        'W9': 'Wizz Air',
        'U2': 'Easyjet',
        'EZ': 'Sun-air',
      };

      // Status code mapping
      const statusCodes = {
        'A': 'Ankommet',
        'C': 'Kansellert',
        'D': 'Avreist',
        'E': 'Ny tid',
        'N': 'Ny info',
        // Add more mappings if needed
      };

      // Generate table rows
      flights.forEach((flight) => {
        const row = headers.map((header) => {
          let value = flight[header];
          if (header === 'airline') {
            // Replace airline code with full name
            value = airlineNames[value] || value; // Use the code if no mapping exists
          }
          if (header === 'status' && typeof value === 'object') {
            // Format the status object
            let statusText = statusCodes[value.code] || value.code || '';
            let statusTime = this.formatTime(value.time) || '';
            if (statusText && statusTime) {
              value = `${statusText}<br>kl: ${statusTime}`;
            } else if (statusText) {
              value = statusText;
            } else if (statusTime) {
              value = `kl: ${statusTime}`;
            } else {
              value = '';
            }
          }
          if (header === 'schedule_time') {
            value = this.formatTime(value);
          }
          return `<td>${this.formatValue(value)}</td>`;
        }).join('');
        flightRows += `<tr>${row}</tr>`;
      });
    } else {
      flightRows = `
        <tr>
          <td colspan="100%">Ingen flydata tilgjengelig for de valgte parameterne.</td>
        </tr>
      `;
      this.shadowRoot.getElementById('tableHeader').innerHTML = '';
    }

    this.shadowRoot.getElementById('flightData').innerHTML = flightRows;
  }

  capitalize(str) {
    if (!str) return '';
    return str.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  formatValue(value) {
    if (!value) return '';
    // Handle nested objects (already formatted in updateData)
    if (typeof value === 'object') {
      return value;
    }
    return value;
  }

  formatTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date)) return dateString; // Return original string if invalid date
    // Format to local time in 24-hour format (HH:mm)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
  }

  formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    if (isNaN(date)) return dateString; // Return original string if invalid date
    // Format to local date and time
    return date.toLocaleString();
  }

  getCardSize() {
    return 4;
  }
}

customElements.define('avinor-flight-card', AvinorFlightCard);
