function flipCard(hackathonId) {
    const card1 = document.getElementById(`${hackathonId}-card-front`);
    const card2 = document.getElementById(`${hackathonId}-card-back`);
    card1.classList.toggle("flipped");
    card2.classList.toggle("flipped");
}

function saveHackathon(event, hackathonId) {
    event.preventDefault();
    const saveButton = document.getElementById(`${hackathonId}-save`);
    const isSaved = saveButton.classList.contains('bg-[#e5462e]');

    saveButton.classList.toggle('bg-[#e5462e]', !isSaved);
    saveButton.classList.toggle('text-white', !isSaved);
    saveButton.classList.toggle('bg-white', isSaved);
    saveButton.textContent = isSaved ? "Save" : "Saved";

    fetch(`/hackathons/${hackathonId}/save`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({})
    });
}

function cancelLoginPop() {
    document.getElementById('login-popup').classList.replace('flex', 'hidden');
}

function addLoginPop() {
    document.getElementById('login-popup').classList.replace('hidden', 'flex');
}

function voteHackathon(event, hackathonId, voteState) {
    event.preventDefault();
    const upButton = document.getElementById(`${hackathonId}-up`);
    const downButton = document.getElementById(`${hackathonId}-down`);
    const voteText = document.getElementById(`${hackathonId}-vote-text`);
    let method = 'POST';
    let voteChange = 0;

    if (voteState === 'true') {
        if (downButton.classList.contains('fill-black')) {
            downButton.classList.replace('fill-black', 'fill-white');
            upButton.classList.replace('fill-white', 'fill-black');
            voteChange = 2;
        } else if (upButton.classList.contains('fill-black')) {
            upButton.classList.replace('fill-black', 'fill-white');
            voteChange = -1;
            method = 'DELETE';
        } else {
            upButton.classList.replace('fill-white', 'fill-black');
            voteChange = 1;
        }
    } else {
        if (upButton.classList.contains('fill-black')) {
            upButton.classList.replace('fill-black', 'fill-white');
            downButton.classList.replace('fill-white', 'fill-black');
            voteChange = -2;
        } else if (downButton.classList.contains('fill-black')) {
            downButton.classList.replace('fill-black', 'fill-white');
            voteChange = 1;
            method = 'DELETE';
        } else {
            downButton.classList.replace('fill-white', 'fill-black');
            voteChange = -1;
        }
    }

    voteText.textContent = parseInt(voteText.textContent) + voteChange;

    fetch(`/hackathons/${hackathonId}/vote/?vote_type=${voteState}`, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({})
    })
        .then(response => response.json())
        .then(data => console.log('successful:', data))
        .catch(error => console.error('failed:', error));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
