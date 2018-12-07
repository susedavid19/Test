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
