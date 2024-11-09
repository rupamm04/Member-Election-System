function showPanel(panel) {
    document.getElementById('student-panel').style.display = panel === 'student' ? 'block' : 'none';
    document.getElementById('admin-panel').style.display = panel === 'admin' ? 'block' : 'none';
    document.getElementById('admin-options').style.display = 'none';
}

function exitSystem() {
    alert("Exiting the system.");
    // Implement exit logic if needed
}


function authenticateAdmin() {
    const username = document.getElementById('admin-username').value;
    const password = document.getElementById('admin-password').value;

    fetch('/admin/authenticate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username: username, password: password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('admin-options').style.display = 'block';
            document.getElementById('admin-message').innerText = "Admin logged in successfully.";
        } else {
            document.getElementById('admin-message').innerText = "Authentication failed.";
        }
    });
}

function checkVotingStatus() {
    const userId = document.getElementById('student-id').value;

    fetch('/student/validate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            document.getElementById('student-message').innerText = 'User ID is valid.';
        } else {
            document.getElementById('student-message').innerText = 'Invalid User ID.';
        }
    });
}


function castVote() {
    const userId = document.getElementById('student-id').value;
    const candidateId = document.getElementById('vote-candidate').value;

    fetch('/vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId, vote_input: candidateId })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('student-message').innerText = data.message;
    });
}


function initiateNewElection() {
    // Example data, replace with actual input values from our form
    const electionData = {
        year: 2023,
        branch: "CSE",
        total_voters: 200,
        number_of_candidates: 2,
        candidate_1: "Alice",
        candidate_2: "Bob"
    };

    fetch('/admin/initiate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(electionData)
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message); // Show success message
    });
}


function continueElection() {
    fetch('/admin/continue', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to continue the election');
        }
    })
    .then(data => {
        alert(data.message); // Show success or error message to the admin
        // Additional logic can be added here, such as updating the UI
    })
    .catch(error => {
        console.error('Error continuing the election:', error);
        alert('An error occurred while trying to continue the election. Please try again later.');
    });
}


function banUser() {
    const userId = prompt("Enter User ID to ban:");
    if (userId) {
        fetch('/admin/ban', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // Show message to the admin
        })
        .catch(error => {
            console.error('Error banning user:', error);
        });
    }
}



function deleteVote() {
    const userId = document.getElementById('student-id').value;

    fetch('/delete_vote', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('student-message').innerText = data.message;
    });
}


function displayResults() {
    fetch('/results', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Get the results div to display results
        const resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = ''; // Clear previous results

        // Display voting percentage
        const votingPercentage = data.voting_percentage || 0;
        resultsDiv.innerHTML += <h3>Voting Percentage: ${votingPercentage}%</h3>;
        
        // Create a list of results
        const resultsList = document.createElement('ul');
        data.results.forEach(candidate => {
            const listItem = document.createElement('li');
            listItem.innerText = 'Candidate ID: ${candidate.id}, Name: ${candidate.name}, Votes: ${candidate.votes}';
            resultsList.appendChild(listItem);
        });

        resultsDiv.appendChild(resultsList);
    })
    .catch(error => {
        console.error('Error fetching results:', error);
        document.getElementById('results').innerText = 'Could not fetch results. Please try again later.';
    });
}

function logout() {
    document.getElementById('admin-options').style.display = 'none';
    document.getElementById('admin-message').innerText = "Logged out.";
}