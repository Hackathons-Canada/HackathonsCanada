


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
    const voteText = document.getElementById(`${hackathonId}-vote-text`);

    console.log(vote_state)
    if (vote_state === 'true') {

        if (downButton.classList.contains('fill-black')) {
            downButton.classList.remove('fill-black');
            downButton.classList.add('fill-white');
            upButton.classList.remove('fill-white');
            upButton.classList.add('fill-black');
            console.log('1')
            voteText.textContent = parseInt(voteText.textContent) + 2;
        }
        else if (upButton.classList.contains('fill-black')) {
            upButton.classList.add('fill-white');
            upButton.classList.remove('fill-black');
            console.log('2')
            voteText.textContent = parseInt(voteText.textContent) - 1;
        }
        else {
            upButton.classList.remove('fill-white');
            upButton.classList.add('fill-black');
            voteText.textContent = parseInt(voteText.textContent) + 1;
            console.log('3')
        }
        console.log('running')



    } else {
        console.log('false')
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
        }
        else {
            downButton.classList.remove('fill-white');
            downButton.classList.add('fill-black');
            voteText.textContent = parseInt(voteText.textContent) - 1;
        }


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