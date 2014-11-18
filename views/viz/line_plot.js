
function d3_plot_init() {
    svg = svg.append("svg")
        .attr("width",w)
        .attr("height",h);
    console.log(svg);
    nv.addGraph(function() {

        chart = nv.models.lineChart()
                    .margin({left: 100})  //Adjust chart margins to give the x-axis some breathing room.
                    .useInteractiveGuideline(true)  //We want nice looking tooltips and a guideline!
                    .transitionDuration(350)  //how fast do you want the lines to transition?
                    .showLegend(true)       //Show the legend, allowing users to turn on/off line series.
                    .showYAxis(true)        //Show the y-axis
                    .showXAxis(true)        //Show the x-axis

        chart.xAxis.orient("bottom")
                 .tickFormat(function(d) { 
                            return d3.time.format('%d %b %H:%M')(new Date(d)) 
                            });

        chart.yAxis.tickFormat(d3.format('.00f'));
    //.axisLabel(data.algorithm.title)

        //We want to show shapes other than circles.
        //chart.scatter.onlyCircles(false);

        svg.datum(data.data)
            .call(chart);
        //console.log(data.tags);

        //nv.utils.windowResize(chart.update);
        nv.utils.windowResize(function() { chart.update() });
        //$("#scatter-plot-stats").append("<div id='tags_label'> Tags: " +data.tags.join([separator = ', '])+ "</div>");
        is_initialised=true

        return chart;
    });
}

function d3_plot_redraw(){
    console.log('calling redraw');
    d3.select("#nv3d-daylogger svg").empty();
    d3.select("#nv3d-daylogger svg")
        .datum(data.data)
        .call(chart);
    nv.utils.windowResize(chart.update);
    //$("#scatter-plot-stats #tags_label").text("Tags: " +data.tags.join([separator = ', ']));
}
