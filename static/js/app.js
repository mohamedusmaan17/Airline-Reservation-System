/* ═══════════════════════════════════════════════════════════
   SKYBOOKER — FRONTEND APPLICATION LOGIC
   Complete Single Page Application (SPA) Engine
   ═══════════════════════════════════════════════════════════ */

// ── Application State ──────────────────────────────────
const state = {
    user: JSON.parse(localStorage.getItem('skybooker_user')) || null,
    token: localStorage.getItem('skybooker_token') || null,
    theme: localStorage.getItem('skybooker_theme') || 'dark',
    lang: localStorage.getItem('skybooker_lang') || 'en',
    currentPage: 'flight-search',
    adminSubPage: 'dashboard',
    searchFilters: {
        source: '',
        destination: '',
        date: '',
        tripType: 'one-way'
    },
    selectedFlight: null,
    selectedSeat: null,
    passengerData: null,
    lastBooking: null,
    loyaltyPoints: 1250,
    loyaltyTier: 'Gold'
};

// ── Internationalization (i18n) Dictionary ─────────────
const i18n = {
    en: {
        search_hero_title: "Fly Anywhere with SkyBooker",
        search_hero_sub: "Compare routes, pick your exact seat visually, and enjoy AI fare forecasts.",
        search_btn: "Search Flights",
        from_label: "From (Source)",
        to_label: "To (Destination)",
        date_label: "Departure Date",
        select_seat: "Select Seat →",
        my_bookings: "My Bookings",
        admin_dash: "Admin Dashboard",
        loyalty_perks: "Loyalty Perks",
        flight_radar: "Live Flight Radar",
        reviews: "Customer Reviews",
        sign_in: "Sign In",
        logout: "Logout",
        price_surge: "Prices expected to rise",
        delay_risk: "Delay Risk",
        carbon_footprint: "CO₂ Footprint",
    },
    hi: {
        search_hero_title: "स्काईबुकर के साथ कहीं भी उड़ान भरें",
        search_hero_sub: "मार्गों की तुलना करें, सीट चुनें और AI मूल्य पूर्वानुमान का आनंद लें।",
        search_btn: "उड़ानें खोजें",
        from_label: "कहाँ से",
        to_label: "कहाँ तक",
        date_label: "यात्रा की तिथि",
        select_seat: "सीट चुनें →",
        my_bookings: "मेरी बुकिंग",
        admin_dash: "एडमिन डैशबोर्ड",
        loyalty_perks: "रॉयल्टी लाभ",
        flight_radar: "लाइव फ्लाइट रडार",
        reviews: "ग्राहकों की समीक्षा",
        sign_in: "साइन इन करें",
        logout: "लॉग आउट",
        price_surge: "कीमतें बढ़ने की संभावना",
        delay_risk: "देरी का जोखिम",
        carbon_footprint: "CO₂ उत्सर्जन",
    },
    es: {
        search_hero_title: "Vuela a cualquier lugar con SkyBooker",
        search_hero_sub: "Compara rutas, elige tu asiento exacto y disfruta de previsiones IA.",
        search_btn: "Buscar Vuelos",
        from_label: "Origen",
        to_label: "Destino",
        date_label: "Fecha de Salida",
        select_seat: "Seleccionar Asiento →",
        my_bookings: "Mis Reservas",
        admin_dash: "Panel de Administración",
        loyalty_perks: "Beneficios de Fidelidad",
        flight_radar: "Radar en Vivo",
        reviews: "Reseñas de Clientes",
        sign_in: "Iniciar Sesión",
        logout: "Cerrar Sesión",
        price_surge: "Se espera aumento de precio",
        delay_risk: "Riesgo de Retraso",
        carbon_footprint: "Huella de CO₂",
    },
    fr: {
        search_hero_title: "Volez n'importe où avec SkyBooker",
        search_hero_sub: "Comparez les itinéraires, choisissez votre siège et profitez de la prévision IA.",
        search_btn: "Rechercher des Vols",
        from_label: "Départ",
        to_label: "Destination",
        date_label: "Date de départ",
        select_seat: "Choisir un siège →",
        my_bookings: "Mes Réservations",
        admin_dash: "Tableau de Bord Admin",
        loyalty_perks: "Privilèges Fidélité",
        flight_radar: "Radar de Vol en Direct",
        reviews: "Avis Clients",
        sign_in: "Se Connecter",
        logout: "Déconnexion",
        price_surge: "Hausse de prix prévue",
        delay_risk: "Risque de Retard",
        carbon_footprint: "Empreinte CO₂",
    }
};

function t(key) {
    const dict = i18n[state.lang] || i18n.en;
    return dict[key] || i18n.en[key] || key;
}

// ── Theme & Language Handlers ───────────────────────────
function initTheme() {
    document.documentElement.setAttribute('data-theme', state.theme);
    const btn = document.getElementById('theme-toggle-btn');
    if (btn) {
        btn.innerHTML = state.theme === 'dark' ? '<i class="fa-solid fa-sun"></i>' : '<i class="fa-solid fa-moon"></i>';
    }
}

function toggleTheme() {
    state.theme = state.theme === 'dark' ? 'light' : 'dark';
    localStorage.setItem('skybooker_theme', state.theme);
    initTheme();
    showToast(`Switched to ${state.theme.toUpperCase()} mode`, 'info');
}

function changeLanguage(langCode) {
    state.lang = langCode;
    localStorage.setItem('skybooker_lang', langCode);
    renderNav();
    navigate(state.currentPage);
    showToast(`Language set to ${langCode.toUpperCase()}`, 'info');
}

// ── API Client Helper ──────────────────────────────────
async function apiCall(endpoint, method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    if (state.token) {
        headers['Authorization'] = `Bearer ${state.token}`;
    }

    const options = { method, headers };
    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(endpoint, options);
        const data = await response.json().catch(() => ({}));

        if (!response.ok) {
            if (response.status === 401 && state.token) {
                logout();
                showToast('Session expired. Please log in again.', 'error');
                throw new Error('Unauthorized');
            }
            throw new Error(data.detail || 'Something went wrong');
        }

        return data;
    } catch (err) {
        if (err.message !== 'Unauthorized') {
            showToast(err.message, 'error');
        }
        throw err;
    }
}

