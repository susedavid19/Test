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
                document.getElementById('result-incident').innerHTML = xhttp.response.objective_incident;

                document.getElementById('result-pti').innerHTML = xhttp.response.objective_pti;

                document.getElementById('result-journey').innerHTML = xhttp.response.objective_journey;
                
                document.getElementById('result-speed').innerHTML = xhttp.response.objective_speed;
                
                document.getElementById('result-exp-incident').innerHTML = xhttp.response.objective_exp_incident;
                
                document.getElementById('result-exp-pti').innerHTML = xhttp.response.objective_exp_pti;

                document.getElementById('result-exp-journey').innerHTML = xhttp.response.objective_exp_journey;

                document.getElementById('result-exp-speed').innerHTML = xhttp.response.objective_exp_speed;

                setTimeout(stopSpinner, 500);
            } else if (this.readyState == 4 && this.status == 404) {
                setTimeout(getResults, 2000);
            } else if (this.readyState == 4) {
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

var getSubOccurrences = function() {
    $('#id_occurrence').change(function () {
        let url = $('#configurationForm').attr('data-sub-occurrences-url');
        let occurrence_id = $(this).val();

        $.ajax({
            url: url,
            data: {
                'occurrence': occurrence_id
            },
            success: function(data) {
                $('#id_sub_occurrence').html(data); 
            }
        })
    });
}

var main = function() {
    setClassToTags();
    getResults();
    getSubOccurrences();
}

window.onload = main;
