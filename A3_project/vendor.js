'use strict';
// Local mock: no network request and no real credential.
const demo = localStorage.getItem('a3_demo_token');
document.getElementById('vendor').textContent =
    "Vendor skripti o‘qigan qiymat: " + (demo || 'YOQ');