// ── Toast Notifications ───────────────────────────────
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const iconMap = {
        success: '<i class="fa-solid fa-circle-check"></i>',
        error: '<i class="fa-solid fa-circle-xmark"></i>',
        info: '<i class="fa-solid fa-circle-info"></i>'
    };

    toast.innerHTML = `<span>${iconMap[type] || ''}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ── Auth & Quick Switcher ──────────────────────────────
async function quickLogin(username, password) {
    try {
        const data = await apiCall('/api/auth/login', 'POST', { username, password });
        loginUser(data.user, data.access_token);
    } catch (err) {
        // Handled
    }
}

function loginUser(userData, token) {
    state.user = userData;
    state.token = token;
    localStorage.setItem('skybooker_user', JSON.stringify(userData));
    localStorage.setItem('skybooker_token', token);
    renderNav();
    showToast(`Welcome back, ${userData.username}! (${userData.role.toUpperCase()})`, 'success');
    navigate('flight-search');
}

function logout() {
    state.user = null;
    state.token = null;
    localStorage.removeItem('skybooker_user');
    localStorage.removeItem('skybooker_token');
    renderNav();
    showToast('Logged out successfully', 'info');
    navigate('login');
}

// ── Navigation Bar Render ──────────────────────────────
function renderNav() {
    const linksContainer = document.getElementById('nav-links');
    const userContainer = document.getElementById('nav-user');
    if (!linksContainer || !userContainer) return;

    let linksHtml = `
        <button class="nav-link ${state.currentPage === 'flight-search' ? 'active' : ''}" onclick="navigate('flight-search')">
            <i class="fa-solid fa-plane-departure"></i> ${t('search_btn')}
        </button>
        <button class="nav-link ${state.currentPage === 'reviews' ? 'active' : ''}" onclick="navigate('reviews')">
            <i class="fa-solid fa-star"></i> ${t('reviews')}
        </button>
        <button class="nav-link ${state.currentPage === 'flight-radar' ? 'active' : ''}" onclick="navigate('flight-radar')">
            <i class="fa-solid fa-radar"></i> ${t('flight_radar')}
        </button>
    `;

    if (state.user) {
        linksHtml += `
            <button class="nav-link ${state.currentPage === 'my-bookings' ? 'active' : ''}" onclick="navigate('my-bookings')">
                <i class="fa-solid fa-ticket"></i> ${t('my_bookings')}
            </button>
            <button class="nav-link ${state.currentPage === 'loyalty' ? 'active' : ''}" onclick="navigate('loyalty')">
                <i class="fa-solid fa-crown text-warning"></i> ${t('loyalty_perks')}
            </button>
        `;

        if (state.user.role === 'admin') {
            linksHtml += `
                <button class="nav-link ${state.currentPage === 'admin' ? 'active' : ''}" onclick="navigate('admin')">
                    <i class="fa-solid fa-chart-line text-accent"></i> ${t('admin_dash')}
                </button>
            `;
        }
    }

    linksContainer.innerHTML = linksHtml;

    if (state.user) {
        userContainer.innerHTML = `
            <div class="user-badge">
                <div class="user-avatar">${state.user.username.charAt(0).toUpperCase()}</div>
                <span>${state.user.username}</span>
                <span class="btn-demo-pill ${state.user.role === 'admin' ? 'admin-pill' : ''}">${state.user.role}</span>
            </div>
            <button class="btn btn-secondary btn-sm" onclick="logout()">${t('logout')}</button>
        `;
    } else {
        userContainer.innerHTML = `
            <button class="btn btn-primary btn-sm" onclick="navigate('login')">${t('sign_in')}</button>
        `;
    }
}

function navigate(page, extra = null) {
    state.currentPage = page;
    renderNav();

    const app = document.getElementById('app');
    if (!app) return;
    app.className = 'app-container page-enter';

    switch (page) {
        case 'login': renderLoginPage(app); break;
        case 'flight-search': renderFlightSearchPage(app); break;
        case 'seat-map':
            if (extra) state.selectedFlight = extra;
            renderSeatMapPage(app);
            break;
        case 'passenger-details': renderPassengerDetailsPage(app); break;
        case 'my-bookings': renderMyBookingsPage(app); break;
        case 'loyalty': renderLoyaltyPage(app); break;
        case 'reviews': renderReviewsPage(app); break;
        case 'flight-radar': renderFlightRadarPage(app); break;
        case 'admin':
            if (extra) state.adminSubPage = extra;
            renderAdminPage(app);
            break;
        default: renderFlightSearchPage(app);
    }
}

// ═══════════════════════════════════════════════════════
// PAGE 1: Login & Register
// ═══════════════════════════════════════════════════════
function renderLoginPage(app) {
    app.innerHTML = `
        <div style="display:flex; align-items:center; justify-content:center; min-height: calc(100vh - 140px);">
            <div class="glass-card no-hover" style="max-width: 440px; width:100%; text-align:center;">
                <div class="logo-icon" style="font-size:3rem; margin-bottom: 1rem;">✈</div>
                <h2>Welcome to SkyBooker</h2>
                <p class="text-secondary mb-lg">Book flights with AI price forecasting & instant seat maps</p>

                <div class="search-trip-tabs mb-lg">
                    <button class="trip-tab active" id="tab-login" onclick="switchAuthTab('login')">Login</button>
                    <button class="trip-tab" id="tab-register" onclick="switchAuthTab('register')">Register Account</button>
                </div>

                <!-- Login Form -->
                <form id="login-form" onsubmit="handleLoginSubmit(event)">
                    <div class="form-group" style="text-align:left;">
                        <label class="form-label">Username</label>
                        <input type="text" id="login-username" class="form-input" placeholder="e.g. john or admin" required>
                    </div>
                    <div class="form-group" style="text-align:left;">
                        <label class="form-label">Password</label>
                        <input type="password" id="login-password" class="form-input" placeholder="••••••••" required>
                    </div>
                    <button type="submit" class="btn btn-primary btn-lg" style="width:100%;">Sign In</button>
                </form>

                <!-- Register Form -->
                <form id="register-form" style="display:none;" onsubmit="handleRegisterSubmit(event)">
                    <div class="form-group" style="text-align:left;">
                        <label class="form-label">Username</label>
                        <input type="text" id="reg-username" class="form-input" placeholder="Choose a username" required>
                    </div>
                    <div class="form-group" style="text-align:left;">
                        <label class="form-label">Email</label>
                        <input type="email" id="reg-email" class="form-input" placeholder="user@example.com" required>
                    </div>
                    <div class="form-group" style="text-align:left;">
                        <label class="form-label">Password</label>
                        <input type="password" id="reg-password" class="form-input" placeholder="Min 6 characters" required minlength="6">
                    </div>
                    <button type="submit" class="btn btn-primary btn-lg" style="width:100%;">Create Account</button>
                </form>
            </div>
        </div>
    `;
}

function switchAuthTab(type) {
    const loginForm = document.getElementById('login-form');
    const regForm = document.getElementById('register-form');
    const tabLogin = document.getElementById('tab-login');
    const tabReg = document.getElementById('tab-register');

    if (type === 'login') {
        loginForm.style.display = 'block';
        regForm.style.display = 'none';
        tabLogin.classList.add('active');
        tabReg.classList.remove('active');
    } else {
        loginForm.style.display = 'none';
        regForm.style.display = 'block';
        tabLogin.classList.remove('active');
        tabReg.classList.add('active');
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;
    try {
        const data = await apiCall('/api/auth/login', 'POST', { username, password });
        loginUser(data.user, data.access_token);
    } catch (err) {}
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;
    try {
        const data = await apiCall('/api/auth/register', 'POST', { username, email, password });
        loginUser(data.user, data.access_token);
    } catch (err) {}
}

// ═══════════════════════════════════════════════════════
// PAGE 2: Flight Search & AI Cards
// ═══════════════════════════════════════════════════════
async function renderFlightSearchPage(app) {
    app.innerHTML = `
        <div class="search-hero">
            <h1>${t('search_hero_title')}</h1>
            <p>${t('search_hero_sub')}</p>

            <div class="glass-card no-hover" style="max-width: 960px; margin: 0 auto; text-align: left;">
                <div class="search-trip-tabs">
                    <button class="trip-tab ${state.searchFilters.tripType === 'one-way' ? 'active' : ''}" onclick="setTripType('one-way')">One-Way</button>
                    <button class="trip-tab ${state.searchFilters.tripType === 'round-trip' ? 'active' : ''}" onclick="setTripType('round-trip')">Round-Trip</button>
                    <button class="trip-tab ${state.searchFilters.tripType === 'multi-city' ? 'active' : ''}" onclick="setTripType('multi-city')">Multi-City</button>
                </div>

                <form class="search-form-grid" onsubmit="handleSearchSubmit(event)" style="grid-template-columns: ${state.searchFilters.tripType === 'round-trip' ? '1fr 1fr 1fr 1fr 140px' : '1fr 1fr 1fr 140px'};">
                    <div class="form-group" style="margin:0;">
                        <label class="form-label">${t('from_label')}</label>
                        <input type="text" id="search-source" class="form-input" placeholder="e.g. Delhi or DEL" value="${state.searchFilters.source}">
                    </div>
                    <div class="form-group" style="margin:0;">
                        <label class="form-label">${t('to_label')}</label>
                        <input type="text" id="search-dest" class="form-input" placeholder="e.g. Mumbai or BOM" value="${state.searchFilters.destination}">
                    </div>
                    <div class="form-group" style="margin:0;">
                        <label class="form-label">${t('date_label')}</label>
                        <input type="date" id="search-date" class="form-input" value="${state.searchFilters.date}">
                    </div>
                    ${state.searchFilters.tripType === 'round-trip' ? `
                        <div class="form-group" style="margin:0;">
                            <label class="form-label">Return Date</label>
                            <input type="date" id="search-return-date" class="form-input" value="${state.searchFilters.returnDate || '2026-08-10'}">
                        </div>
                    ` : ''}
                    <div style="display:flex; align-items:flex-end;">
                        <button type="submit" class="btn btn-primary btn-lg" style="width:100%;">${t('search_btn')}</button>
                    </div>
                </form>

            </div>
        </div>

        <div class="flight-results">
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom: 1rem;">
                <h2>Available Flights</h2>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-secondary btn-sm" onclick="loadFlights('price')"><i class="fa-solid fa-arrow-down-short-wide"></i> Cheaper First</button>
                    <button class="btn btn-secondary btn-sm" onclick="loadFlights('early')"><i class="fa-solid fa-clock"></i> Earliest Departure</button>
                </div>
            </div>
            <div id="flight-cards-container" class="flight-cards-container">
                <div class="spinner"></div>
            </div>
        </div>
    `;

    loadFlights();
}

function setTripType(type) {
    state.searchFilters.tripType = type;
    renderFlightSearchPage(document.getElementById('app'));
}

function parseVoiceQuery(transcript) {
    let source = '';
    let destination = '';
    let dateStr = '';

    let text = transcript.toLowerCase().trim();

    // 1. Extract date if present (e.g. "on date 08/01/2026", "on 2026-08-01", "on 1st august 2026")
    const dateOnRegex = /on\s+(date\s+)?([a-z0-9\/\-\s]+)/i;
    const dateMatch = text.match(dateOnRegex);

    if (dateMatch) {
        let datePart = dateMatch[2].trim();
        text = text.replace(dateMatch[0], '').trim();

        try {
            const numDateMatch = datePart.match(/(\d{1,4})[\/\-\.](\d{1,2})[\/\-\.](\d{1,4})/);
            if (numDateMatch) {
                let p1 = parseInt(numDateMatch[1]);
                let p2 = parseInt(numDateMatch[2]);
                let p3 = parseInt(numDateMatch[3]);
                let y, m, d;
                if (p1 > 1000) { y = p1; m = p2; d = p3; }
                else if (p3 > 1000) { y = p3; m = p1; d = p2; }
                else { y = 2026; m = p1; d = p2; }
                dateStr = `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
            } else {
                const parsedDate = new Date(datePart);
                if (!isNaN(parsedDate.getTime())) {
                    dateStr = parsedDate.toISOString().split('T')[0];
                }
            }
        } catch (e) {}
    }

    // 2. Extract origin & destination cities
    if (text.includes(' to ')) {
        const parts = text.split(' to ');
        source = parts[0].replace(/flights?\s+from/g, '').replace(/flight\s+from/g, '').replace(/from/g, '').trim();
        destination = parts[1].replace(/flights?\s+/g, '').replace(/flight\s+/g, '').trim();
    } else if (text.includes(' from ')) {
        source = text.split(' from ')[1].trim();
    } else {
        source = text;
    }

    if (source) source = source.charAt(0).toUpperCase() + source.slice(1);
    if (destination) destination = destination.charAt(0).toUpperCase() + destination.slice(1);

    return { source, destination, dateStr };
}

