
function flipCard(hackathonId) {
    const card1 = document.getElementById(`${hackathonId}-card-front`);
    const card2 = document.getElementById(`${hackathonId}-card-back`);
    card1.classList.toggle("flipped")
    card2.classList.toggle("flipped")
}

function saveHackathon(event, hackathonId) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();
    const saveButton = document.getElementById(`${hackathonId}-save`);
    if (saveButton.classList.contains('bg-[#e5462e]')) {
        saveButton.classList.remove('bg-[#e5462e]');
        saveButton.classList.remove('text-white');
        saveButton.classList.add('bg-white');
        saveButton.textContent = "Save";
    }
    else {
        saveButton.classList.add('bg-[#e5462e]');
        saveButton.classList.add('text-white');
        saveButton.classList.remove('bg-white');
        saveButton.textContent = "Saved";
    }
    xhr.open('POST', `/hackathons/${hackathonId}/save`, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.send(JSON.stringify({}));
}

function cancelLoginPop(){
    const popup = document.getElementById('login-popup');
    popup.classList.add('hidden');
    popup.classList.remove('flex');
}

function addLoginPop(){
    const popup = document.getElementById('login-popup');
    popup.classList.remove('hidden');
    popup.classList.add('flex');
}


function voteHackathon(event, hackathonId, vote_state) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();

    const upButton = document.getElementById(`${hackathonId}-up`);
    const downButton = document.getElementById(`${hackathonId}-down`);
    const voteText = document.getElementById(`${hackathonId}-vote-text`);

    var state = 'POST'


    if (vote_state === 'true') {

        if (downButton.classList.contains('fill-black')) {
            downButton.classList.remove('fill-black');
            downButton.classList.add('fill-white');
            upButton.classList.remove('fill-white');
            upButton.classList.add('fill-black');
            voteText.textContent = parseInt(voteText.textContent) + 2;

        }
        else if (upButton.classList.contains('fill-black')) {
            upButton.classList.add('fill-white');
            upButton.classList.remove('fill-black');
            voteText.textContent = parseInt(voteText.textContent) - 1;
            state = "DELETE"
        }
        else {
            upButton.classList.remove('fill-white');
            upButton.classList.add('fill-black');
            voteText.textContent = parseInt(voteText.textContent) + 1;

        }



    } else {
        if (upButton.classList.contains('fill-black')) {
            upButton.classList.remove('fill-black');
            upButton.classList.add('fill-white');
            downButton.classList.remove('fill-black');
            downButton.classList.remove('fill-white');
            downButton.classList.add('fill-black');
            voteText.textContent = parseInt(voteText.textContent) - 2;


        }
        else if (downButton.classList.contains('fill-black')) {
            downButton.classList.remove('fill-black');
            downButton.classList.add('fill-white');
            voteText.textContent = parseInt(voteText.textContent) + 1;
            state = "DELETE"
        }
        else {
            downButton.classList.remove('fill-white');
            downButton.classList.add('fill-black');
            voteText.textContent = parseInt(voteText.textContent) - 1;

        }


    }

    xhr.open(state, `/hackathons/${hackathonId}/vote/?vote_type=${vote_state}`, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.send(JSON.stringify({}));

    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log('successful:', response);
            } else {
                console.error('failed:', xhr.status);
            }
        }
    };
}


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}