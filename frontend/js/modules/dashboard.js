/**
 * Dashboard Module
 */
window.Dashboard = {
    init: function () {
        this.renderAnnouncements();
    },

    renderAnnouncements: function () {
        const list = document.getElementById('announcement-list');
        if (!list) return;

        const mockAnnouncements = [
            { title: 'New Tactical Gear Protocol', date: '2h ago', author: 'Command Staff' },
            { title: 'Vespucci Beach Area BOLO', date: '5h ago', author: 'Detective Bureau' },
            { title: 'Server Sync Successfull', date: 'System', author: 'System' }
        ];

        list.innerHTML = mockAnnouncements.map(a => `
            <div style="padding:1rem; border-bottom:1px solid hsl(var(--border-dim)); display:flex; justify-content:space-between; align-items:center">
                <div>
                    <h4 style="font-size:0.9rem; margin-bottom:2px">${a.title}</h4>
                    <p style="font-size:0.75rem; color:hsl(var(--h) 10% 40%)">${a.author}</p>
                </div>
                <span style="font-size:0.7rem; color:hsl(var(--primary))">${a.date}</span>
            </div>
        `).join('');
    }
};
