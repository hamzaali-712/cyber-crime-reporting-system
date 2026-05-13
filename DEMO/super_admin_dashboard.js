document.addEventListener('DOMContentLoaded', function() {
    // Firebase se data fetch karna shuru karein
    renderOfficersFromFirebase();
    renderStatsFromFirebase();

    // Sidebar Logic (as it was)
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    const overlay = document.querySelector('.sidebar-overlay');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active');
        });
    }
});

// Firebase se real-time Officers list fetch karna
function renderOfficersFromFirebase() {
    const list = document.getElementById('officerList');
    const emptyMsg = document.getElementById('noOfficerMsg');

    db.ref('officers').on('value', (snapshot) => {
        list.innerHTML = '';
        let count = 0;

        if (snapshot.exists()) {
            emptyMsg.style.display = 'none';
            snapshot.forEach((child) => {
                const off = child.val();
                count++;
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td style="font-weight: 600;">
                        <i class="fas fa-user-shield" style="color: #00d2ff; margin-right: 10px;"></i> 
                        ${off.officerID}
                    </td>
                    <td><span class="status-badge">Authorized</span></td>
                    <td>
                        <button class="del-btn" onclick="removeOfficer('${child.key}')">
                            <i class="fas fa-trash-alt"></i> Remove Access
                        </button>
                    </td>
                `;
                list.appendChild(row);
            });
        } else {
            emptyMsg.style.display = 'block';
        }
        document.getElementById('officerCount').innerText = count;
    });
}

// Stats calculate karna
function renderStatsFromFirebase() {
    // Total Complaints ginna
    db.ref('complaints').on('value', (snapshot) => {
        const total = snapshot.numChildren() || 0;
        document.getElementById('totalComplaintsCount').innerText = total;

        let solved = 0;
        snapshot.forEach((child) => {
            if(child.val().status === 'Solved') solved++;
        });
        document.getElementById('solvedCasesCount').innerText = solved;
    });
}

// Officer delete karna Firebase se
function removeOfficer(id) {
    if (confirm("Are you sure you want to revoke this officer's access?")) {
        db.ref('officers/' + id).remove()
        .then(() => alert("Access Revoked!"))
        .catch((error) => alert("Error: " + error.message));
    }
}