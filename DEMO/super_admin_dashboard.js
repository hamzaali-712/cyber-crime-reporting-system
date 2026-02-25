document.addEventListener('DOMContentLoaded', function() {

    // ── Responsive Sidebar Toggle (Mobile) ──────────────────────────
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    const overlay = document.querySelector('.sidebar-overlay');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('active');
        });
    }

    // Close sidebar on nav-item click (mobile UX)
    document.querySelectorAll('.nav-item').forEach(function(item) {
        item.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('open');
                if (overlay) overlay.classList.remove('active');
            }
        });
    });

    // ── Original Logic ───────────────────────────────────────────────
    renderOfficers();
});

// Function to fetch and display enrolled officers
function renderOfficers() {
    const list = document.getElementById('officerList');
    const emptyMsg = document.getElementById('noOfficerMsg');

    // Memory se officers ki list uthana
    const officers = JSON.parse(localStorage.getItem('enrolledOfficers')) || [];

    // Clear current list
    list.innerHTML = '';
    document.getElementById('officerCount').innerText = officers.length;

    if (officers.length === 0) {
        emptyMsg.style.display = 'block';
        return;
    }

    emptyMsg.style.display = 'none';

    // List render karna
    officers.forEach((off, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td style="font-weight: 600;"><i class="fas fa-user-shield" style="color: #00d2ff; margin-right: 10px;"></i> ${off.id}</td>
            <td><span class="status-badge">Authorized</span></td>
            <td>
                <button class="del-btn" onclick="removeOfficer(${index})">
                    <i class="fas fa-trash-alt"></i> Remove Access
                </button>
            </td>
        `;
        list.appendChild(row);
    });
}

// Function to remove an officer
function removeOfficer(index) {
    if (confirm("Are you sure you want to revoke this officer's access?")) {
        let officers = JSON.parse(localStorage.getItem('enrolledOfficers')) || [];
        officers.splice(index, 1); // List se delete karna
        localStorage.setItem('enrolledOfficers', JSON.stringify(officers)); // Memory update karna
        renderOfficers(); // Table refresh karna
    }
}