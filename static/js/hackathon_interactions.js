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
    const saveButtons = document.querySelectorAll(`[id$="${hackathonId}-save"]`);
    console.log(saveButtons)
    const isSavedBefore = saveButtons[0].classList.contains('bg-[#e5462e]');

    saveButtons.forEach(saveButton => {
        const isSaved = saveButton.classList.contains('bg-[#e5462e]');
        if (!isSaved) {
            saveButton.classList.remove('bg-white');
            saveButton.classList.add('bg-[#e5462e]', 'text-white');
        } else {
            saveButton.classList.remove('bg-[#e5462e]', 'text-white');
            saveButton.classList.add('bg-white');
        }
        saveButton.textContent = isSaved ? "Save" : "Saved";
    });


    saveButtons[0].textContent = isSavedBefore ? "Save" : "Saved";

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

    // when you just use the first one, it will only work for one side of the card, so the js wont work for the buttons on the back of the cards
    // this also makes sure the front cards and the back cards are in sync

    // Get UI elements
    const upButtons = document.querySelectorAll(`[id$="${hackathonId}-up"]`);
    const downButtons = document.querySelectorAll(`[id$="${hackathonId}-down"]`);
    const voteTexts = document.querySelectorAll(`[id$="${hackathonId}-vote-text"]`);

    const buttonContainer1 = upButtons[0].closest('div');
    const buttonContainer2 = upButtons[1].closest('div');

    // Add visual feedback that the vote is being processed
    buttonContainer1.style.opacity = '0.7';
    buttonContainer1.style.pointerEvents = 'none';
    buttonContainer2.style.opacity = '0.7';
    buttonContainer2.style.pointerEvents = 'none';
    pendingVotes.add(hackathonId);

    let method, voteChange;

    // If clicking upvote button
    upButtons.forEach((upButton, index) => {
        if (isUpvote) {
            if (upButton.classList.contains('fill-black')) {
                method = 'DELETE';
                voteChange = -1;
                upButton.classList.replace('fill-black', 'fill-white');
            } else if (downButtons[index].classList.contains('fill-black')) {
                method = 'POST';
                voteChange = 2;
                upButton.classList.replace('fill-white', 'fill-black');
                downButtons[index].classList.replace('fill-black', 'fill-white');
            } else {
                method = 'POST';
                voteChange = 1;
                upButton.classList.replace('fill-white', 'fill-black');
            }
        } else {
            if (downButtons[index].classList.contains('fill-black')) {
                method = 'DELETE';
                voteChange = 1;
                downButtons[index].classList.replace('fill-black', 'fill-white');
            } else if (upButton.classList.contains('fill-black')) {
                method = 'POST';
                voteChange = -2;
                downButtons[index].classList.replace('fill-white', 'fill-black');
                upButton.classList.replace('fill-black', 'fill-white');
            } else {
                method = 'POST';
                voteChange = -1;
                downButtons[index].classList.replace('fill-white', 'fill-black');
            }
        }
    });

    // because the class has been changed for both the front and back, either works 

    const originalUpButtonState = upButtons[1].classList.contains('fill-black') ? 'fill-black' : 'fill-white';
    const originalDownButtonState = downButtons[1].classList.contains('fill-black') ? 'fill-black' : 'fill-white';
    const originalVoteCount = parseInt(voteTexts[1].textContent);

    voteTexts[0].textContent = (originalVoteCount + voteChange).toString();
    voteTexts[1].textContent = (originalVoteCount + voteChange).toString();

    // Create a function to reset the UI state
    const resetState = () => {
        buttonContainer1.style.opacity = '1';
        buttonContainer1.style.pointerEvents = 'auto';

        buttonContainer2.style.opacity = '1';
        buttonContainer2.style.pointerEvents = 'auto';
        pendingVotes.delete(hackathonId);
        // first side
        voteTexts[0].textContent = originalVoteCount;
        upButtons[0].classList.remove('fill-black', 'fill-white');
        downButtons[0].classList.remove('fill-black', 'fill-white');
        upButtons[0].classList.add(originalUpButtonState);
        downButtons[0].classList.add(originalDownButtonState);

        // second side 
        voteTexts[1].textContent = originalVoteCount;
        upButtons[1].classList.remove('fill-black', 'fill-white');
        downButtons[1].classList.remove('fill-black', 'fill-white');
        upButtons[1].classList.add(originalUpButtonState);
        downButtons[1].classList.add(originalDownButtonState);
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
            // first side
            buttonContainer1.style.opacity = '1';
            buttonContainer1.style.pointerEvents = 'auto';

            // second side
            buttonContainer2.style.opacity = '1';
            buttonContainer2.style.pointerEvents = 'auto';
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
