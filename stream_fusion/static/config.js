const sorts = ['quality', 'sizedesc', 'sizeasc', 'qualitythensize'];
const qualityExclusions = ['2160p', '1080p', '720p', '480p', 'rips', 'cam', 'hevc', 'unknown'];
const languages = ['en', 'fr', 'multi'];

document.addEventListener('DOMContentLoaded', function () {
    updateProviderFields();
    loadData();
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
    console.log('Début de l\'authentification Real-Debrid');

    fetch('/api/auth/realdebrid/device_code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
    })
    .then(response => {
        console.log('Réponse reçue', response);
        if (!response.ok) {
            throw new Error('Erreur de requête');
        }
        return response.json();
    })
    .then(data => {
        console.log('Réponse reçue:', data);
        document.getElementById('verification-url').href = data.direct_verification_url;
        document.getElementById('verification-url').textContent = data.verification_url;
        document.getElementById('user-code').textContent = data.user_code;
        document.getElementById('auth-instructions').style.display = 'block';
        pollForCredentials(data.device_code, data.expires_in);
    })
    .catch(error => {
        console.error('Erreur détaillée:', error);
        alert("Erreur lors de l'authentification. Veuillez réessayer.");
        resetAuthButton();
    });
}

function pollForCredentials(deviceCode, expiresIn) {
    console.log('Début du polling avec device_code:', deviceCode);
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
            document.getElementById('debrid_api_key').value = JSON.stringify(rdCredentials, null, 2);
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

function updateProviderFields() {
    const debridChecked = document.getElementById('debrid').checked;
    const cacheChecked = document.getElementById('cache')?.checked;
    const yggflixChecked = document.getElementById('yggflix')?.checked;
    const sharewoodChecked = document.getElementById('sharewood')?.checked;

    const debridFields = document.getElementById('debrid-fields');
    const cacheFields = document.getElementById('cache-fields');
    const yggFields = document.getElementById('ygg-fields');
    const sharewoodFields = document.getElementById('sharewood-fields');

    if (debridFields) debridFields.style.display = debridChecked ? 'block' : 'none';
    if (cacheFields) cacheFields.style.display = cacheChecked ? 'block' : 'none';
    if (yggFields) yggFields.style.display = yggflixChecked ? 'block' : 'none';
    if (sharewoodFields) sharewoodFields.style.display = sharewoodChecked ? 'block' : 'none';
}

function loadData() {
    const currentUrl = window.location.href;
    let data = currentUrl.match(/\/([^\/]+)\/configure$/);
    if (data && data[1]) {
        try {
            const decodedData = JSON.parse(atob(data[1]));
            
            document.getElementById('jackett').checked = decodedData.jackett;
            document.getElementById('cache').checked = decodedData.cache;
            document.getElementById('cacheUrl').value = decodedData.cacheUrl;
            document.getElementById('zilean').checked = decodedData.zilean;
            document.getElementById('yggflix').checked = decodedData.yggflix;
            document.getElementById('sharewood').checked = decodedData.sharewood;
            document.getElementById('debrid_api_key').value = decodedData.debridKey;
            document.getElementById('sharewoodPasskey').value = decodedData.sharewoodPasskey;
            document.getElementById('yggPasskey').value = decodedData.yggPasskey;
            document.getElementById('ApiKey').value = decodedData.apiKey;
            document.getElementById('exclusion-keywords').value = (decodedData.exclusionKeywords || []).join(', ');
            document.getElementById('maxSize').value = decodedData.maxSize;
            document.getElementById('resultsPerQuality').value = decodedData.resultsPerQuality;
            document.getElementById('maxResults').value = decodedData.maxResults;
            document.getElementById('minCachedResults').value = decodedData.minCachedResults;
            document.getElementById('torrenting').checked = decodedData.torrenting;
            document.getElementById('debrid').checked = decodedData.debrid;
            document.getElementById('ctg_yggtorrent').checked = decodedData.yggtorrentCtg;
            document.getElementById('ctg_yggflix').checked = decodedData.yggflixCtg;
            document.getElementById('tmdb').checked = decodedData.metadataProvider === 'tmdb';
            document.getElementById('cinemeta').checked = decodedData.metadataProvider === 'cinemeta';

            sorts.forEach(sort => {
                document.getElementById(sort).checked = decodedData.sort === sort;
            });

            qualityExclusions.forEach(quality => {
                document.getElementById(quality).checked = decodedData.exclusion.includes(quality);
            });

            languages.forEach(language => {
                document.getElementById(language).checked = decodedData.languages.includes(language);
            });

            updateProviderFields();
        } catch (error) {
            console.error("Error decoding data:", error);
        }
    }
}

function getLink(method) {
    const data = {
        addonHost: new URL(window.location.href).origin,
        apiKey: document.getElementById('ApiKey').value,
        service: 'Real-Debrid',
        debridKey: document.getElementById('debrid_api_key')?.value,
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
        debrid: document.getElementById('debrid').checked,
        metadataProvider: document.getElementById('tmdb').checked ? 'tmdb' : 'cinemeta'
    };

    // Check if all required fields are filled
    const missingRequiredFields = [];

    if (data.cache && !data.cacheUrl) missingRequiredFields.push("Cache URL");
    if (data.debrid && document.getElementById('debrid_api_key') && !data.debridKey) missingRequiredFields.push("Debrid API Key");
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