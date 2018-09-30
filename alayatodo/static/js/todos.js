(function() {
    var d = document.getElementById('desc-input');
    var b = document.getElementById('add-btn');
    
    function validate() {
        b.disabled = d.value.length == 0;
    }
    
    validate();
    
    d.addEventListener("input", function() {
        validate();
    }, false);
})()
