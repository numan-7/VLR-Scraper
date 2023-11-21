$(document).ready(function(){
    // get username from url ^-^
    let urlParams = new URLSearchParams(window.location.search);
    let username = urlParams.get('username');
    if (username) {
        // disable submit button, show load spinner, hide 'Search' text, and show cancel button
        $("#scrapeBtn").prop("disabled", true);
        $("#cancelBtn").show();
        // poll every 2 seconds to see if its done....
        const checkInterval = setInterval( () => {
            $.ajax({
                type: "GET",
                url: "http://web:8000/check_scrapy_status/" + username,
                success: (response) =>  {
                    if (response.is_completed) {
                        clearInterval(checkInterval);
                        setTimeout( () => {
                            window.location.href = "/";
                        }, 150)
                    } 
                },
                error: () => {
                    $('#spinny').hide()
                    setTimeout( () => {
                        window.location.href = "/";
                    }, 150)
                }
            });
        }, 2000);
    }
});

$("#cancelBtn").click(() => {
    $("#cancelBtn").prop("disabled", true);
    let urlParams = new URLSearchParams(window.location.search);
    let username = urlParams.get('username');
    $("#header-content").text("Cancelling...");
    $.ajax({
        type: "POST",
        url: "http://localhost:8000/cancel_scrapy_task/" + username + "/",
        data: { 'username': username },
        success: () => {
            window.location.href = "/";
        }
    });
});