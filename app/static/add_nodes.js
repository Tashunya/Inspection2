var submit = document.getElementById('submit');
var input = document.getElementsByTagName("input");
var jsInput = document.getElementById("final_structure");


var submit_form = document.getElementsByTagName('form')[0];

submit_form.addEventListener('submit', function (event){
    jsInput.value = "started"

    var jsonObject = json.parse(text_json)

    jsInput.value = "started 2"

    for(var i=0; i<input.length; i++) {
        path = input[i].name.split('_');
        current_obj = jsonObject
        path.forEach(function(elem){
             if(elem === "Elements"){
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
                    current_obj = current_obj[elem-1].children
                }
             }
        });
    }
    jsInput.value = json.stringify(jsonObject)

    return true;
});

