function saveHackathon(event, hackathonId) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();


    xhr.open('POST', `/hackathons/${hackathonId}/save`, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.send(JSON.stringify({}));
}

function voteHackathon(event, hackathonId, vote_state) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();

    const upButton = document.getElementById(`${hackathonId}-up`);
    const downButton = document.getElementById(`${hackathonId}-down`);
    const upText = document.getElementById(`${hackathonId}-up-text`);
    const downText = document.getElementById(`${hackathonId}-down-text`);


    if (vote_state === 'true') {
        // Check if the down button is active
        if (downButton.classList.contains('fill-black')) {
            downButton.classList.remove('fill-black');
            downButton.classList.add('fill-white');
            downText.textContent = parseInt(downText.textContent) - 1;
        }

        // Activate the up button
        upButton.classList.add('fill-black');
        upButton.classList.remove('fill-white');
        upText.textContent = parseInt(upText.textContent) + 1;
    } else {
        // Check if the up button is active
        if (upButton.classList.contains('fill-black')) {
            upButton.classList.remove('fill-black');
            upButton.classList.add('fill-white');
            upText.textContent = parseInt(upText.textContent) - 1;
        }

        // Activate the down button
        downButton.classList.add('fill-black');
        downButton.classList.remove('fill-white');
        downText.textContent = parseInt(downText.textContent) + 1;
    }

    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log(`${response.hackathon.id} Hackathon ${response.hackathon.name} saved successfully`);
            }
            else {
                console.log(`ERROR: ${response.hackathon.id} Hackathon ${response.hackathon.name} saved unsuccessfully`);
            }
        }
    };

    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                console.log(`saved successfully`);
            }
            else {
                console.log(`saved unsuccessfully`);
            }
        }
    };

    xhr.open('POST', `/hackathons/${hackathonId}/vote?vote_state=${vote_state}`, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.send(JSON.stringify({}));
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