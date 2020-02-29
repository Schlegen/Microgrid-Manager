var chart_battery;
var chart_net_demand;

function draw_charts (){ $.getJSON('/data',
  function draw_charts (response) {
    window.chart_battery = Highcharts.chart('container1', {
    chart: {
      zoomType: 'x'
    },
    title: {
      text: 'Remplissage de la batterie'
    },
    subtitle: {
      text: document.ontouchstart === undefined ?
        'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
    },
    xAxis: {
      type: 'datetime'
    },
    yAxis: {
      title: {
        text: 'Remplissage de batterie en kWh'
      }
    },
    legend: {
      enabled: false
    },
    plotOptions: {
      area: {
        fillColor: {
          linearGradient: {
            x1: 0,
            y1: 0,
            x2: 0,
            y2: 1
          },
          stops: [
            [0, Highcharts.getOptions().colors[0]],
            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
          ]
        },
        marker: {
          radius: 2
        },
        lineWidth: 1,
        states: {
          hover: {
            lineWidth: 1
          }
        },
        threshold: null
      }
    },

    series: [{
      type: 'area',
      name: 'Remplissage de la batterie passé',
      data: response.battery.slice(9*48, 14*48)
    },{
      type: 'area',
      name: 'Prévision du remplissage de la batterie',
      data: response.battery.slice(14*48, 19*48)
    }

  ]
  });
    window.chart_net_demand = Highcharts.chart('container2', {
    chart: {
      zoomType: 'x'
    },
    title: {
      text: 'Demande nette'
    },
    subtitle: {
      text: document.ontouchstart === undefined ?
        'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
    },
    xAxis: {
      type: 'datetime'
    },
    yAxis: {
      title: {
        text: 'Demande nette en kWh'
      }
    },
    legend: {
      enabled: false
    },
    legend: {
      enabled: false
    },
    plotOptions: {
      area: {
        fillColor: {
          linearGradient: {
            x1: 0,
            y1: 0,
            x2: 0,
            y2: 1
          },
          stops: [
            [0, Highcharts.getOptions().colors[0]],
            [1, Highcharts.Color(Highcharts.getOptions().colors[0]).setOpacity(0).get('rgba')]
          ]
        },
        marker: {
          radius: 2
        },
        lineWidth: 1,
        states: {
          hover: {
            lineWidth: 1
          }
        },
        threshold: null
      }
    },

    series: [{
      type: 'area',
      name: 'Demande nette passée',
      data: response.net_demand.slice(9*48, 14*48)
    },{
      type: 'area',
      name: 'Prévision de la demande nette',
      data: response.net_demand.slice(14*48, 19*48)
    }
    ]
    });
  }
);
}

function update_chart_net_demand (data_to_draw) {
  window.chart_net_demand.series[0].setData(data_to_draw.slice(9*48, 14*48));
  window.chart_net_demand.series[1].setData(data_to_draw.slice(14*48, 19*48));
}


function update_chart_battery (data_to_draw) {
  window.chart_battery.series[0].setData(data_to_draw.slice(9*48, 14*48));
  window.chart_battery.series[1].setData(data_to_draw.slice(14*48, 19*48));
}

//----------------------------- treating the svg -------------------------------

function set_triangle_sense (data) {
  let triangles = document.getElementsByClassName('triangle');

  let solar_pannels = document.getElementsByClassName('solar_pannel');
  let batter = document.getElementsByClassName('batter');
  let house = document.getElementsByClassName('house');
  let antenna = document.getElementsByClassName('antenna');

  let charging = data.battery[14*48 - 1][1] - data.battery[14*48 - 2][1];
  let imported = data.imported; // gérer en Python
  // let loss1 = (1/0.95 - 1) * charging;
  // let loss2 = 0.05 * charging;
  let loss = 0
  if (charging > 0) {
    loss = (1/0.95 - 1) * charging;
  } else {
    loss = 0.05 * charging;
  }
  console.log("charge", charging, "import", imported, "demand", data.demand, "generation", data.generation, "loss", loss, "balance", -charging + imported - data.demand + data.generation);

// ------------- arrows of the cable of battery --------------------------------
  if (charging > 0) {
    [].forEach.call(batter,
      function(elem, i, a) {
        elem.style.transform = "rotate(0.5turn)";
        elem.style.fill = '#00FF00';
      }
    );
  } else if (charging == 0) {
    [].forEach.call(batter,
      function(elem, i, a) {
        elem.style.transform = "rotate(0)";
        elem.style.fill = '#606063';
      }
    );
  } else {
    [].forEach.call(batter,
      function(elem, i, a) {
        elem.style.transform = "rotate(0.5turn)";
        elem.style.fill = '#00FF00';
      }
    );
  }

  // ----------------------- arrow of the delivery cable -----------------------

  if (imported < 0) {
    [].forEach.call(antenna,
      function(elem, i, a) {
        elem.style.transform = "rotate(0.5turn)";
        elem.style.fill = '#00FF00';
      }
    );
  } else if (imported == 0) {
    [].forEach.call(antenna,
      function(elem, i, a) {
        elem.style.transform = "rotate(0)";
        elem.style.fill = '#606063';
      }
    );
  } else {
    [].forEach.call(antenna,
      function(elem, i, a) {
        elem.style.transform = "rotate(0.5turn)";
        elem.style.fill = '#00FF00';
      }
    );
  }

  // ----------------------- used by the house ---------------------------------
  $("#tspan330-3").text(String(Math.round(data.demand *100) / 100.0 ).concat(" kWh"));

  //------------------------ charged by the battery ----------------------------
  $("#tspan330-3-8-9").text(String(Math.round(charging *100) / 100.0 ).concat(" kWh"));

  //------------------------ imported from the outside -------------------------
  $("#tspan330").text(String(Math.round(imported *100) / 100.0 ).concat(" kWh"));

  //------------------------ produced by the solar pannel ----------------------
  $("#tspan330-3-8").text(String(Math.round(data.generation *100) / 100.0 ).concat(" kWh"));



// ---------- arrows in direction of the delivery point ------------------------
  if (imported < 0) {
    [].forEach.call(batter,
      function(elem, i, a) {
        elem.style.transform = "rotate(0.5turn)";
      }
    );
  }

}


// ------------------- update ---------------------------------------------
function update_charts (){
  $.getJSON('/data',
    function (response) {
      update_chart_net_demand(response.net_demand);
      update_chart_battery(response.battery);
      set_triangle_sense(response);
    });
}




draw_charts();
window.setInterval(update_charts, 8000);