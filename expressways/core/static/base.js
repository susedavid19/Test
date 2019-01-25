document.addEventListener("DOMContentLoaded", function() {
  var elems = document.querySelectorAll(".collapsible");
  var options = {};
  var instances = M.Collapsible.init(elems);
});

document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems);
});

document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.autocomplete');
    let options = {
      data: {
        "This One": null,
        "A Different One": null,
        "Another One": null
      },
    }
    var instances = M.Autocomplete.init(elems, options);
});

document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.modal');
    var instances = M.Modal.init(elems, {'dismissible': false});
});


var startSpinner = function() {
    var elem = document.querySelector('#spinner');
    var instance = M.Modal.getInstance(elem);
    instance.open();
};

var stopSpinner = function() {
    var elem = document.querySelector('#spinner');
    var instance = M.Modal.getInstance(elem);
    instance.close();
};

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

window.onload = getResults;