function startVoiceSearch() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showToast('Web Speech API is not supported in this browser. Type your query.', 'info');
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';

    const voiceBtn = document.getElementById('voice-btn');
    if (voiceBtn) voiceBtn.classList.add('recording');
    showToast('🎙 Listening... Say e.g. "Flights from Chennai to Mumbai on date 01/08/2026"', 'info');

    recognition.onresult = (event) => {
        if (voiceBtn) voiceBtn.classList.remove('recording');
        const transcript = event.results[0][0].transcript;
        showToast(`🎙 Heard: "${transcript}"`, 'success');

        const parsed = parseVoiceQuery(transcript);

        const srcInput = document.getElementById('search-source');
        const dstInput = document.getElementById('search-dest');
        const dateInput = document.getElementById('search-date');

        if (parsed.source && srcInput) {
            srcInput.value = parsed.source;
            state.searchFilters.source = parsed.source;
        }
        if (parsed.destination && dstInput) {
            dstInput.value = parsed.destination;
            state.searchFilters.destination = parsed.destination;
        }
        if (parsed.dateStr && dateInput) {
            dateInput.value = parsed.dateStr;
            state.searchFilters.date = parsed.dateStr;
        }

        loadFlights();
    };

    recognition.onerror = () => {
        if (voiceBtn) voiceBtn.classList.remove('recording');
        showToast('Voice search cancelled or timed out.', 'info');
    };

    recognition.start();
}


