$(document).ready(function(){
    // get username from url ^-^
    let urlParams = new URLSearchParams(window.location.search);
    let username = urlParams.get('username');
    if (username) {
        // disable submit button, show load spinner, hide 'Search' text, and show cancel button
        $("#scrapeBtn").prop("disabled", true);
        $("#cancelBtn").show();
        const csrftoken = getCookie("csrftoken");
        // poll every 2 seconds to see if it's done...
        const checkInterval = setInterval(() => {
            fetch(`http://localhost:8000/check_scrapy_status/${username}/`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_completed) {
                    clearInterval(checkInterval);
                    window.location.href = "/";
                }
            })
            .catch(error => {
                console.error("Fail", error);
                $('#spinny').hide();
                setTimeout(() => {
                    window.location.href = "/";
                }, 150);
            });
        }, 2000);        
    }
});

$("#cancelBtn").click(() => {
    $("#cancelBtn").prop("disabled", true);
    $("#header-content").text("Cancelling...");
    let urlParams = new URLSearchParams(window.location.search);
    let username = urlParams.get('username');
    $.ajax({
        type: "POST",
        url: "http://localhost:8000/cancel_scrapy_task/" + username + "/",
        data: { 'username': username },
        success: () => {
            window.location.href = "/";
        }
    });
});

// JavaScript function to get cookie by name; retrieved from https://docs.djangoproject.com/en/3.1/ref/csrf/
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}