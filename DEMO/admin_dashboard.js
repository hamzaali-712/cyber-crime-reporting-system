document.addEventListener('DOMContentLoaded', function() {
    // 1. Check karein kaunsa officer login hai
    // Note: Aap login page par localStorage.setItem('loggedInOfficer', id) set karein
    const loggedInOfficer = localStorage.getItem('loggedInOfficer') || "FIA-786"; 
    document.getElementById('displayOfficerID').innerText = "Officer ID: " + loggedInOfficer;

    renderOfficerComplaints(loggedInOfficer);
});

function renderOfficerComplaints(officerID) {
    const tableBody = document.getElementById('complaintTableBody');
    const allComplaints = JSON.parse(localStorage.getItem('allComplaints')) || [];

    // Sirf is officer ke cases filter karein
    const filteredData = allComplaints.filter(c => c.officer === officerID);

    tableBody.innerHTML = '';
    let pending = 0;
    let resolved = 0;

    filteredData.forEach((item, index) => {
        if(item.status === 'completed') resolved++; else pending++;

        const row = `
            <tr>
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.category}</td>
                <td>
                    <select class="status-select" onchange="updateCaseStatus(${index}, this, '${officerID}')">
                        <option value="progress" ${item.status !== 'completed' ? 'selected' : ''}>In Progress</option>
                        <option value="completed" ${item.status === 'completed' ? 'selected' : ''}>Completed</option>
                    </select>
                </td>
                <td>
                    <div class="action-btns">
                        <button class="review-btn" onclick="alert('Reviewing Case: ${item.id}')">Review</button>
                        <button class="del-btn" onclick="deleteCase(${index}, '${officerID}')"><i class="fas fa-trash"></i></button>
                    </div>
                </td>
            </tr>`;
        tableBody.innerHTML += row;
    });

    // Update Stats Cards
    document.getElementById('totalCount').innerText = filteredData.length;
    document.getElementById('pendingCount').innerText = pending;
    document.getElementById('resolvedCount').innerText = resolved;
}

function updateCaseStatus(index, select, officerID) {
    let allComplaints = JSON.parse(localStorage.getItem('allComplaints')) || [];
    // Pura filter karke index nikalna zaroori hai
    allComplaints.find(c => c.officer === officerID && allComplaints.indexOf(c) === index); 
    // Simplified for demo:
    allComplaints[index].status = select.value;
    localStorage.setItem('allComplaints', JSON.stringify(allComplaints));
    renderOfficerComplaints(officerID);
}