async function loadFlights(sortBy = null) {
    const container = document.getElementById('flight-cards-container');
    if (!container) return;

    let url = '/api/flights/search';
    const params = new URLSearchParams();
    if (state.searchFilters.source) params.append('source', state.searchFilters.source);
    if (state.searchFilters.destination) params.append('destination', state.searchFilters.destination);
    if (state.searchFilters.date) params.append('flight_date', state.searchFilters.date);

    if (params.toString()) url += '?' + params.toString();

    try {
        let flights = await apiCall(url);
        if (sortBy === 'price') flights.sort((a, b) => a.ticket_price - b.ticket_price);
        if (sortBy === 'early') flights.sort((a, b) => a.departure_time.localeCompare(b.departure_time));

        if (flights.length === 0) {
            container.innerHTML = `
                <div class="glass-card empty-state text-center" style="padding:3rem;">
                    <div style="font-size:3rem; margin-bottom:1rem;">🛫</div>
                    <h3>No Flights Found</h3>
                    <p class="text-secondary">Try searching for different cities or clear your filter.</p>
                </div>
            `;
            return;
        }

        // Render Cards asynchronously with AI prediction integration
        container.innerHTML = flights.map(f => {
            // Simulated AI badge signals
            const surgePct = Math.floor((f.flight_id * 7) % 18 + 5);
            const delayProb = Math.floor((f.flight_id * 13) % 40 + 10);
            const co2Kg = Math.floor((f.ticket_price * 0.04));

            return `
                <div class="glass-card flight-card" onclick="selectFlightForBooking(${f.flight_id})">
                    <div class="flight-endpoint">
                        <div class="city">${f.source_name || 'Origin'}</div>
                        <div class="time">${f.departure_time}</div>
                        <div class="airport">Terminal ${f.terminal_no || 'T1'} • Gate ${f.gate_no || 'G1'}</div>
                    </div>

                    <div class="flight-divider">
                        <span class="flight-no text-accent" style="font-weight:700;">${f.airline_name || 'Airline'} ${f.flight_number}</span>
                        <div class="line"></div>
                        <span class="duration">${f.flight_date || 'Daily Direct'}</span>
                        
                        <div class="ai-chips-row">
                            <span class="ai-chip price-surge"><i class="fa-solid fa-fire"></i> Price +${surgePct}% soon</span>
                            <span class="ai-chip ${delayProb > 30 ? 'delay-risk' : 'delay-low'}">
                                <i class="fa-solid fa-triangle-exclamation"></i> ${delayProb}% Delay Risk
                            </span>
                            <span class="ai-chip carbon-eco"><i class="fa-solid fa-leaf"></i> ${co2Kg}kg CO₂</span>
                        </div>
                    </div>

                    <div class="flight-endpoint">
                        <div class="city">${f.destination_name || 'Destination'}</div>
                        <div class="time">${f.arrival_time}</div>
                        <div class="airport">Non-stop</div>
                    </div>

                    <div class="flight-price-box">
                        <div class="price">₹${f.ticket_price.toLocaleString()}</div>
                        <span style="font-size:0.75rem; color:var(--success); font-weight:700;"><i class="fa-solid fa-bolt"></i> ${f.available_seats} seats left</span>
                        <button class="btn btn-primary btn-sm mt-xs" style="width:100%;">
                            ${t('select_seat')}
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        if (container) container.innerHTML = `<div class="glass-card p-lg text-danger">Failed to load flights.</div>`;
    }
}

function handleSearchSubmit(e) {
    e.preventDefault();
    state.searchFilters.source = document.getElementById('search-source').value.trim();
    state.searchFilters.destination = document.getElementById('search-dest').value.trim();
    state.searchFilters.date = document.getElementById('search-date').value;
    loadFlights();
}

async function selectFlightForBooking(flightId) {
    if (!state.user) {
        showToast('Please sign in to proceed with booking', 'info');
        navigate('login');
        return;
    }

    try {
        const flight = await apiCall(`/api/flights/${flightId}`);
        state.selectedFlight = flight;
        navigate('seat-map');
    } catch (err) {}
}

// ═══════════════════════════════════════════════════════
// PAGE 3: Interactive Seat Map & AI Seat Recommendation
// ═══════════════════════════════════════════════════════
async function renderSeatMapPage(app) {
    if (!state.selectedFlight) {
        navigate('flight-search');
        return;
    }

    state.selectedSeat = null;

    app.innerHTML = `
        <div>
            <button class="btn btn-secondary btn-sm mb-md" onclick="navigate('flight-search')">← Back to Search</button>
            <div style="display:flex; align-items:center; justify-content:space-between;" class="mb-lg">
                <div>
                    <h1>Interactive Seat Map</h1>
                    <p class="text-secondary">Flight ${state.selectedFlight.flight_number}: ${state.selectedFlight.source_name} → ${state.selectedFlight.destination_name}</p>
                </div>
                <div class="ai-chip price-surge p-sm" style="font-size:0.85rem;">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> AI Seat Advisor Enabled
                </div>
            </div>

            <div class="seat-map-wrapper">
                <div class="glass-card seat-grid-container no-hover">
                    <div class="seat-filter-pills">
                        <button class="seat-pill active" onclick="filterSeats('all', this)">All Seats</button>
                        <button class="seat-pill" onclick="filterSeats('window', this)">Window</button>
                        <button class="seat-pill" onclick="filterSeats('aisle', this)">Aisle</button>
                        <button class="seat-pill" onclick="filterSeats('business', this)">Business Class (+₹1,500)</button>
                    </div>

                    <div class="plane-fuselage">
                        <div class="cockpit-header">✈ COCKPIT / FRONT OF AIRCRAFT</div>
                        <div id="seat-grid" class="seat-grid">
                            <div class="spinner"></div>
                        </div>
                    </div>

                    <div class="seat-legend">
                        <div class="legend-item"><div class="legend-box" style="background:rgba(59,130,246,0.3); border:1px solid #3b82f6;"></div> Economy</div>
                        <div class="legend-item"><div class="legend-box" style="background:rgba(245,158,11,0.3); border:1px solid #f59e0b;"></div> Business (+₹1,500)</div>
                        <div class="legend-item"><div class="legend-box" style="background:var(--success);"></div> Selected</div>
                        <div class="legend-item"><div class="legend-box" style="background:rgba(255,255,255,0.08);"></div> Booked</div>
                    </div>
                </div>

                <!-- Seat Sidebar -->
                <div class="glass-card no-hover" style="height:fit-content;">
                    <h3>Fare Summary</h3>
                    <div style="display:flex; justify-content:space-between; margin-top:1rem;" class="mb-xs">
                        <span class="text-secondary">Flight Base Fare</span>
                        <span>₹${state.selectedFlight.ticket_price.toLocaleString()}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;" class="mb-xs">
                        <span class="text-secondary">Selected Seat</span>
                        <span id="summary-seat-num" class="text-accent font-bold">None</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;" class="mb-xs">
                        <span class="text-secondary">Seat Addon</span>
                        <span id="summary-seat-addon">₹0</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; border-top:1px solid var(--border-subtle); padding-top:1rem; margin-top:1rem;">
                        <span class="font-bold">Total Fare</span>
                        <span id="summary-total-fare" class="text-success font-bold" style="font-size:1.5rem;">₹${state.selectedFlight.ticket_price.toLocaleString()}</span>
                    </div>

                    <button id="btn-proceed-pass" class="btn btn-primary btn-lg mt-lg" style="width:100%;" disabled onclick="navigate('passenger-details')">
                        Proceed to Passenger Info →
                    </button>
                </div>
            </div>
        </div>
    `;

    loadSeatGrid(state.selectedFlight.flight_id);
}

async function loadSeatGrid(flightId) {
    try {
        const seats = await apiCall(`/api/flights/${flightId}/seats`);
        const aiRecs = await apiCall(`/api/ai/seat-recommendation/${flightId}`).catch(() => ({ recommendations: [] }));
        const recSeatIds = new Set((aiRecs.recommendations || []).map(r => r.seat_id));

        const grid = document.getElementById('seat-grid');
        if (!grid) return;

        // Group by row
        const rows = {};
        seats.forEach(s => {
            const rNum = s.seat_number.replace(/\D/g, '');
            if (!rows[rNum]) rows[rNum] = [];
            rows[rNum].push(s);
        });

        grid.innerHTML = Object.keys(rows).map(rNum => {
            const rSeats = rows[rNum];
            const left = rSeats.slice(0, 3);
            const right = rSeats.slice(3, 6);

            return `
                <div class="seat-row" data-row-type="${rSeats[0].seat_class}">
                    <span class="row-label">${rNum}</span>
                    ${left.map(s => renderSeatButton(s, recSeatIds.has(s.seat_id))).join('')}
                    <div class="seat-aisle"></div>
                    ${right.map(s => renderSeatButton(s, recSeatIds.has(s.seat_id))).join('')}
                </div>
            `;
        }).join('');
    } catch (err) {}
}

function renderSeatButton(s, isAiRec) {
    let classes = ['seat'];
    if (s.is_booked) classes.push('booked');
    if (s.seat_class === 'business') classes.push('business');
    if (isAiRec && !s.is_booked) classes.push('ai-recommended');

    return `
        <div class="${classes.join(' ')}"
             id="seat-btn-${s.seat_id}"
             data-type="${s.seat_type}"
             data-class="${s.seat_class}"
             onclick="onSeatSelect(${JSON.stringify(s).replace(/"/g, '&quot;')})">
            ${s.seat_number}
        </div>
    `;
}

function filterSeats(filterType, btnEl) {
    document.querySelectorAll('.seat-pill').forEach(b => b.classList.remove('active'));
    btnEl.classList.add('active');

    document.querySelectorAll('.seat').forEach(el => {
        if (filterType === 'all') {
            el.style.opacity = '1';
        } else if (filterType === 'window' && el.getAttribute('data-type') === 'window') {
            el.style.opacity = '1';
        } else if (filterType === 'aisle' && el.getAttribute('data-type') === 'aisle') {
            el.style.opacity = '1';
        } else if (filterType === 'business' && el.getAttribute('data-class') === 'business') {
            el.style.opacity = '1';
        } else {
            el.style.opacity = '0.25';
        }
    });
}

function onSeatSelect(seat) {
    if (seat.is_booked) return;

    document.querySelectorAll('.seat.selected').forEach(e => e.classList.remove('selected'));
    const seatEl = document.getElementById(`seat-btn-${seat.seat_id}`);
    if (seatEl) seatEl.classList.add('selected');

    state.selectedSeat = seat;
    const total = state.selectedFlight.ticket_price + seat.price_addon;

    const numEl = document.getElementById('summary-seat-num');
    const addonEl = document.getElementById('summary-seat-addon');
    const totalEl = document.getElementById('summary-total-fare');
    const btn = document.getElementById('btn-proceed-pass');

    if (numEl) numEl.innerText = `${seat.seat_number} (${seat.seat_class.toUpperCase()})`;
    if (addonEl) addonEl.innerText = `+₹${seat.price_addon.toLocaleString()}`;
    if (totalEl) totalEl.innerText = `₹${total.toLocaleString()}`;
    if (btn) btn.disabled = false;
}

// ═══════════════════════════════════════════════════════
// PAGE 4: Passenger Info, OCR Scanner, & Payment Modal
// ═══════════════════════════════════════════════════════
function renderPassengerDetailsPage(app) {
    if (!state.selectedFlight || !state.selectedSeat) {
        navigate('flight-search');
        return;
    }

    const total = state.selectedFlight.ticket_price + state.selectedSeat.price_addon;

    app.innerHTML = `
        <div>
            <button class="btn btn-secondary btn-sm mb-md" onclick="navigate('seat-map')">← Back to Seat Selection</button>
            <div style="display:flex; align-items:center; justify-content:space-between;" class="mb-lg">
                <h1>Passenger Details & Payment</h1>
                <button class="btn btn-secondary btn-sm" onclick="openOCRModal()"><i class="fa-solid fa-camera text-accent"></i> AI OCR Passport Autofill</button>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 360px; gap: 1.5rem;">
                <div class="glass-card no-hover">
                    <h3>Traveler Information</h3>
                    <form id="passenger-form" onsubmit="handlePassengerFormSubmit(event)">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;" class="mt-md">
                            <div class="form-group">
                                <label class="form-label">First Name *</label>
                                <input type="text" id="p-first" class="form-input" required placeholder="John">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Last Name *</label>
                                <input type="text" id="p-last" class="form-input" required placeholder="Doe">
                            </div>
                        </div>

                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;">
                            <div class="form-group">
                                <label class="form-label">Email Address *</label>
                                <input type="email" id="p-email" class="form-input" required placeholder="john@example.com">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Phone Number *</label>
                                <input type="tel" id="p-phone" class="form-input" required placeholder="+91 9876543210">
                            </div>
                        </div>

                        <div style="display:grid; grid-template-columns: 1fr 1fr 1fr; gap:1rem;">
                            <div class="form-group">
                                <label class="form-label">Gender</label>
                                <select id="p-gender" class="form-select">
                                    <option value="Male">Male</option>
                                    <option value="Female">Female</option>
                                    <option value="Other">Other</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Date of Birth</label>
                                <input type="date" id="p-dob" class="form-input">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Passport Number</label>
                                <input type="text" id="p-passport" class="form-input" placeholder="Z1234567">
                            </div>
                        </div>

                        <div class="form-group mt-md">
                            <label class="form-label"><i class="fa-solid fa-suitcase-rolling text-accent"></i> Luggage & Baggage Allowance *</label>
                            <select id="p-baggage" class="form-select">
                                <option value="7kg Cabin + 15kg Check-in">🧳 Standard: 7kg Cabin + 15kg Check-in (Included)</option>
                                <option value="7kg Cabin + 20kg Check-in">🧳 Extra +5kg: 7kg Cabin + 20kg Check-in (+₹900)</option>
                                <option value="7kg Cabin + 25kg Check-in">🧳 Extra +10kg: 7kg Cabin + 25kg Check-in (+₹1,600)</option>
                                <option value="7kg Cabin + 35kg Check-in">🧳 Heavy Load: 7kg Cabin + 35kg Check-in (+₹2,800)</option>
                            </select>
                        </div>

                        <button type="submit" class="btn btn-primary btn-lg mt-md" style="width:100%;">
                            Proceed to Payment (₹${total.toLocaleString()}) →
                        </button>
                    </form>
                </div>

                <!-- Flight Summary -->
                <div class="glass-card no-hover" style="height:fit-content;">
                    <h3>Flight Summary</h3>
                    <div style="display:flex; justify-content:space-between;" class="mt-md mb-xs">
                        <span class="text-secondary">Trip Type</span>
                        <span class="btn-demo-pill">${state.searchFilters.tripType === 'round-trip' ? 'Round-Trip' : 'Single Trip (One-Way)'}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;" class="mb-xs">
                        <span class="text-secondary">Flight</span>
                        <span class="font-bold">${state.selectedFlight.flight_number}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;" class="mb-xs">
                        <span class="text-secondary">Route</span>
                        <span>${state.selectedFlight.source_name} → ${state.selectedFlight.destination_name}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;" class="mb-xs">
                        <span class="text-secondary">Departure</span>
                        <span>${state.selectedFlight.departure_time}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between;" class="mb-xs">
                        <span class="text-secondary">Seat Number</span>
                        <span class="text-accent font-bold">${state.selectedSeat.seat_number}</span>
                    </div>
                    <div style="display:flex; justify-content:space-between; border-top:1px solid var(--border-subtle); padding-top:1rem; margin-top:1rem;">
                        <span class="font-bold">Total Fare</span>
                        <span class="text-success font-bold" style="font-size:1.5rem;">₹${total.toLocaleString()}</span>
                    </div>
                </div>

            </div>
        </div>
    `;
}

function openOCRModal() {
    const modal = document.getElementById('ocr-modal');
    const body = document.getElementById('ocr-modal-body');
    if (!modal || !body) return;

    body.innerHTML = `
        <div style="text-align:center; padding:1rem;">
            <div style="border:2px dashed var(--border-active); border-radius:12px; padding:2rem; cursor:pointer;" onclick="triggerOCRScan()">
                <i class="fa-solid fa-cloud-arrow-up text-accent" style="font-size:3rem; margin-bottom:1rem;"></i>
                <h4>Click to Upload Passport / ID Photo</h4>
                <p class="text-secondary" style="font-size:0.85rem;">Supports JPG, PNG, Passport PDF format</p>
            </div>
            <div id="ocr-status" class="mt-md text-accent" style="display:none; font-weight:600;">
                <i class="fa-solid fa-spinner fa-spin"></i> Scanning Passport with Tesseract OCR AI...
            </div>
        </div>
    `;

    modal.style.display = 'flex';
}

async function triggerOCRScan() {
    const status = document.getElementById('ocr-status');
    if (status) status.style.display = 'block';

    try {
        const res = await apiCall('/api/ai/ocr-extract', 'POST', { document_type: 'passport' });
        const data = res.extracted_data;

        document.getElementById('p-first').value = data.first_name;
        document.getElementById('p-last').value = data.last_name;
        document.getElementById('p-dob').value = data.date_of_birth;
        document.getElementById('p-passport').value = data.passport_number;
        document.getElementById('p-gender').value = data.gender;

        closeModal('ocr-modal');
        showToast('⚡ Passenger fields auto-filled via OCR!', 'success');
    } catch (err) {}
}

async function handlePassengerFormSubmit(e) {
    e.preventDefault();

    state.passengerData = {
        first_name: document.getElementById('p-first').value.trim(),
        last_name: document.getElementById('p-last').value.trim(),
        email: document.getElementById('p-email').value.trim(),
        phone: document.getElementById('p-phone').value.trim(),
        gender: document.getElementById('p-gender').value,
        date_of_birth: document.getElementById('p-dob').value || null,
        passport_number: document.getElementById('p-passport').value.trim() || null,
        nationality: 'India',
        baggage: document.getElementById('p-baggage') ? document.getElementById('p-baggage').value : '7kg Cabin + 15kg Check-in'
    };

    openPaymentGatewayModal();
}

function openPaymentGatewayModal() {
    const modal = document.getElementById('payment-modal');
    const body = document.getElementById('payment-modal-body');
    if (!modal || !body) return;

    const total = state.selectedFlight.ticket_price + state.selectedSeat.price_addon;

    body.innerHTML = `
        <div>
            <div class="credit-card-preview">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-weight:700; font-size:1.1rem;">SkyBooker Pay</span>
                    <i class="fa-brands fa-cc-visa" style="font-size:1.8rem;"></i>
                </div>
                <div class="card-chip"></div>
                <div class="card-num" id="preview-card-num">•••• •••• •••• 4242</div>
                <div style="display:flex; justify-content:space-between; font-size:0.75rem;">
                    <div>CARD HOLDER<br><strong id="preview-card-name">${state.passengerData.first_name} ${state.passengerData.last_name}</strong></div>
                    <div>EXPIRES<br><strong>12/28</strong></div>
                </div>
            </div>

            <div class="search-trip-tabs mb-md">
                <button class="trip-tab active" onclick="switchPayTab('upi', this)">UPI / QR</button>
                <button class="trip-tab" onclick="switchPayTab('card', this)">Card</button>
                <button class="trip-tab" onclick="switchPayTab('net', this)">Netbanking</button>
            </div>

            <div id="pay-method-upi" class="qr-timer-box">
                <p class="text-secondary" style="font-size:0.85rem;">Scan QR code with GPay / PhonePe / Paytm</p>
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=upi://pay?pa=skybooker@upi" class="qr-code-img">
                <div style="font-size:0.8rem; color:var(--warning); font-weight:700;">⏱ Expires in 04:59</div>
            </div>

            <div id="pay-method-card" style="display:none;" class="form-group">
                <label class="form-label">Card Number</label>
                <input type="text" class="form-input" placeholder="4532 7100 8899 4242">
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:1rem;">
                <div>Total: <strong class="text-success" style="font-size:1.25rem;">₹${total.toLocaleString()}</strong></div>
                <button class="btn btn-primary btn-lg" onclick="executeFinalBooking()">Pay & Issue Ticket</button>
            </div>
        </div>
    `;

    modal.style.display = 'flex';
}

function switchPayTab(type, btnEl) {
    document.querySelectorAll('.trip-tab').forEach(b => b.classList.remove('active'));
    btnEl.classList.add('active');

    const upiBox = document.getElementById('pay-method-upi');
    const cardBox = document.getElementById('pay-method-card');

    if (type === 'upi') {
        if (upiBox) upiBox.style.display = 'block';
        if (cardBox) cardBox.style.display = 'none';
    } else {
        if (upiBox) upiBox.style.display = 'none';
        if (cardBox) cardBox.style.display = 'block';
    }
}

async function executeFinalBooking() {
    try {
        // Create passenger
        const passRes = await apiCall('/api/admin/passengers', 'POST', state.passengerData);

        // Create booking
        const bookingData = {
            passenger_id: passRes.passenger_id,
            flight_id: state.selectedFlight.flight_id,
            seat_id: state.selectedSeat.seat_id,
            payment_method: 'UPI',
            baggage_allowance: state.passengerData.baggage || '7kg Cabin + 15kg Check-in',
            trip_type: state.searchFilters.tripType === 'round-trip' ? 'Round-Trip' : 'One-Way'
        };

        const bookingRes = await apiCall('/api/bookings/', 'POST', bookingData);
        state.lastBooking = bookingRes;

        closeModal('payment-modal');
        showToast(`🎉 Booking Confirmed! PNR: ${bookingRes.pnr}`, 'success');
        openETicketModal(bookingRes);
    } catch (err) {}
}

// ═══════════════════════════════════════════════════════
// PAGE 5: E-Ticket PDF View & Download
// ═══════════════════════════════════════════════════════
function openETicketModal(b) {
    const modal = document.getElementById('eticket-modal');
    const body = document.getElementById('eticket-modal-body');
    if (!modal || !body) return;

    const qrUrl = `http://localhost:8000/api/bookings/${b.booking_id}/pdf`;

    body.innerHTML = `
        <div class="eticket-paper">
            <div class="eticket-header">
                <div>
                    <h2 style="color:#0f172a; font-size:1.5rem;">✈ SkyBooker E-TICKET</h2>
                    <span style="font-size:0.8rem; color:#64748b;">Boarding Pass & Official Receipt</span>
                </div>
                <div class="pnr-badge-box">PNR: ${b.pnr}</div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap:1rem; margin-bottom:1.5rem; font-size:0.9rem;">
                <div>
                    <div style="color:#64748b; font-size:0.75rem;">PASSENGER NAME</div>
                    <strong>${b.passenger_name}</strong>
                </div>
                <div>
                    <div style="color:#64748b; font-size:0.75rem;">FLIGHT NUMBER</div>
                    <strong>${b.flight_number}</strong>
                </div>
                <div>
                    <div style="color:#64748b; font-size:0.75rem;">SEAT NUMBER</div>
                    <strong style="color:#2563eb; font-size:1.2rem;">${b.seat_number}</strong>
                </div>
                <div>
                    <div style="color:#64748b; font-size:0.75rem;">TRIP TYPE</div>
                    <strong style="color:#10b981;">${b.trip_type || 'One-Way'}</strong>
                </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; background:#f8fafc; padding:1rem; border-radius:8px; margin-bottom:1.5rem;">
                <div>
                    <div style="color:#64748b; font-size:0.75rem;">BAGGAGE ALLOWANCE</div>
                    <strong style="color:#0f172a; font-size:0.95rem;"><i class="fa-solid fa-suitcase-rolling text-accent"></i> ${b.baggage_allowance || '7kg Cabin + 15kg Check-in'}</strong>
                </div>
                <div>
                    <div style="color:#64748b; font-size:0.75rem;">TOTAL PAID</div>
                    <strong style="color:#10b981; font-size:1.2rem;">₹${b.total_amount.toLocaleString()}</strong>
                </div>
                <div>
                    <div style="color:#64748b; font-size:0.75rem;">STATUS</div>
                    <span class="btn-demo-pill" style="background:#dcfce7; color:#166534;">CONFIRMED</span>
                </div>
            </div>

            <div style="text-align:center; padding:1rem; background:#f8fafc; border-radius:12px; border:1px dashed #cbd5e1;">
                <a href="${qrUrl}" target="_blank" title="Click to open ticket details PDF directly">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(qrUrl)}" style="width:125px; border:3px solid #2563eb; border-radius:10px; padding:4px; background:#fff;">
                </a>
                <div style="font-size:0.85rem; color:#2563eb; font-weight:700; margin-top:8px;">
                    📲 Direct QR Scanning Enabled
                </div>
                <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Scan with ANY phone camera to open ticket details directly</div>
            </div>
        </div>

        <div style="display:flex; gap:1rem; margin-top:1.5rem;">
            <a href="/api/bookings/${b.booking_id}/pdf" target="_blank" download="SkyBooker_BoardingPass_${b.pnr}.pdf" class="btn btn-primary" style="flex:1; text-decoration:none;">
                <i class="fa-solid fa-file-pdf"></i> Download Official PDF Ticket & Receipt
            </a>
            <button class="btn btn-secondary" style="flex:1;" onclick="closeModal('eticket-modal'); navigate('my-bookings');">Go to My Bookings</button>
        </div>
    `;

    modal.style.display = 'flex';
}


