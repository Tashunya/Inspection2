var value;

var getData = $.get("/boiler/analytics/" + value);

getData.done(function (results) {
  $('#avg_thinning').html(results["avg_thinning"]);
  $('#avg_thickness').html(results["avg_thickness"]);


  // make stacked bar chart
  var ctx = document.getElementById('BarChart').getContext('2d');
  var stackedChart = new Chart(ctx, {
      // The type of chart we want to create
      type: 'bar',
      // The data for our dataset
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
      // Configuration options go here
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
  });

  // make pie chart
  var ctx = document.getElementById('PieChart').getContext('2d');
  var pieChart = new Chart(ctx, {
     type: 'pie',
     data: {
        labels: ['below default', 'below minor', 'below major', 'below defect'],
        datasets: [{
           backgroundColor: ["#28A745", "#ffdb0b", "#FDB45C", "#DC3545"],
           borderColor: '#fff',
           data: results["pie"]["2018"]
        }]
       },
     options: {
        legend: {
           position: 'bottom'
        }
     }
  });
});

