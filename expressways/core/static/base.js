var setClassToTags = function(tagName, classNames) {
    var elements = document.getElementsByTagName(tagName);
    for (let idx = 0; idx < elements.length; idx++) {
        classNames.forEach(className => {
            elements[idx].className += className;
        });
    }
}

var startSpinner = function() {
    $('#spinner').modal('show');
}

var stopSpinner = function() {
    $('#spinner').modal('hide');
}

var displayError = function(msg) {
    if(msg !== undefined) {
       var message = document.querySelector('#error-msg');
       message.innerHTML = msg;
    }
    var card = document.querySelector('#error-card');
    card.style.display = 'block';
};

var getResults = function() {
    if (typeof result_url !== "undefined") {
        startSpinner();

        var xhttp = new XMLHttpRequest();
        xhttp.responseType = 'json';
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var res1 = document.getElementById('result-1');
                res1.innerHTML = xhttp.response.objective_1;

                var res2 = document.getElementById('result-2');
                res2.innerHTML = xhttp.response.objective_2;
                
                stopSpinner();
            } else if (this.readyState == 4 && this.status == 404) {
                setTimeout(getResults, 2000);
            } else if (this.readyState == 4) {
                stopSpinner();
                displayError(xhttp.response.msg);
            }
        };
        xhttp.open("GET", result_url, true);
        xhttp.send();
    }
};

var main = function() {
    setClassToTags('select', ['custom-select']);
    setClassToTags('input', ['form-control']);
    getResults();
}

window.onload = main;