// ═══════════════════════════════════════════════════════
// PAGE 6: My Bookings & Refund Status Tracker
// ═══════════════════════════════════════════════════════
let allUserBookings = [];

async function renderMyBookingsPage(app) {
    app.innerHTML = `
        <div>
            <h1>My Bookings</h1>
            <p class="text-secondary mb-md">Manage tickets, check in online, reschedule, or track refund status.</p>

            <div class="search-trip-tabs mb-lg" style="justify-content:flex-start;">
                <button class="trip-tab active" onclick="filterBookingCards('all', this)">All Bookings</button>
                <button class="trip-tab" onclick="filterBookingCards('Confirmed', this)">Confirmed</button>
                <button class="trip-tab" onclick="filterBookingCards('Cancelled', this)">Cancelled / Refunds</button>
            </div>

            <div id="bookings-list" class="flight-cards-container">
                <div class="spinner"></div>
            </div>
        </div>
    `;

    try {
        allUserBookings = await apiCall('/api/bookings/my');
        displayBookingsList(allUserBookings);
    } catch (err) {}
}

function filterBookingCards(statusFilter, btnEl) {
    document.querySelectorAll('.trip-tab').forEach(b => b.classList.remove('active'));
    if (btnEl) btnEl.classList.add('active');

    if (statusFilter === 'all') {
        displayBookingsList(allUserBookings);
    } else {
        const filtered = allUserBookings.filter(b => b.booking_status === statusFilter);
        displayBookingsList(filtered);
    }
}

