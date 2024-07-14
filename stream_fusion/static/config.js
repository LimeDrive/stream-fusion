const sorts = ['quality', 'sizedesc', 'sizeasc', 'qualitythensize'];
const qualityExclusions = ['4K', '2160p', '1080p', '720p', '480p', 'rips', 'cam', 'unknown'];
const languages = ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'in', 'nl', 'hu', 'la', 'multi'];

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

function updateProviderFields() {
    setElementDisplay('debrid-fields', document.getElementById('debrid').checked ? 'block' : 'none');
    setElementDisplay('cache-fields', document.getElementById('cache')?.checked ? 'block' : 'none');
    setElementDisplay('ygg-fields', document.getElementById('yggflix')?.checked ? 'block' : 'none');
}

function loadData() {
    const currentUrl = window.location.href;
    let data = currentUrl.match(/\/([^\/]+)\/configure$/);
    if (data && data[1].startsWith("ey")) {
        try {
            // Decrypt data from URL
            const decryptedData = CryptoJS.AES.decrypt(atob(data[1]), secretApiKey).toString(CryptoJS.enc.Utf8);
            data = JSON.parse(decryptedData);
            
            // Fill form fields with decrypted data
            document.getElementById('jackett').checked = data.jackett;
            document.getElementById('cache').checked = data.cache;
            document.getElementById('cacheUrl').value = data.cacheUrl;
            document.getElementById('zilean').checked = data.zilean;
            document.getElementById('yggflix').checked = data.yggflix;
            document.getElementById('debrid_api_key').value = data.debridKey;
            document.getElementById('yggPasskey').value = data.yggPasskey;
            document.getElementById('yggUsername').value = data.yggUsername;
            document.getElementById('yggPassword').value = data.yggPassword;
            document.getElementById('service').value = data.service;
            document.getElementById('exclusion-keywords').value = (data.exclusionKeywords || []).join(', ');
            document.getElementById('maxSize').value = data.maxSize;
            document.getElementById('resultsPerQuality').value = data.resultsPerQuality;
            document.getElementById('maxResults').value = data.maxResults;
            document.getElementById('minCachedResults').value = data.minCachedResults;
            document.getElementById('torrenting').checked = data.torrenting;
            document.getElementById('debrid').checked = data.debrid;
            document.getElementById('tmdb').checked = data.metadataProvider === 'tmdb';
            document.getElementById('cinemeta').checked = data.metadataProvider === 'cinemeta';

            sorts.forEach(sort => {
                document.getElementById(sort).checked = data.sort === sort;
            });

            qualityExclusions.forEach(quality => {
                document.getElementById(quality).checked = data.exclusion.includes(quality);
            });

            languages.forEach(language => {
                document.getElementById(language).checked = data.languages.includes(language);
            });

            updateProviderFields();
        } catch (error) {
            console.error("Error decrypting data:", error);
        }
    }
}

function getLink(method) {
    const data = {
        addonHost: new URL(window.location.href).origin,
        apiKey: document.getElementById('ApiKey').value,
        service: document.getElementById('service').value,
        debridKey: document.getElementById('debrid_api_key').value,
        maxSize: parseInt(document.getElementById('maxSize').value) || 16,
        exclusionKeywords: document.getElementById('exclusion-keywords').value.split(',').map(keyword => keyword.trim()).filter(keyword => keyword !== ''),
        languages: languages.filter(lang => document.getElementById(lang).checked),
        sort: sorts.find(sort => document.getElementById(sort).checked),
        resultsPerQuality: parseInt(document.getElementById('resultsPerQuality').value) || 5,
        maxResults: parseInt(document.getElementById('maxResults').value) || 5,
        minCachedResults: parseInt(document.getElementById('minCachedResults').value) || 5,
        exclusion: qualityExclusions.filter(quality => document.getElementById(quality).checked),
        cacheUrl: document.getElementById('cacheUrl').value,
        jackett: document.getElementById('jackett')?.checked,
        cache: document.getElementById('cache')?.checked,
        zilean: document.getElementById('zilean')?.checked,
        yggflix: document.getElementById('yggflix')?.checked,
        yggUsername: document.getElementById('yggUsername')?.value,
        yggPassword: document.getElementById('yggPassword')?.value,
        yggPasskey: document.getElementById('yggPasskey')?.value,
        torrenting: document.getElementById('torrenting').checked,
        debrid: document.getElementById('debrid').checked,
        metadataProvider: document.getElementById('tmdb').checked ? 'tmdb' : 'cinemeta'
    };

    // Check if all required fields are filled
    if ((data.cache && !data.cacheUrl) || (data.debrid && !data.debridKey) || data.languages.length === 0 || !data.apiKey || (data.yggflix && (!data.yggPasskey || !data.yggUsername || !data.yggPassword))) {
        alert('Please fill all required fields');
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