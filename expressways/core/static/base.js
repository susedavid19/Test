var element_class_obj = {
    'select': 'custom-select',
    'input': 'form-control'
};

var setClassToTags = function() {
    for (const [element, className] of Object.entries(element_class_obj)) {
        var elements = document.getElementsByTagName(element);
        for (let idx = 0; idx < elements.length; idx++) {
            if (elements[idx].className.split(' ').indexOf(className) == -1) {
                elements[idx].className += ' ' + className;
            }
        }
    }
}

var startSpinner = function() {
    $('#spinner').modal('show');
}

var stopSpinner = function() {
    $('#spinner').modal('hide');
}

var displayError = function(msg) {
    if(msg) {
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
        xhttp.open("GET", result_url, true);
        xhttp.send();
        xhttp.responseType = 'json';
        xhttp.timeout = 5000;

        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var res1 = document.getElementById('result-1');
                res1.innerHTML = xhttp.response.objective_1;

                var res2 = document.getElementById('result-2');
                res2.innerHTML = xhttp.response.objective_2;
                
                setTimeout(stopSpinner, 500);
            } else if (this.readyState == 4 && this.status != 200) {
                setTimeout(stopSpinner, 500);
                displayError(this.statusText);
            }
        };

        xhttp.ontimeout = function() {
            setTimeout(stopSpinner, 500);
            displayError('Connection timed out!');
        }
    }
};

var main = function() {
    setClassToTags();
    getResults();
}

window.onload = main;
