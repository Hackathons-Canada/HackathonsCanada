function saveHackathon(event, hackathonId) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();


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

    xhr.open('POST', `/hackathons/${hackathonId}/save`, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.send(JSON.stringify({}));
}

function upvoteHackathon(event, hackathonId) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();


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

    xhr.open('POST', `/hackathons/${hackathonId}/save`, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken'));
    xhr.send(JSON.stringify({}));
}

function downvoteHackathon(event, hackathonId) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();


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

    xhr.open('POST', `/hackathons/${hackathonId}/save`, true);
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