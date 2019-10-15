var value;
var getData = $.get("/boiler/analytics/" + value);
var jsonObjResults;

getData.done(function (results) {
    jsonObjResults = results;
    $('#avg_thinning').html(results["avg_thinning"]);
    $('#avg_thickness').html(results["avg_thickness"]);
    $('#last_year').html(results["last_year"]);
    $('#years').html(results["last_year"]);

    // make stacked bar chart
    makeStackedBarChart(results);

    // make pie chart
    makePieChart(results, results["last_year"]);
});

function makeStackedBarChart(results) {
    var ctx = document.getElementById('BarChart').getContext('2d');
    var stackedChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: results["stacked_bar"]["labels"],
            datasets: [
                {
                    label: "average thickness",
                    backgroundColor: "#28A745",
                    borderColor: '#fff',
                    data: results["stacked_bar"]["thickness"]
                },
                {
                    label: "average thinning",
                    backgroundColor: "#DC3545",
                    borderColor: "#fff",
                    data: results["stacked_bar"]["thinning"]
                }]
        },
        options: {
            legend: {
                display: true,
                position: 'bottom'
            },
            scales: {
                xAxes: [{
                    stacked: true
                }],
                yAxes: [{
                    ticks: {
                        min: 4.0
                    },
                    stacked: true
                }]
            }
        }
    })
}

function makePieChart(results, year) {
    var ctx = document.getElementById('PieChart').getContext('2d');
    var pieChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['below default', 'below minor', 'below major', 'below defect'],
            datasets: [{
                backgroundColor: ["#28A745", "#ffdb0b", "#FDB45C", "#DC3545"],
                borderColor: '#fff',
                data: results["pie"][year]
            }]
        },
        options: {
            legend: {
                position: 'bottom'
            }
        }
    })
}

// $("ul.pagination").on('click', 'a', function() {
//     var currentYear = $("#years")["0"].innerText;
//     var years = Object.keys(jsonObjResults["pie"]);
//
//     var choice = this;
//     if (this.getAttribute('aria-label') === "Previous") {
//         alert('<<<')
//     }
//     else if (this.getAttribute('aria-label') === "Next") {
//         alert(">>>")
//     }
//
//     // makePieChart(jsonObjResults, year);
// });