function displayBookingsList(bookings) {
    const container = document.getElementById('bookings-list');
    if (!container) return;

    if (bookings.length === 0) {
        container.innerHTML = `
            <div class="glass-card text-center p-xl">
                <h3>No Bookings Found</h3>
                <p class="text-secondary mb-md">You haven't booked any flights in this category.</p>
                <button class="btn btn-primary" onclick="navigate('flight-search')">Search Flights Now</button>
            </div>
        `;
        return;
    }

    container.innerHTML = bookings.map(b => `
        <div class="glass-card no-hover" style="margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-subtle); padding-bottom:1rem; margin-bottom:1rem;">
                <div>
                    <span class="font-bold" style="font-size:1.2rem; color:var(--text-accent);">PNR: ${b.pnr}</span>
                    <span class="text-secondary" style="font-size:0.85rem; margin-left:1rem;">Passenger: ${b.passenger_name}</span>
                </div>
                <div>
                    <span class="btn-demo-pill ${b.booking_status === 'Cancelled' ? 'admin-pill' : ''}">${b.booking_status}</span>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap:1rem;" class="mb-md">
                <div><span class="text-muted" style="font-size:0.75rem;">FLIGHT</span><br><strong>${b.flight_number}</strong></div>
                <div><span class="text-muted" style="font-size:0.75rem;">SEAT</span><br><strong class="text-accent">${b.seat_number}</strong></div>
                <div><span class="text-muted" style="font-size:0.75rem;">TOTAL PAID</span><br><strong class="text-success">₹${b.total_amount.toLocaleString()}</strong></div>
                <div><span class="text-muted" style="font-size:0.75rem;">DATE</span><br><span>${b.booking_date ? b.booking_date.split('T')[0] : 'Today'}</span></div>
            </div>

            ${b.booking_status === 'Cancelled' ? `
                <div style="background:var(--bg-glass); padding:1rem; border-radius:8px;" class="mb-md">
                    <div style="font-size:0.8rem; font-weight:700; color:var(--warning); margin-bottom:6px;">🔄 Refund Tracker Progress</div>
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-secondary);">
                        <span>1. Request Approved ✓</span>
                        <span>2. Processed by Bank ✓</span>
                        <span class="text-success">3. Refunded to Source</span>
                    </div>
                </div>
            ` : ''}

            <div style="display:flex; gap:8px; flex-wrap:wrap;">
                <a href="/api/bookings/${b.booking_id}/pdf" target="_blank" download="SkyBooker_BoardingPass_${b.pnr}.pdf" class="btn btn-primary btn-sm" style="text-decoration:none;">
                    <i class="fa-solid fa-file-pdf"></i> Download Official PDF
                </a>
                <button class="btn btn-secondary btn-sm" onclick='openETicketModal(${JSON.stringify(b)})'><i class="fa-solid fa-ticket"></i> View Digital Pass</button>
                ${b.booking_status !== 'Cancelled' ? `
                    <button class="btn btn-secondary btn-sm" style="background:var(--accent-gradient); color:#fff; border:none;" onclick="doCheckInClick(${b.booking_id})"><i class="fa-solid fa-plane-circle-check"></i> Check-In</button>
                    <button class="btn btn-secondary btn-sm" onclick="openRescheduleModal(${b.booking_id})"><i class="fa-solid fa-calendar-days"></i> Reschedule</button>
                    <button class="btn btn-danger btn-sm" onclick="cancelBookingClick(${b.booking_id})"><i class="fa-solid fa-ban"></i> Cancel Booking</button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

async function doCheckInClick(bookingId) {
    try {
        const res = await apiCall(`/api/bookings/${bookingId}/checkin`, 'POST');
        showToast(`🎉 Check-In Successful! Gate: ${res.gate}, Boarding #: ${res.boarding_number}`, 'success');
    } catch (err) {}
}



function openRescheduleModal(bookingId) {
    const modal = document.getElementById('reschedule-modal');
    const body = document.getElementById('reschedule-modal-body');
    if (!modal || !body) return;

    body.innerHTML = `
        <form onsubmit="handleRescheduleSubmit(event, ${bookingId})">
            <div class="form-group">
                <label class="form-label">Select New Travel Date</label>
                <input type="date" id="reschedule-date" class="form-input" required value="2026-08-10">
            </div>
            <div class="form-group">
                <label class="form-label">Reason for Rescheduling</label>
                <select class="form-select">
                    <option>Schedule Change</option>
                    <option>Personal Plan Update</option>
                    <option>Medical Necessity</option>
                </select>
            </div>
            <div style="background:var(--bg-glass); padding:10px; border-radius:8px; font-size:0.8rem;" class="mb-md text-success">
                <i class="fa-solid fa-crown text-warning"></i> Gold Member Privilege: Rescheduling fee (₹1,200) Waived!
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%;">Confirm Flight Reschedule</button>
        </form>
    `;

    modal.style.display = 'flex';
}

function handleRescheduleSubmit(e, bookingId) {
    e.preventDefault();
    closeModal('reschedule-modal');
    showToast('⚡ Flight rescheduled successfully! Confirmation email sent.', 'success');
}


async function cancelBookingClick(bookingId) {
    if (!confirm('Are you sure you want to cancel this booking? Refund will be initiated.')) return;
    try {
        await apiCall(`/api/bookings/${bookingId}/cancel`, 'PUT');
        showToast('Booking cancelled. Refund initiated.', 'info');
        renderMyBookingsPage(document.getElementById('app'));
    } catch (err) {}
}

// ═══════════════════════════════════════════════════════
// PAGE 7: Loyalty Tier Perks
// ═══════════════════════════════════════════════════════
function renderLoyaltyPage(app) {
    app.innerHTML = `
        <div>
            <h1>SkyBooker Rewards & Loyalty Tier</h1>
            <p class="text-secondary mb-lg">Earn points on every flight and unlock exclusive VIP airport privileges.</p>

            <div style="display:grid; grid-template-columns: 340px 1fr; gap:1.5rem;">
                <div class="glass-card no-hover text-center">
                    <div style="font-size:3rem; margin-bottom:0.5rem;" class="text-warning">🥇</div>
                    <h2>Gold Tier Member</h2>
                    <div class="text-accent font-bold mt-xs" style="font-size:1.5rem;">${state.loyaltyPoints} Points</div>
                    <p class="text-secondary" style="font-size:0.8rem; margin-top:8px;">750 points to Platinum Tier</p>

                    <button class="btn btn-primary btn-sm mt-md" onclick="showLoungePass()"><i class="fa-solid fa-couch"></i> Generate Airport Lounge Pass</button>
                </div>

                <div class="glass-card no-hover">
                    <h3>Your VIP Perks</h3>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:1rem;" class="mt-md">
                        <div style="background:var(--bg-glass); padding:1rem; border-radius:8px;">
                            <div style="font-weight:700; color:var(--success);"><i class="fa-solid fa-plane-circle-check"></i> Priority Boarding</div>
                            <p style="font-size:0.8rem; color:var(--text-secondary);">Skip airport queues with dedicated Gold lane.</p>
                        </div>
                        <div style="background:var(--bg-glass); padding:1rem; border-radius:8px;">
                            <div style="font-weight:700; color:var(--warning);"><i class="fa-solid fa-suitcase"></i> Extra Baggage Allowance</div>
                            <p style="font-size:0.8rem; color:var(--text-secondary);">+10 kg check-in allowance on all routes.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function showLoungePass() {
    showToast('🎫 Airport Lounge VIP Access Code: SKY-LOUNGE-9988', 'success');
}

// ═══════════════════════════════════════════════════════
// PAGE 8: Customer Reviews & AI Sentiment Analysis
// ═══════════════════════════════════════════════════════
async function renderReviewsPage(app) {
    app.innerHTML = `
        <div>
            <div style="display:flex; align-items:center; justify-content:space-between;" class="mb-lg">
                <div>
                    <h1>Customer Reviews & AI Sentiment</h1>
                    <p class="text-secondary">Read real passenger feedback auto-tagged with AI Sentiment scores.</p>
                </div>
                <button class="btn btn-primary" onclick="openReviewModal()"><i class="fa-solid fa-pen"></i> Write a Review</button>
            </div>

            <div id="reviews-list-container" style="display:grid; grid-template-columns: 1fr 1fr; gap:1.25rem;">
                <div class="spinner"></div>
            </div>
        </div>
    `;

    try {
        const reviews = await apiCall('/api/reviews/');
        const container = document.getElementById('reviews-list-container');
        if (!container) return;

        container.innerHTML = reviews.map(r => `
            <div class="glass-card no-hover">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div>
                        <strong class="text-primary">${r.user_name}</strong>
                        <span class="text-muted" style="font-size:0.75rem; margin-left:6px;">${r.flight_number || 'Flight'}</span>
                    </div>
                    <span class="btn-demo-pill ${r.sentiment === 'positive' ? '' : 'admin-pill'}">
                        ${r.sentiment.toUpperCase()} (${Math.round(r.sentiment_score * 100)}%)
                    </span>
                </div>
                <p style="font-size:0.9rem; color:var(--text-secondary); mb-xs">"${r.review_text}"</p>
                <div style="font-size:0.75rem; color:var(--warning);">{"★".repeat(r.rating)}</div>
            </div>
        `).join('');
    } catch (err) {}
}

function openReviewModal() {
    const modal = document.getElementById('review-modal');
    const body = document.getElementById('review-modal-body');
    if (!modal || !body) return;

    body.innerHTML = `
        <form onsubmit="submitReviewForm(event)">
            <div class="form-group">
                <label class="form-label">Star Rating</label>
                <select id="rev-rating" class="form-select">
                    <option value="5">⭐⭐⭐⭐⭐ (5/5)</option>
                    <option value="4">⭐⭐⭐⭐ (4/5)</option>
                    <option value="3">⭐⭐⭐ (3/5)</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Your Review</label>
                <textarea id="rev-text" class="form-textarea" rows="4" placeholder="How was your flight experience?" required></textarea>
            </div>
            <button type="submit" class="btn btn-primary" style="width:100%;">Submit & Analyze Sentiment</button>
        </form>
    `;

    modal.style.display = 'flex';
}

async function submitReviewForm(e) {
    e.preventDefault();
    const rating = parseInt(document.getElementById('rev-rating').value);
    const review_text = document.getElementById('rev-text').value.trim();

    try {
        const res = await apiCall('/api/reviews/', 'POST', { rating, review_text });
        closeModal('review-modal');
        showToast(`Review published! Sentiment: ${res.sentiment.toUpperCase()} ${res.emoji}`, 'success');
        renderReviewsPage(document.getElementById('app'));
    } catch (err) {}
}

// ═══════════════════════════════════════════════════════
// PAGE 9: Live Flight Status Simulation (Radar)
// ═══════════════════════════════════════════════════════
function renderFlightRadarPage(app) {
    app.innerHTML = `
        <div>
            <h1>Live Flight Radar Simulation</h1>
            <p class="text-secondary mb-lg">Animated real-time flight position tracker across major routes.</p>

            <div class="glass-card no-hover p-xl text-center mb-lg">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
                    <div><strong>DEL (Delhi)</strong><br><span class="text-muted">06:00 AM</span></div>
                    <div style="flex:1; margin:0 2rem; position:relative;">
                        <div style="height:4px; background:var(--border-subtle); border-radius:2px;"></div>
                        <div style="height:4px; width:65%; background:var(--accent-gradient); position:absolute; top:0; left:0; border-radius:2px;"></div>
                        <i class="fa-solid fa-plane text-accent" style="position:absolute; top:-12px; left:65%; font-size:1.4rem;"></i>
                    </div>
                    <div><strong>BOM (Mumbai)</strong><br><span class="text-muted">08:15 AM</span></div>
                </div>
                <div style="display:flex; justify-content:space-around; font-size:0.85rem;">
                    <div>Altitude: <strong class="text-accent">34,000 ft</strong></div>
                    <div>Speed: <strong class="text-accent">840 km/h</strong></div>
                    <div>Status: <strong class="text-success">On Schedule</strong></div>
                </div>
            </div>
        </div>
    `;
}

// ═══════════════════════════════════════════════════════
// PAGE 10: Admin Dashboard & Chart.js Analytics
// ═══════════════════════════════════════════════════════
async function renderAdminPage(app) {
    app.innerHTML = `
        <div>
            <div style="display:flex; align-items:center; justify-content:space-between;" class="mb-lg">
                <h1>⚡ Admin Analytics Dashboard</h1>
                <span class="btn-demo-pill admin-pill">SQL Aggregated Metrics</span>
            </div>

            <div id="admin-stats-grid" class="stats-grid mb-lg">
                <div class="spinner"></div>
            </div>

            <div class="admin-charts-grid mb-lg">
                <div class="glass-card chart-card no-hover">
                    <h3 class="mb-md">Revenue by Route (₹)</h3>
                    <canvas id="chart-route-revenue"></canvas>
                </div>
                <div class="glass-card chart-card no-hover">
                    <h3 class="mb-md">Customer Review Sentiment</h3>
                    <canvas id="chart-sentiment-pie"></canvas>
                </div>
            </div>

            <div class="glass-card no-hover">
                <h3 class="mb-md">Flight Occupancy Rates</h3>
                <div id="admin-occupancy-table" style="overflow-x:auto;">
                    <div class="spinner"></div>
                </div>
            </div>
        </div>
    `;

    try {
        const stats = await apiCall('/api/admin/dashboard');

        // Render Stats Grid
        const grid = document.getElementById('admin-stats-grid');
        if (grid) {
            grid.innerHTML = `
                <div class="stat-card">
                    <div class="text-muted" style="font-size:0.8rem;">TOTAL REVENUE</div>
                    <div class="stat-value">₹${stats.total_revenue.toLocaleString()}</div>
                </div>
                <div class="stat-card">
                    <div class="text-muted" style="font-size:0.8rem;">TOTAL BOOKINGS</div>
                    <div class="stat-value">${stats.total_bookings}</div>
                </div>
                <div class="stat-card">
                    <div class="text-muted" style="font-size:0.8rem;">ACTIVE FLIGHTS</div>
                    <div class="stat-value">${stats.total_flights}</div>
                </div>
                <div class="stat-card">
                    <div class="text-muted" style="font-size:0.8rem;">REGISTERED USERS</div>
                    <div class="stat-value">${stats.total_passengers}</div>
                </div>
            `;
        }

        // Render Chart.js Revenue Chart
        const routeCtx = document.getElementById('chart-route-revenue');
        if (routeCtx && typeof Chart !== 'undefined') {
            const labels = Object.keys(stats.route_revenue || {});
            const dataVals = Object.values(stats.route_revenue || {});

            new Chart(routeCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Route Revenue (₹)',
                        data: dataVals,
                        backgroundColor: 'rgba(37, 99, 235, 0.6)',
                        borderColor: '#2563eb',
                        borderWidth: 1
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Render Chart.js Sentiment Pie Chart
        const sentCtx = document.getElementById('chart-sentiment-pie');
        if (sentCtx && typeof Chart !== 'undefined') {
            const sData = stats.sentiment_counts || stats.sentiment_chart || { positive: 4, neutral: 1, negative: 0 };
            new Chart(sentCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Positive', 'Neutral', 'Negative'],
                    datasets: [{
                        data: [sData.positive || 0, sData.neutral || 0, sData.negative || 0],
                        backgroundColor: ['#10b981', '#f59e0b', '#ef4444']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Render Occupancy Rates Table
        const occContainer = document.getElementById('admin-occupancy-table');
        const occList = stats.occupancy_rates || stats.occupancy_data || [];
        if (occContainer && occList.length > 0) {
            occContainer.innerHTML = `
                <table style="width:100%; border-collapse:collapse; text-align:left; font-size:0.9rem;">
                    <thead>
                        <tr style="border-bottom:1px solid var(--border-subtle); color:var(--text-secondary);">
                            <th style="padding:10px;">Flight #</th>
                            <th style="padding:10px;">Route</th>
                            <th style="padding:10px;">Occupancy %</th>
                            <th style="padding:10px;">Available / Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${occList.map(o => `
                            <tr style="border-bottom:1px solid var(--border-subtle);">
                                <td style="padding:10px; font-weight:700;">${o.flight_number}</td>
                                <td style="padding:10px;">${o.route}</td>
                                <td style="padding:10px;">
                                    <span class="btn-demo-pill ${o.occupancy_pct > 80 ? '' : 'admin-pill'}">${o.occupancy_pct}%</span>
                                </td>
                                <td style="padding:10px;">${o.available_seats} / ${o.total_seats} seats</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }


    } catch (err) {}
}


// ═══════════════════════════════════════════════════════
// Floating AI Chatbot Widget Logic
// ═══════════════════════════════════════════════════════
function toggleChatbot() {
    const panel = document.getElementById('chatbot-panel');
    if (panel) {
        panel.style.display = panel.style.display === 'none' ? 'flex' : 'none';
    }
}

function sendQuickPrompt(promptText) {
    const input = document.getElementById('chatbot-input');
    if (input) {
        input.value = promptText;
        sendChatMessage();
    }
}

function handleChatKeyPress(e) {
    if (e.key === 'Enter') sendChatMessage();
}

function startVoiceAssistant() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        showToast('Web Speech API is not supported in this browser. Please type your query.', 'info');
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.lang = 'en-US';

    const micBtn = document.getElementById('chatbot-mic-btn');
    if (micBtn) micBtn.style.color = '#ef4444';
    showToast('🎙 Chatbot listening... Speak your question now', 'info');

    recognition.onresult = (event) => {
        if (micBtn) micBtn.style.color = '';
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById('chatbot-input');
        if (input) {
            input.value = transcript;
            sendChatMessage();
        }
    };

    recognition.onerror = () => {
        if (micBtn) micBtn.style.color = '';
        showToast('Voice input cancelled or timed out.', 'info');
    };

    recognition.start();
}


async function sendChatMessage() {
    const input = document.getElementById('chatbot-input');
    const container = document.getElementById('chatbot-messages');
    if (!input || !container) return;

    const userMsg = input.value.trim();
    if (!userMsg) return;

    // Append User Message
    container.innerHTML += `
        <div class="chat-msg user">
            <div class="msg-content">${userMsg}</div>
        </div>
    `;
    input.value = '';
    container.scrollTop = container.scrollHeight;

    try {
        const data = await apiCall('/api/ai/chatbot', 'POST', { message: userMsg });
        container.innerHTML += `
            <div class="chat-msg bot">
                <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
                <div class="msg-content">${data.response}</div>
            </div>
        `;
        container.scrollTop = container.scrollHeight;
    } catch (err) {}
}

function closeModal(modalId) {
    const m = document.getElementById(modalId);
    if (m) m.style.display = 'none';
}

// ── Application Initialization ─────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    renderNav();
    navigate(state.currentPage);
});
