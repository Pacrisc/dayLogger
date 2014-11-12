
function d3_plot_init() {
    svg = svg.append("svg")
        .attr("width",w)
        .attr("height",h);
    nv.addGraph(function() {

    chart = nv.models.scatterChart()
                .showDistX(true)    //showDist, when true, will display those little distribution lines on the axis.
                .showDistY(true)
                //.showLegend(false)
                .transitionDuration(350)
                .color(d3.scale.category10().range())
                .size(1).sizeRange([50,50]);;

  //Configure how the tooltip looks.
  //chart.tooltipContent(function(key) {
  //    return  key ;
  //});
    chart.tooltipContent(function(key, x, y, obj) {
        //console.log(arguments);
        return '<div> Event: ' + key +'<br /> Item: <em>' +  obj.point.label + '</em></div>';
    });

    chart.xAxis.orient("bottom")
             .tickFormat(function(d) { 
                        return d3.time.format('%d %b %H:%M')(new Date(d)) 
                        });

    chart.yAxis.tickFormat(d3.format('.00f'));

    //We want to show shapes other than circles.
    chart.scatter.onlyCircles(false);

    svg.datum(data.data)
        .call(chart);
    console.log(data.tags);

    nv.utils.windowResize(chart.update);

    $("#scatter-plot-stats").append("<div id='tags_label'> Tags: " +data.tags.join([separator = ', '])+ "</div>");
    is_initialised=true

    return chart;
});
}

function d3_plot_redraw(){
    console.log('calling redraw');
    d3.select("#scatter-plot-stats svg").empty();
    d3.select("#scatter-plot-stats svg")
        .datum(data.data)
        .call(chart);
    nv.utils.windowResize(chart.update);
    $("#scatter-plot-stats #tags_label").text("Tags: " +data.tags.join([separator = ', ']));
}
