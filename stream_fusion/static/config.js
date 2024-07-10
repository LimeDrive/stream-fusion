const sorts = ['quality', 'sizedesc', 'sizeasc', 'qualitythensize'];
const qualityExclusions = ['4K', '2160p', '1080p', '720p', '480p', 'rips', 'cam', 'unknown'];
const languages = ['en', 'fr', 'es', 'de', 'it', 'pt', 'ru', 'in', 'nl', 'hu', 'la', 'multi'];

document.addEventListener('DOMContentLoaded', function () {
    updateProviderFields();
});

function setElementDisplay(elementId, displayStatus) {
    const element = document.getElementById(elementId);
    if (!element) {
        return;
    }
    element.style.display = displayStatus;
}

function updateProviderFields(isChangeEvent = false) {
    if (document.getElementById('debrid').checked) {
        setElementDisplay('debrid-fields', 'block');
    } else {
        setElementDisplay('debrid-fields', 'none');
    }
    if (document.getElementById('cache')?.checked) {
        setElementDisplay('cache-fields', 'block');
    } else {
        setElementDisplay('cache-fields', 'none');
    }
}

// document.getElementById('service').addEventListener('change', function() {
//     updateProviderFields(true);
// });

function loadData() {
    const currentUrl = window.location.href;
    let data = currentUrl.match(/\/([^\/]+)\/configure$/);
    if (data && data[1].startsWith("ey")) {
        data = atob(data[1]);
        data = JSON.parse(data);
        if (document.getElementById('jackett')) {
            document.getElementById('jackett').checked = data.jackett;
        }
        if (document.getElementById('cache')) {
            document.getElementById('cache').checked = data.cache;
        }
        if (document.getElementById('cache-fields')) {
            document.getElementById('cacheUrl').value = data.cacheUrl;
        }
        if (document.getElementById('zilean')) {
            document.getElementById('zilean').checked = data.zilean;
        }
        document.getElementById('debrid_api_key').value = data.debridKey;
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
            if (data.sort === sort) {
                document.getElementById(sort).checked = true;
            }
        });

        qualityExclusions.forEach(quality => {
            if (data.exclusion.includes(quality)) {
                document.getElementById(quality).checked = true;
            }
        })

        languages.forEach(language => {
            if (data.languages.includes(language)) {
                document.getElementById(language).checked = true;
            }
        });

    }
}

let showLanguageCheckBoxes = true;

function showCheckboxes() {
    let checkboxes = document.getElementById("languageCheckBoxes");

    if (showLanguageCheckBoxes) {
        checkboxes.style.display = "block";
        showLanguageCheckBoxes = false;
    } else {
        checkboxes.style.display = "none";
        showLanguageCheckBoxes = true;
    }
}

loadData();

function getLink(method) {
    const addonHost = new URL(window.location.href).protocol.replace(':', '') + "://" + new URL(window.location.href).host
    const apiKey = document.getElementById('ApiKey').value;
    const debridApi = document.getElementById('debrid_api_key').value;
    const cacheUrl = document.getElementById('cacheUrl').value;
    const service = document.getElementById('service').value;
    const exclusionKeywords = document.getElementById('exclusion-keywords').value.split(',').map(keyword => keyword.trim()).filter(keyword => keyword !== '');
    let maxSize = document.getElementById('maxSize').value;
    let resultsPerQuality = document.getElementById('resultsPerQuality').value;
    let maxResults = document.getElementById('maxResults').value;
    let minCachedResults = document.getElementById('minCachedResults').value;
    const jackett = document.getElementById('jackett')?.checked;
    const cache = document.getElementById('cache')?.checked;
    const zilean = document.getElementById('zilean')?.checked;
    const torrenting = document.getElementById('torrenting').checked;
    const debrid = document.getElementById('debrid').checked;
    const metadataProvider = document.getElementById('tmdb').checked ? 'tmdb' : 'cinemeta';
    const selectedQualityExclusion = [];

    qualityExclusions.forEach(quality => {
        console.log(quality, document.getElementById(quality).checked);
        if (document.getElementById(quality).checked) {
            selectedQualityExclusion.push(quality);
        }
    });

    const selectedLanguages = [];
    languages.forEach(language => {
        if (document.getElementById(language).checked) {
            selectedLanguages.push(language);
        }
    });

    let filter;
    sorts.forEach(sort => {
        if (document.getElementById(sort).checked) {
            filter = sort;
        }
    });

    if (maxSize === '' || isNaN(maxSize)) {
        maxSize = 16;
    }
    if (maxResults === '' || isNaN(maxResults)) {
        maxResults = 5;
    }
    if (resultsPerQuality === '' || isNaN(resultsPerQuality)) {
        resultsPerQuality = 5;
    }
    if (minCachedResults === '' || isNaN(minCachedResults)) {
        minCachedResults = 5;
    }
    let data = {
        addonHost,
        apiKey,
        service,
        'debridKey': debridApi,
        maxSize,
        exclusionKeywords,
        'languages': selectedLanguages,
        'sort': filter,
        resultsPerQuality,
        maxResults,
        minCachedResults,
        'exclusion': selectedQualityExclusion,
        cacheUrl,
        jackett,
        cache,
        zilean,
        torrenting,
        debrid,
        metadataProvider
    };
    if ((cache && (cacheUrl === '')) || (debrid && debridApi === '') || languages.length === 0 || (apiKey === '')) {
        alert('Please fill all required fields');
        return false;
    }
    let stremio_link = `${window.location.host}/${btoa(JSON.stringify(data))}/manifest.json`;

    if (method === 'link') {
        window.open(`stremio://${stremio_link}`, "_blank");
    } else if (method === 'copy') {
        const link = window.location.protocol + '//' + stremio_link;

        if (!navigator.clipboard) {
            alert('Your browser does not support clipboard');
            console.log(link);
            return;
        }

        navigator.clipboard.writeText(link).then(() => {
            alert('Link copied to clipboard');
        }, () => {
            alert('Error copying link to clipboard');
        });
    }
}