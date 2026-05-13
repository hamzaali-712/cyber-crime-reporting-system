document.addEventListener('DOMContentLoaded', function() {
    // ── Responsive Sidebar Logic (Aapka original code) ──────────────────────────
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    const overlay = document.querySelector('.sidebar-overlay');

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            if (overlay) overlay.classList.toggle('active');
        });
    }

    // ── Firebase & Officer Logic (Integrated) ───────────────────────────────

    // 1. Check karein kaunsa officer login hai
    const loggedInOfficer = localStorage.getItem('loggedInOfficer') || "FIA-786";
    document.getElementById('displayOfficerID').innerText = "Officer ID: " + loggedInOfficer;

    // 2. Firebase se complaints load karein
    renderOfficerComplaints(loggedInOfficer);
});

function renderOfficerComplaints(officerID) {
    const tableBody = document.getElementById('complaintTableBody');
    
    // Real-time listener: Firebase se data live uthana
    db.ref('complaints').on('value', (snapshot) => {
        tableBody.innerHTML = '';
        let total = 0, pending = 0, resolved = 0;

        snapshot.forEach((child) => {
            const item = child.val();
            
            // Sirf is officer ke cases filter karein (Field check: assignedTo ya officer)
            // Maine yahan dono check laga diye hain taake mismatch na ho
            if (item.assignedTo === officerID || item.officer === officerID) {
                total++;
                const currentStatus = item.status || "Pending";
                if(currentStatus === 'Solved' || currentStatus === 'completed') resolved++; else pending++;

                const row = `
                    <tr>
                        <td>#${child.key.substring(0, 6)}</td>
                        <td>${item.victimName || item.name}</td>
                        <td>${item.crimeType || item.category}</td>
                        <td>
                            <select class="status-select" onchange="updateCaseStatus('${child.key}', this.value, '${officerID}')">
                                <option value="Pending" ${currentStatus !== 'Solved' ? 'selected' : ''}>Pending</option>
                                <option value="Solved" ${currentStatus === 'Solved' ? 'selected' : ''}>Solved</option>
                            </select>
                        </td>
                        <td>
                            <div class="action-btns">
                                <button class="review-btn" onclick="openReviewModal('${child.key}')">Review</button>
                                <button class="del-btn" onclick="deleteCase('${child.key}')"><i class="fas fa-trash"></i></button>
                            </div>
                        </td>
                    </tr>`;
                tableBody.innerHTML += row;
            }
        });

        // Stats Cards update
        document.getElementById('totalCount').innerText = total;
        document.getElementById('pendingCount').innerText = pending;
        document.getElementById('resolvedCount').innerText = resolved;
    });
}

// Case Status update karna Firebase mein
function updateCaseStatus(caseID, newStatus, officerID) {
    db.ref('complaints/' + caseID).update({
        status: newStatus
    }).then(() => {
        console.log("Status Updated!");
    });
}

// Case delete karna Firebase se
function deleteCase(caseID) {
    if (confirm("Are you sure you want to delete this record?")) {
        db.ref('complaints/' + caseID).remove();
    }
}

// Review Modal (Popup) function
function openReviewModal(caseID) {
    db.ref('complaints/' + caseID).once('value').then((snapshot) => {
        const data = snapshot.val();
        const modal = document.getElementById('reviewModal');
        const content = document.getElementById('modalContent');
        
        content.innerHTML = `
            <p><strong>Victim Name:</strong> ${data.victimName || data.name}</p>
            <p><strong>Crime Type:</strong> ${data.crimeType || data.category}</p>
            <p><strong>Description:</strong> ${data.description || 'No description'}</p>
            <p><strong>Location:</strong> ${data.location || 'N/A'}</p>
        `;
        modal.style.display = 'block';
    });
}