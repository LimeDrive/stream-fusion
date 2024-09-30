const sorts = ['quality', 'sizedesc', 'sizeasc', 'qualitythensize'];
const qualityExclusions = ['2160p', '1080p', '720p', '480p', 'rips', 'cam', 'hevc', 'unknown'];
const languages = ['en', 'fr', 'multi'];

document.addEventListener('DOMContentLoaded', function () {
    loadData();
    handleUniqueAccounts();
    updateProviderFields();
    updateDebridOrderList();
});

function setElementDisplay(elementId, displayStatus) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = displayStatus;
    }
}

function startRealDebridAuth() {
    document.getElementById('rd-auth-button').disabled = true;
    document.getElementById('rd-auth-button').textContent = "Authentification en cours...";

    fetch('/api/auth/realdebrid/device_code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur de requête');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('verification-url').href = data.direct_verification_url;
            document.getElementById('verification-url').textContent = data.verification_url;
            document.getElementById('user-code').textContent = data.user_code;
            document.getElementById('auth-instructions').style.display = 'block';
            pollForCredentials(data.device_code, data.expires_in);
        })
        .catch(error => {
            alert("Erreur lors de l'authentification. Veuillez réessayer.");
            resetAuthButton();
        });
}

function pollForCredentials(deviceCode, expiresIn) {
    const pollInterval = setInterval(() => {
        fetch(`/api/auth/realdebrid/credentials?device_code=${encodeURIComponent(deviceCode)}`, {
            method: 'POST',
            headers: {
                'accept': 'application/json'
            }
        })
            .then(response => {
                if (!response.ok) {
                    if (response.status === 400) {
                        console.log('Autorisation en attente...');
                        return null;
                    }
                    throw new Error('Erreur de requête');
                }
                return response.json();
            })
            .then(data => {
                if (data && data.client_id && data.client_secret) {
                    clearInterval(pollInterval);
                    clearTimeout(timeoutId);
                    getToken(deviceCode, data.client_id, data.client_secret);
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                console.log('Tentative suivante dans 5 secondes...');
            });
    }, 5000);

    const timeoutId = setTimeout(() => {
        clearInterval(pollInterval);
        alert("Le délai d'authentification a expiré. Veuillez réessayer.");
        resetAuthButton();
    }, expiresIn * 1000);
}

function getToken(deviceCode, clientId, clientSecret) {
    const url = `/api/auth/realdebrid/token?client_id=${encodeURIComponent(clientId)}&client_secret=${encodeURIComponent(clientSecret)}&device_code=${encodeURIComponent(deviceCode)}`;

    fetch(url, {
        method: 'POST',
        headers: {
            'accept': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur de requête');
            }
            return response.json();
        })
        .then(data => {
            if (data.access_token && data.refresh_token) {
                const rdCredentials = {
                    client_id: clientId,
                    client_secret: clientSecret,
                    access_token: data.access_token,
                    refresh_token: data.refresh_token
                };
                document.getElementById('rd_token_info').value = JSON.stringify(rdCredentials, null, 2);
                document.getElementById('auth-status').style.display = 'block';
                document.getElementById('auth-instructions').style.display = 'none';
                document.getElementById('rd-auth-button').disabled = true;
                document.getElementById('rd-auth-button').classList.add('opacity-50', 'cursor-not-allowed');
                document.getElementById('rd-auth-button').textContent = "Connexion réussie";
            } else {
                throw new Error('Tokens non reçus');
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            console.log('Erreur lors de la récupération du token. Nouvelle tentative lors du prochain polling.');
        });
}

function resetAuthButton() {
    const button = document.getElementById('rd-auth-button');
    button.disabled = false;
    button.textContent = "S'authentifier avec Real-Debrid";
    button.classList.remove('opacity-50', 'cursor-not-allowed');
}

function startADAuth() {
    document.getElementById('ad-auth-button').disabled = true;
    document.getElementById('ad-auth-button').textContent = "Authentication in progress...";

    console.log('Starting AllDebrid authentication');
    fetch('/api/auth/alldebrid/pin/get', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            console.log('Response received', response);
            if (!response.ok) {
                throw new Error('Request error');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('ad-verification-url').href = data.data.user_url;
            document.getElementById('ad-verification-url').textContent = data.data.base_url;
            document.getElementById('ad-user-code').textContent = data.data.pin;
            document.getElementById('ad-auth-instructions').style.display = 'block';
            pollForADCredentials(data.data.check, data.data.pin, data.data.expires_in);
        })
        .catch(error => {
            console.error('Detailed error:', error);
            alert("Authentication error. Please try again.");
            resetADAuthButton();
        });
}

function pollForADCredentials(check, pin, expiresIn) {
    const pollInterval = setInterval(() => {
        fetch(`/api/auth/alldebrid/pin/check?agent=streamfusion&check=${encodeURIComponent(check)}&pin=${encodeURIComponent(pin)}`, {
            method: 'GET',
            headers: {
                'accept': 'application/json'
            }
        })
            .then(response => {
                if (response.status === 400) {
                    console.log('Waiting for user authorization...');
                    return null;
                }
                if (!response.ok) {
                    throw new Error('Request error');
                }
                return response.json();
            })
            .then(data => {
                if (data === null) return; // Skip processing if user hasn't entered PIN yet
                if (data.data && data.data.activated && data.data.apikey) {
                    clearInterval(pollInterval);
                    clearTimeout(timeoutId);
                    document.getElementById('ad_token_info').value = data.data.apikey;
                    document.getElementById('ad-auth-status').style.display = 'block';
                    document.getElementById('ad-auth-instructions').style.display = 'none';
                    document.getElementById('ad-auth-button').disabled = true;
                    document.getElementById('ad-auth-button').textContent = "Connection successful";
                    console.log('AllDebrid authentication successful');
                } else {
                    console.log('Waiting for user authorization...');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                console.log('Next attempt in 5 seconds...');
            });
    }, 5000);

    const timeoutId = setTimeout(() => {
        clearInterval(pollInterval);
        alert("Authentication timeout. Please try again.");
        resetADAuthButton();
    }, expiresIn * 1000);
}

function resetADAuthButton() {
    const button = document.getElementById('ad-auth-button');
    button.disabled = false;
    button.textContent = "Connect with AllDebrid";
}

function handleUniqueAccounts() {
    const accounts = ['debrid_rd', 'debrid_ad', 'sharewood', 'yggflix'];

    accounts.forEach(account => {
        const checkbox = document.getElementById(account);
        if (checkbox) {
            const isUnique = checkbox.dataset.uniqueAccount === 'true';
            if (!isUnique) {
            } else {
                checkbox.checked = isUnique;
                checkbox.disabled = isUnique;
                checkbox.parentElement.classList.add('opacity-50', 'cursor-not-allowed');
            }
        }
    });
}

function updateDebridOrderList() {
    const debridOrderList = document.getElementById('debridOrderList');
    if (!debridOrderList) return;

    debridOrderList.innerHTML = '';

    let debridOrder = [];
    const currentUrl = window.location.href;
    let data = currentUrl.match(/\/([^\/]+)\/configure$/);
    if (data && data[1]) {
        try {
            const decodedData = JSON.parse(atob(data[1]));
            debridOrder = decodedData.service || [];
        } catch (error) {
            console.warn("No valid debrid order data in URL, using default order.");
        }
    }

    const rdEnabled = document.getElementById('debrid_rd').checked || document.getElementById('debrid_rd').disabled;
    const adEnabled = document.getElementById('debrid_ad').checked || document.getElementById('debrid_ad').disabled;

    if (debridOrder.length === 0 ||
        !debridOrder.every(service =>
            (service === 'Real-Debrid' && rdEnabled) ||
            (service === 'AllDebrid' && adEnabled)
        )) {
        debridOrder = [];
        if (rdEnabled) debridOrder.push('Real-Debrid');
        if (adEnabled) debridOrder.push('AllDebrid');
    }

    debridOrder.forEach(serviceName => {
        if ((serviceName === 'Real-Debrid' && rdEnabled) ||
            (serviceName === 'AllDebrid' && adEnabled)) {
            addDebridToList(serviceName);
        }
    });

    if (rdEnabled && !debridOrder.includes('Real-Debrid')) {
        addDebridToList('Real-Debrid');
    }
    if (adEnabled && !debridOrder.includes('AllDebrid')) {
        addDebridToList('AllDebrid');
    }

    Sortable.create(debridOrderList, {
        animation: 150,
        ghostClass: 'bg-gray-100',
        onEnd: function () {
            const newOrder = Array.from(debridOrderList.children).map(li => li.dataset.serviceName);
            console.log("Nouvel ordre des débrideurs:", newOrder);
        }
    });
}


function addDebridToList(serviceName) {
    const debridOrderList = document.getElementById('debridOrderList');
    const li = document.createElement('li');
    li.className = 'bg-gray-700 text-white text-sm p-1.5 rounded shadow cursor-move flex items-center justify-between w-64 mb-2';

    const text = document.createElement('span');
    text.textContent = serviceName;
    text.className = 'flex-grow truncate';

    const icon = document.createElement('span');
    icon.innerHTML = '&#8942;';
    icon.className = 'text-gray-400 ml-2 flex-shrink-0';

    li.appendChild(text);
    li.appendChild(icon);
    li.dataset.serviceName = serviceName;
    debridOrderList.appendChild(li);
}

function toggleDebridOrderList() {
    const orderList = document.getElementById('debridOrderList');
    const isChecked = document.getElementById('debrid_order').checked;
    orderList.classList.toggle('hidden', !isChecked);

    if (isChecked) {
        updateDebridOrderList();
    }
}

function updateDebridDownloaderOptions() {
    const debridDownloaderOptions = document.getElementById('debridDownloaderOptions');
    if (!debridDownloaderOptions) return;

    debridDownloaderOptions.innerHTML = '';

    const rdEnabled = document.getElementById('debrid_rd').checked || document.getElementById('debrid_rd').disabled;
    const adEnabled = document.getElementById('debrid_ad').checked || document.getElementById('debrid_ad').disabled;

    let firstOption = null;

    if (rdEnabled) {
        firstOption = addDebridDownloaderOption('Real-Debrid');
    }
    if (adEnabled) {
        if (!firstOption) {
            firstOption = addDebridDownloaderOption('AllDebrid');
        } else {
            addDebridDownloaderOption('AllDebrid');
        }
    }

    if (firstOption && !document.querySelector('input[name="debrid_downloader"]:checked')) {
        firstOption.checked = true;
    }
}

function addDebridDownloaderOption(serviceName) {
    const debridDownloaderOptions = document.getElementById('debridDownloaderOptions');
    const id = `debrid_downloader_${serviceName.toLowerCase().replace('-', '_')}`;

    const div = document.createElement('div');
    div.className = 'flex items-center';

    const input = document.createElement('input');
    input.type = 'radio';
    input.id = id;
    input.name = 'debrid_downloader';
    input.value = serviceName;
    input.className = 'h-4 w-4 border-gray-300 text-indigo-600 focus:ring-indigo-600';

    const label = document.createElement('label');
    label.htmlFor = id;
    label.className = 'ml-3 block text-sm font-medium text-white';
    label.textContent = serviceName;

    div.appendChild(input);
    div.appendChild(label);
    debridDownloaderOptions.appendChild(div);

    return input;
}


function updateProviderFields() {
    const RDdebridChecked = document.getElementById('debrid_rd').checked ||
        document.getElementById('debrid_rd').disabled;
    const ADdebridChecked = document.getElementById('debrid_ad').checked ||
        document.getElementById('debrid_ad').disabled;
    const cacheChecked = document.getElementById('cache')?.checked;
    const yggflixChecked = document.getElementById('yggflix')?.checked ||
        document.getElementById('yggflix')?.disabled;
    const sharewoodChecked = document.getElementById('sharewood')?.checked ||
        document.getElementById('sharewood')?.disabled;

    // Mise à jour de l'affichage des champs
    setElementDisplay('rd_debrid-fields', RDdebridChecked ? 'block' : 'none');
    setElementDisplay('ad_debrid-fields', ADdebridChecked ? 'block' : 'none');
    setElementDisplay('cache-fields', cacheChecked ? 'block' : 'none');
    setElementDisplay('ygg-fields', yggflixChecked ? 'block' : 'none');
    setElementDisplay('sharewood-fields', sharewoodChecked ? 'block' : 'none');

    const debridOrderCheckbox = document.getElementById('debrid_order');
    const debridOrderList = document.getElementById('debridOrderList');

    if (debridOrderCheckbox && debridOrderList) {
        const anyDebridEnabled = RDdebridChecked || ADdebridChecked;

        debridOrderCheckbox.disabled = !anyDebridEnabled;
        
        // Mise à jour de l'état de la case à cocher debrid_order
        if (!anyDebridEnabled) {
            debridOrderCheckbox.checked = false;
        }

        // Mise à jour de l'affichage de la liste d'ordre des débrideurs
        debridOrderList.classList.toggle('hidden', !(anyDebridEnabled && debridOrderCheckbox.checked));
    }

    // Mise à jour des options de débrideur
    updateDebridOrderList();
    updateDebridDownloaderOptions();

    // Vérification finale de la cohérence des états
    ensureDebridConsistency();
}

function ensureDebridConsistency() {
    const RDdebridChecked = document.getElementById('debrid_rd').checked;
    const ADdebridChecked = document.getElementById('debrid_ad').checked;
    const debridOrderChecked = document.getElementById('debrid_order').checked;

    if (!RDdebridChecked && !ADdebridChecked) {
        document.getElementById('debrid_order').checked = false;
        document.getElementById('debridOrderList').classList.add('hidden');
    }

    if (debridOrderChecked && !RDdebridChecked && !ADdebridChecked) {
        document.getElementById('debrid_order').checked = false;
    }

    updateDebridDownloaderOptions();
}

function loadData() {
    const currentUrl = window.location.href;
    let data = currentUrl.match(/\/([^\/]+)\/configure$/);
    let decodedData = {};
    if (data && data[1]) {
        try {
            decodedData = JSON.parse(atob(data[1]));
        } catch (error) {
            console.warn("No valid data to decode in URL, using default values.");
        }
    }

    function setElementValue(id, value, defaultValue) {
        const element = document.getElementById(id);
        if (element) {
            if (element.type === 'radio' || element.type === 'checkbox') {
                element.checked = (value !== undefined) ? value : defaultValue;
            } else {
                element.value = value || defaultValue || '';
            }
        }
    }

    const defaultConfig = {
        jackett: false,
        cache: true,
        cacheUrl: 'https://stremio-jackett-cacher.elfhosted.com/',
        zilean: true,
        yggflix: true,
        sharewood: false,
        maxSize: '18',
        resultsPerQuality: '10',
        maxResults: '30',
        minCachedResults: '10',
        torrenting: false,
        ctg_yggtorrent: true,
        ctg_yggflix: false,
        metadataProvider: 'tmdb',
        sort: 'qualitythensize',
        exclusion: ['cam', '2160p'],
        languages: ['fr', 'multi'],
        debrid_rd: false,
        debrid_ad: false,
        debrid_order: false
    };

    // Appliquer les valeurs (de l'URL ou par défaut)
    Object.keys(defaultConfig).forEach(key => {
        const value = decodedData[key] !== undefined ? decodedData[key] : defaultConfig[key];
        if (key === 'metadataProvider') {
            setElementValue('tmdb', value === 'tmdb', true);
            setElementValue('cinemeta', value === 'cinemeta', false);
        } else if (key === 'sort') {
            sorts.forEach(sort => {
                setElementValue(sort, value === sort, sort === defaultConfig.sort);
            });
        } else if (key === 'exclusion') {
            qualityExclusions.forEach(quality => {
                setElementValue(quality, value.includes(quality), defaultConfig.exclusion.includes(quality));
            });
        } else if (key === 'languages') {
            languages.forEach(language => {
                setElementValue(language, value.includes(language), defaultConfig.languages.includes(language));
            });
        } else {
            setElementValue(key, value, defaultConfig[key]);
        }
    });

    const serviceArray = decodedData.service || [];
    setElementValue('debrid_rd', serviceArray.includes('Real-Debrid'), defaultConfig.debrid_rd);
    setElementValue('debrid_ad', serviceArray.includes('AllDebrid'), defaultConfig.debrid_ad);
    setElementValue('debrid_order', serviceArray.length > 0, defaultConfig.debrid_order);

    // Catalogues
    setElementValue('ctg_yggtorrent', decodedData.yggtorrentCtg, defaultConfig.ctg_yggtorrent);
    setElementValue('ctg_yggflix', decodedData.yggflixCtg, defaultConfig.ctg_yggflix);

    // Tokens et passkeys
    setElementValue('rd_token_info', decodedData.RDToken, '');
    setElementValue('ad_token_info', decodedData.ADToken, '');
    setElementValue('sharewoodPasskey', decodedData.sharewoodPasskey, '');
    setElementValue('yggPasskey', decodedData.yggPasskey, '');
    setElementValue('ApiKey', decodedData.apiKey, '');
    setElementValue('exclusion-keywords', (decodedData.exclusionKeywords || []).join(', '), '');

    handleUniqueAccounts();
    updateProviderFields();

    const debridDownloader = decodedData.debridDownloader;
    if (debridDownloader) {
        const radioButton = document.querySelector(`input[name="debrid_downloader"][value="${debridDownloader}"]`);
        if (radioButton) {
            radioButton.checked = true;
        }
    }

    updateDebridDownloaderOptions();
    updateDebridOrderList();
    ensureDebridConsistency();
}

function getLink(method) {
    const data = {
        addonHost: new URL(window.location.href).origin,
        apiKey: document.getElementById('ApiKey').value,
        service: [],
        RDToken: document.getElementById('rd_token_info')?.value,
        ADToken: document.getElementById('ad_token_info')?.value,
        sharewoodPasskey: document.getElementById('sharewoodPasskey')?.value,
        maxSize: parseInt(document.getElementById('maxSize').value) || 16,
        exclusionKeywords: document.getElementById('exclusion-keywords').value.split(',').map(keyword => keyword.trim()).filter(keyword => keyword !== ''),
        languages: languages.filter(lang => document.getElementById(lang).checked),
        sort: sorts.find(sort => document.getElementById(sort).checked),
        resultsPerQuality: parseInt(document.getElementById('resultsPerQuality').value) || 5,
        maxResults: parseInt(document.getElementById('maxResults').value) || 5,
        minCachedResults: parseInt(document.getElementById('minCachedResults').value) || 5,
        exclusion: qualityExclusions.filter(quality => document.getElementById(quality).checked),
        cacheUrl: document.getElementById('cacheUrl')?.value,
        jackett: document.getElementById('jackett')?.checked,
        cache: document.getElementById('cache')?.checked,
        zilean: document.getElementById('zilean')?.checked,
        yggflix: document.getElementById('yggflix')?.checked,
        sharewood: document.getElementById('sharewood')?.checked,
        yggtorrentCtg: document.getElementById('ctg_yggtorrent')?.checked,
        yggflixCtg: document.getElementById('ctg_yggflix')?.checked,
        yggPasskey: document.getElementById('yggPasskey')?.value,
        torrenting: document.getElementById('torrenting').checked,
        debrid: false,
        metadataProvider: document.getElementById('tmdb').checked ? 'tmdb' : 'cinemeta',
        debridDownloader: document.querySelector('input[name="debrid_downloader"]:checked')?.value
    };

    data.service = Array.from(document.getElementById('debridOrderList').children).map(li => li.dataset.serviceName);
    data.debrid = data.service.length > 0;

    const missingRequiredFields = [];

    if (data.cache && !data.cacheUrl) missingRequiredFields.push("Cache URL");
    if (data.service.includes('Real-Debrid') && document.getElementById('rd_token_info') && !data.RDToken) missingRequiredFields.push("Real-Debrid Account Connection");
    if (data.service.includes('AllDebrid') && document.getElementById('ad_token_info') && !data.ADToken) missingRequiredFields.push("AllDebrid Account Connection");
    if (data.languages.length === 0) missingRequiredFields.push("Languages");
    if (!data.apiKey) missingRequiredFields.push("API Key");
    if (data.yggflix && document.getElementById('yggPasskey') && !data.yggPasskey) missingRequiredFields.push("Ygg Passkey");
    if (data.sharewood && document.getElementById('sharewoodPasskey') && !data.sharewoodPasskey) missingRequiredFields.push("Sharewood Passkey");

    if (missingRequiredFields.length > 0) {
        alert(`Please fill all required fields: ${missingRequiredFields.join(", ")}`);
        return false;
    }

    // Fonctions de validation
    function validatePasskey(passkey) {
        return /^[a-zA-Z0-9]{32}$/.test(passkey);
    }

    function validateApiKey(apiKey) {
        return /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(apiKey);
    }

    // Validation des champs
    if (data.yggflix && data.yggPasskey && !validatePasskey(data.yggPasskey)) {
        alert('Ygg Passkey doit contenir exactement 32 caractères alphanumériques');
        return false;
    }

    if (data.sharewood && data.sharewoodPasskey && !validatePasskey(data.sharewoodPasskey)) {
        alert('Sharewood Passkey doit contenir exactement 32 caractères alphanumériques');
        return false;
    }

    if (!validateApiKey(data.apiKey)) {
        alert('APIKEY doit être un UUID v4 valide');
        return false;
    }

    const encodedData = btoa(JSON.stringify(data));
    const stremio_link = `${window.location.host}/${encodedData}/manifest.json`;

    if (method === 'link') {
        window.open(`stremio://${stremio_link}`, "_blank");
    } else if (method === 'copy') {
        const link = window.location.protocol + '//' + stremio_link;
        navigator.clipboard.writeText(link).then(() => {
            alert('Link copied to clipboard');
        }, () => {
            alert('Error copying link to clipboard');
        });
    }
}

let showLanguageCheckBoxes = true;
function showCheckboxes() {
    let checkboxes = document.getElementById("languageCheckBoxes");
    checkboxes.style.display = showLanguageCheckBoxes ? "block" : "none";
    showLanguageCheckBoxes = !showLanguageCheckBoxes;
}