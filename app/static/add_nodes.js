var input = $("td input");
var default_json;


$('#submit').click( function() {
    $.get("/boiler/default_structure", function(data) {
        default_json = data;

        updateStructure(); // change structure in default_json

        $.ajax({ // send updated structure to Flask view add_nodes
            async: false,
            type: "POST",
            contentType: "application/json",
            url: addNodesUrl,
            data: JSON.stringify(default_json),
            dataType: "json"
        });



        window.location.href = '/boiler/' + boilerId;

    }, "json");

    return false;

});


function updateStructure(){ // change structure in default_json
    for(var i=0; i<input.length; i++) {
        current_obj = default_json.structure;
        var path = input[i].name.split('_'); // ["1", "2", "3", "Elements"]
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