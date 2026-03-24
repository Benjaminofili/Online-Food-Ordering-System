(function () {
    function normalizeStatus(rawStatus) {
        return String(rawStatus || '').trim().toLowerCase();
    }

    function iconForStatus(status) {
        const map = {
            pending: 'fa-clock',
            accepted: 'fa-check',
            preparing: 'fa-fire',
            'out for delivery': 'fa-motorcycle',
            delivered: 'fa-check-double',
            completed: 'fa-check-double',
            cancelled: 'fa-ban'
        };
        return map[status] || 'fa-info-circle';
    }

    function badgeHtml(eventData, options) {
        const opts = options || {};
        const status = normalizeStatus(eventData && eventData.status);
        const tone = (eventData && eventData.status_tone) || 'secondary';
        const label = (eventData && eventData.status_label) || (status ? status.replace(/\b\w/g, c => c.toUpperCase()) : 'Unknown');
        const icon = iconForStatus(status);
        const extraClass = opts.extraClass ? ` ${opts.extraClass}` : '';
        const textClass = tone === 'warning' ? ' text-dark' : (opts.forceWhiteText ? ' text-white' : '');
        return `<span class="badge badge-${tone}${textClass}${extraClass}" data-status="${status}"><i class="fas ${icon} mr-1"></i>${label}</span>`;
    }

    window.OrderSync = {
        normalizeStatus,
        badgeHtml
    };
})();
