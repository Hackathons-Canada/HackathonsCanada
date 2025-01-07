function flipCard(hackathonId) {
    const card1 = document.getElementById(`${hackathonId}-card-front`);
    const card2 = document.getElementById(`${hackathonId}-card-back`);
    card1.classList.toggle("flipped");
    card2.classList.toggle("flipped");
}

function copyText(text) {

    navigator.clipboard.writeText(text);

    alert("Copied the text: " + text);
}

function toggleAccordion(index) {
    const content = document.getElementById(`accordion-content-${index}`);
    const allContents = document.querySelectorAll('[id^="accordion-content-"]');

    allContents.forEach((item) => {
        if (item !== content) {
            item.classList.add('hidden');
        }
    });

    content.classList.toggle('hidden');
}

function saveHackathon(event, hackathonId) {
    event.preventDefault();
    event.stopPropagation();
    const saveButton = document.getElementById(`${hackathonId}-save`);
    const isSaved = saveButton.classList.contains('bg-[#e5462e]');
    // was not working 
    // saveButton.classList.toggle('bg-[#e5462e]', !isSaved);
    // saveButton.classList.toggle('text-white', !isSaved);
    // saveButton.classList.toggle('bg-white', isSaved);
    console.log(saveButton.classList);
    if (!isSaved) {
        saveButton.classList.remove('bg-white');
        saveButton.classList.add('bg-[#e5462e]', 'text-white');
    } else {
        saveButton.classList.remove('bg-[#e5462e]', 'text-white');
        saveButton.classList.add('bg-white');
    }

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
// First, let's add a debounce utility function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Keep track of ongoing votes to prevent concurrent requests
const pendingVotes = new Set();

function handleVote(event, hackathonId, isUpvote) {
    event.preventDefault();

    // If there's already a pending vote for this hackathon, ignore the click
    if (pendingVotes.has(hackathonId)) {
        console.log('Vote in progress, please wait...');
        return;
    }

    // Get UI elements
    const upButton = document.getElementById(`${hackathonId}-up`);
    const downButton = document.getElementById(`${hackathonId}-down`);
    const voteText = document.getElementById(`${hackathonId}-vote-text`);
    const buttonContainer = upButton.closest('div');

    // Add visual feedback that the vote is being processed
    buttonContainer.style.opacity = '0.7';
    buttonContainer.style.pointerEvents = 'none';
    pendingVotes.add(hackathonId);

    let method, voteChange;

    // If clicking upvote button
    if (isUpvote) {
        if (upButton.classList.contains('fill-black')) {
            method = 'DELETE';
            voteChange = -1;
            upButton.classList.replace('fill-black', 'fill-white');
        } else if (downButton.classList.contains('fill-black')) {
            method = 'POST';
            voteChange = 2;
            upButton.classList.replace('fill-white', 'fill-black');
            downButton.classList.replace('fill-black', 'fill-white');
        } else {
            method = 'POST';
            voteChange = 1;
            upButton.classList.replace('fill-white', 'fill-black');
        }
    } else {
        if (downButton.classList.contains('fill-black')) {
            method = 'DELETE';
            voteChange = 1;
            downButton.classList.replace('fill-black', 'fill-white');
        } else if (upButton.classList.contains('fill-black')) {
            method = 'POST';
            voteChange = -2;
            downButton.classList.replace('fill-white', 'fill-black');
            upButton.classList.replace('fill-black', 'fill-white');
        } else {
            method = 'POST';
            voteChange = -1;
            downButton.classList.replace('fill-white', 'fill-black');
        }
    }

    const originalUpButtonState = upButton.classList.contains('fill-black') ? 'fill-black' : 'fill-white';
    const originalDownButtonState = downButton.classList.contains('fill-black') ? 'fill-black' : 'fill-white';
    const originalVoteCount = parseInt(voteText.textContent);

    voteText.textContent = (originalVoteCount + voteChange).toString();

    // Create a function to reset the UI state
    const resetState = () => {
        buttonContainer.style.opacity = '1';
        buttonContainer.style.pointerEvents = 'auto';
        pendingVotes.delete(hackathonId);
        voteText.textContent = originalVoteCount;
        upButton.classList.remove('fill-black', 'fill-white');
        downButton.classList.remove('fill-black', 'fill-white');
        upButton.classList.add(originalUpButtonState);
        downButton.classList.add(originalDownButtonState);
    };

    fetch(`/hackathons/${hackathonId}/vote/?vote_type=${isUpvote}`, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({})
    })
        .then(response => {
            if (!response.ok) throw new Error('Vote failed');
            return response.json();
        })
        .then(data => {
            console.log('Vote successful:', data);
        // Re-enable buttons after successful vote
            buttonContainer.style.opacity = '1';
            buttonContainer.style.pointerEvents = 'auto';
            pendingVotes.delete(hackathonId);
        })
        .catch(error => {
            console.error('Vote failed:', error);
            resetState();
        });
}

// Create a debounced version of handleVote
const debouncedHandleVote = debounce(handleVote, 300);

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
