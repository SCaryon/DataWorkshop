function draw_radviz (){

      var createVis = function(parent, width, height){
        var no_identifiers_data_dictionary, displayVars, springConstants, anchorPoints, tooltipVars, colorVar;
        var margins = {top:30, bottom:10, left: 10, right:10};
        var chartWidth = width - margins.left - margins.right;
        var chartHeight = height - margins.top - margins.bottom;
        var center = {x: chartWidth/2, y: chartHeight/2};
        var radius = Math.min(center.x, center.y);
        var color = d3.scale.category10();

        var svg = d3.select(parent)
          .append("svg")
          .attr({width:width, height:height})
            .attr('id', 'radviz_svg');

        var chart = svg.append("g")
          .attr("transform", "translate("+margins.left + "," + margins.top + ")");

        var chartBorder = svg.append("g")
          .attr("transform", "translate("+margins.left + "," + margins.top + ")")

        var angleToPoint = function(angle) {
          return {
            x: center.x + radius*Math.cos(angle),
            y: center.y + radius*Math.sin(angle)
          };
        };


        // vis() redraws the visualization.
        var vis = function(){

          // Create anchor points and style anchor points.
          anchorPoints = displayVars.map(function(d, i, arr){return angleToPoint((2*Math.PI/arr.length)*i);});
          var anchorCircles = chartBorder.selectAll("circle").data(anchorPoints);
          anchorCircles.exit().remove();
          anchorCircles.enter().append("circle");
          anchorCircles

          .attr({
            cx: function(d){return d.x},
            cy: function(d){return d.y},
            r: 3
          }).style("fill", "black");


          // Create anchor point labels.
          var offsetDistance = 7;

          var getTextX = function(d, i) {
            var xOffset = anchorPoints[i].x - center.x;
            var yOffset = anchorPoints[i].y - center.y;
            var angle = Math.atan2(yOffset, xOffset);
            return anchorPoints[i].x + offsetDistance*Math.cos(angle);
          };
          var getTextY = function(d, i) {
            var xOffset = anchorPoints[i].x - center.x;
            var yOffset = anchorPoints[i].y - center.y;
            var angle = Math.atan2(yOffset, xOffset);
            return anchorPoints[i].y + offsetDistance*Math.sin(angle);
          };
          var getTextAnchor = function(d, i) {
            var xOffset = anchorPoints[i].x - center.x;
            if (xOffset >= -0.1) return "start";
            return "end";
          }
          var getTextBaseline = function(d, i) {
            var yOffset = anchorPoints[i].y - center.y;
            if (yOffset > 0) return "hanging";
            return "alphabetic";
          }

          var anchorLabels = chartBorder.selectAll("text").data(displayVars);
          anchorLabels.exit().remove();
          anchorLabels.enter().append("text");
          anchorLabels.attr({
            x: getTextX,
            y: getTextY,
            "font-size": 10,
            "text-anchor": getTextAnchor,
            "alignment-baseline": getTextBaseline,
            "pointer-events": "none"
          }).text(function(d){return d});

          // Create circle for RadViz
          chartBorder.append("circle")
          .attr({
            cx: center.x,
            cy: center.y,
            r: radius,
            })
            .style("stroke", "black")    // set the line color
            .style("fill", "none");

          springConstants = displayVars.map(function(){return d3.scale.linear().range([0, 1]);});
          springConstants.forEach(function(element, index, array){
            element.domain(d3.extent(no_identifiers_data_dictionary, function(d){return +d[displayVars[index]];}));
          });

          if (colorVar) color.domain(allValuesOf(no_identifiers_data_dictionary, colorVar));

          var circles = chart.selectAll("circle").data(no_identifiers_data_dictionary);

          circles.exit().remove();

          circles.enter().append("circle")
              .data(data_dictionary)
              .on("mouseover", function(d,i) {

                  d3.select(this);
             key_name=new Array();
            for(var key in d){
                key_value=key+':'+d[key];
                key_name.push(key_value)
                }
            table=key_name.toString();
            table_n=table.replace(/,/g,'\n');
            svg.append("title").text('ID:'+ i +"\n"+ table_n).attr("id","Ttitle");
           d3.select(this)
           .attr("r", 8);

 })

.on("mouseout", function(d){
            d3.select("#Ttitle").remove();
            d3.select(this)
              .attr("r", 2);});

          var getPt = function(d) {
            var list = springConstants.map(function(element, index, array){

              return element(d[displayVars[index]]);}
              );
            var sum = list.reduce(function(prev, cur) {return prev + cur;});
            var pt = {x:0, y:0};
            for (var i = 0; i < anchorPoints.length; i++) {
              pt.x += (list[i]/sum)*anchorPoints[i].x
              pt.y += (list[i]/sum)*anchorPoints[i].y
            }
            return pt;
          }

          var getX = function(d) {return getPt(d).x; };

          var getY = function(d) {return getPt(d).y; };

          circles.transition()
          .duration(500)
          .attr({
            cx: getX,
            cy: getY,
            r: 2
          }).style("fill", function(d){
            if (!colorVar) {return "black";}
            return color(d[colorVar]);});


        };

        vis.loadData = function(data){
          no_identifiers_data_dictionary = data;
          return vis;
        }
        vis.setVars = function(value){
          if (!arguments.length) return displayVars;
          displayVars = value;
          return vis;
        }

        vis.setTooltipVars = function(value) {
          if (!arguments.length) return tooltipVars;
          tooltipVars = value;
          return vis;
        }

        vis.setColorVar = function(value) {
          if (!arguments.length) return colorVar;
          colorVar = value;
          return vis;
        }

        return vis;
      };

      var allValuesOf = function(data, variable) {
          var values = [];
          for (var i=0; i<data.length; i++){
            if (!values.includes(data[i][variable])) {
              values.push(data[i][variable]);
            }
          }
          return values;
        };

      var vis = createVis("#visDiv", 350,350);

 // Allow for user to adjust displayed variables and redraws vis as changes occur.
        var numericAttributeSelection = d3.select("#setVars").on("change", function(d){
          var selection = document.querySelectorAll('input[name="numericAttribute"]:checked');
          var variables = [];
          for (var i=0; i<selection.length; i++) {
            variables.push(selection[i].value);
          }
          vis.setVars(variables);
          vis();
        });

        var tooltipAttributeSelection = d3.select("#setTooltipDisplay").on("change", function(d){
          var selection = document.querySelectorAll('input[name="tooltipAttribute"]:checked');
          var variables = [];
          for (var i=0; i<selection.length; i++) {
            variables.push(selection[i].value);
          }

          vis.setTooltipVars(variables);
          vis();
        });

        var colorAttributeSelection = d3.select("#setColorVar").on("change", function(d){
          var selection = document.querySelector('input[name="colorAttribute"]:checked');
          var val = selection.value;
          if (val == "-1") vis.setColorVar(null);
          else vis.setColorVar(val);
          vis();
        })


            var isNumeric = function( n ) {
              return !isNaN(parseFloat(n)) && isFinite(n);
            }

            var addToTable = function(propertyList, parent, name, type) {

             var inputlist = d3.select(parent).selectAll("g").data(propertyList);

              inputlist.exit().remove();

              var groups = inputlist.enter().append("g");
              groups.append("input");
              groups.append("text");

              inputlist.select("input")
              .attr({
                "type":type,
                "value":function(d){return d},
                "label":function(d){return d},
                "name":name
              });

              inputlist.select("text").text(function(d){return d}).append("p");
            };

            var numericProps = [];
            for (property in no_identifiers_data_dictionary[0]) {
              if (isNumeric(no_identifiers_data_dictionary[0][property])) {
                numericProps.push(property);
              }
            }
            addToTable(numericProps, "#numeric", "numericAttribute", "checkbox");

            //adding all data attributes to tooltip table
            addToTable(Object.keys(no_identifiers_data_dictionary[0]), "#tooltip", "tooltipAttribute", "checkbox");

            //find categorical vars
            var categoricalVars = [];
            for (property in no_identifiers_data_dictionary[0]) {
              if (allValuesOf(no_identifiers_data_dictionary, property).length <= 20) {
                categoricalVars.push(property);
              }
            }

            addToTable(categoricalVars, "#colorGroup", "colorAttribute", "radio");

            vis.loadData(no_identifiers_data_dictionary);
            vis.setVars([]);
            vis.setTooltipVars([]);
            vis();
}
