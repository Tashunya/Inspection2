var jsonobj;

// choose element

lvlOne = $("select[id='level_1']");
lvlTwo = $("select[id='level_2']");

$('#block').change( function() {
    $.get("/boiler/children/" + this.value, levelOneChoice, "json");
});

function levelOneChoice(childrenArray) {
    lvlOne.find("option").remove();
    lvlTwo.find("option").remove();
    options = addOptions(childrenArray);
    lvlOne.append(options);
}


$('#level_1').change( function() {
    $.get("/boiler/children/" + this.value, levelTwoChoice, "json");
});

function levelTwoChoice(childrenArray) {
    lvlTwo.find("option").remove();
    options = addOptions(childrenArray);
    lvlTwo.append(options);
}

function addOptions(childrenArray) {
    var options = "<option selected value='__None'></option>";
    for(var i = 0; i < childrenArray.length; i++) {
        options += "<option value='" + childrenArray[i].id + "'>"
            + childrenArray[i].node_name + "</option>";
    }
    return options
}


// when element is chosen

$('#chooseNode').click( function() {

    var chosenNode = $('#level_2').val();

    $.get("/boiler/table/" + chosenNode, chooseElement, "json");

    function chooseElement(tableArray) {
        // set upload link
        link = "/boiler/upload?parent_id=" + chosenNode;
        $("a#upload").attr("href", link);

        if (Object.entries(tableArray).length === 0) {
            console.log("No data!");
            changeElementName();
            emptyData();
        } else {
            jsonobj = tableArray;
            // change title with element name
            changeElementName();
            // add analytics button
            addAnalyticsBtn();
            // create button group with years
            createBtnGroup(tableArray);
            // find last year
            var measuresYears = Object.keys(tableArray);
            var lastYear = measuresYears[measuresYears.length-1];
            var lastYearData = tableArray[lastYear];
            // show table with data for last year
            createTable(lastYearData)
        }
    }
});

// for empty data
function emptyData() {
    $("tbody").find("tr").remove();
    $(".btn-group").find("button").remove();
    $("div[colspan]").html("No data for chosen node. Please upload the data.")
}

// change title with element name
function changeElementName() {
    var block = $('#block option:selected').text();
    var level_1 = $('#level_1 option:selected').text();
    var level_2 = $('#level_2 option:selected').text();
    $('#elementName').html(block + '/' + level_1 + '/' + level_2)
}

// add analytics button
function addAnalyticsBtn() {
    var chosenNode = $('#level_2').val();
    var link = "/boiler/analytics?parent_id=" + chosenNode;
    var analyticsBtn = ' <a class="btn btn-warning btn-sm" href="' + link + '"> Analytics</a>';
    $('#elementName').append(analyticsBtn)
}

// create button group with years
function createBtnGroup(tableArray) {
    var btnGroup = $(".btn-group");
    btnGroup.find("button").remove();
    var measuresYears = Object.keys(tableArray);
    for(var i = 0; i < measuresYears.length; i++) {
        var button = '<button type="button" class="btn btn-outline-info" value="'
            + measuresYears[i] + '">' + measuresYears[i] + '</button>';
        btnGroup.append(button);
    }
}

// when change years
$("div.btn-group").on('click', 'button', function() {
    //    this.className += " active"
    var year = this.textContent;
    var data = jsonobj[year];
    createTable(data)
});

// show table with data
function createTable(data) {
    var results = $("tbody");
    results.find("tr").remove();
    data.forEach(function(element, index) {
        var newRow = '<tr><td>' + (index+1) + '</td><td>';
        var columns = ['node_name','value', 'default', 'minor', 'major', 'defect'];
        columns.forEach(function(column, num) {
            newRow += element[column] + ((num==columns.length-1) ? '</td></tr>' : '</td><td>')
        });
        results.append(newRow);
    });
}

function addColor() {
}

// change active button