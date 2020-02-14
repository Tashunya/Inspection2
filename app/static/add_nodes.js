let input = $("td input");


$('#submit').click( function() {
    $.get("/api/v1/default_structure", function(data) {

        updateStructure(data); // change structure in default_json

        $.ajax({ // send updated structure to Flask view add_nodes
            async: false,
            type: "POST",
            contentType: "application/json",
            url: window.location.pathname,
            data: JSON.stringify(data),
            dataType: "json"
        });

        window.location.href = '/';

    }, "json");

    return false;
});


function updateStructure(data){ // change structure in default_json
    for(var i=0; i<input.length; i++) {
        let current_obj = data.structure;

        let path = input[i].name.split('_'); // ["1", "2", "3", "Elements"]

        path.forEach(function(elem){
             if(elem === "Elements") {
                current_obj.Elements = input[i].value
             }
             if(elem === "Points") {
                 current_obj.Points = input[i].value
             }

             else {
                if (current_obj.hasOwnProperty('children') === false) {
                    current_obj = current_obj[elem-1]
                }
                else {
                    current_obj = current_obj.children[elem-1]
                }
             }
        });
    }
}