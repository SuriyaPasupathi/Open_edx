<%page args="grade_summary, grade_cutoffs, graph_div_id, show_grade_breakdown=True, show_grade_cutoffs=True, **kwargs"/>

<%!
    import nh3
    import json
    import math
    import six

    from openedx.core.djangolib.js_utils import (
        dump_js_escaped_json, js_escaped_string
    )
%>

<script>
$(function () {

  function showTooltip(x, y, contents) {
      $("#tooltip").remove();
      var $tooltip_div = $('<div id="tooltip"></div>').css({
          position: 'absolute',
          display: 'none',
          top: y + 5,
          left: x + 15,
          border: '1px solid #000',
          padding: '4px 6px',
          color: '#fff',
          'background-color': '#222',
          opacity: 0.90
      });

      edx.HtmlUtils.setHtml(
          $tooltip_div,
          edx.HtmlUtils.HTML(contents)
      );

      edx.HtmlUtils.append(
          $('body'),
          edx.HtmlUtils.HTML($tooltip_div)
      );

      $('#tooltip').fadeIn(200);
  }

  /* -------------------------------- Grade detail bars -------------------------------- */

  <%
  colors = ["#b72121", "#600101", "#666666", "#333333"]
  categories = {}

  tickIndex = 1
  sectionSpacer = 0.25

  ticks = []
  bottomTicks = []
  detail_tooltips = {}
  droppedScores = []
  dropped_score_tooltips = []

  # Ensure section_breakdown exists and is a list
  section_breakdown = grade_summary.get('section_breakdown', [])
  if not isinstance(section_breakdown, list):
      section_breakdown = []

  for section in section_breakdown:

      if section.get('prominent', False):
          tickIndex += sectionSpacer

      if section['category'] not in categories:
          colorIndex = len(categories) % len(colors)
          categories[section['category']] = {
              'label': section['category'],
              'data': [],
              'color': colors[colorIndex]
          }

      categoryData = categories[section['category']]
      categoryData['data'].append([tickIndex, section['percent']])

      ticks.append([tickIndex, nh3.clean(section['label'], tags=set())])

      if section['category'] in detail_tooltips:
          detail_tooltips[section['category']].append(section['detail'])
      else:
          detail_tooltips[section['category']] = [section['detail']]

      if 'mark' in section:
          droppedScores.append([tickIndex, 0.05])
          dropped_score_tooltips.append(section['mark']['detail'])

      tickIndex += 1

      if section.get('prominent', False):
          tickIndex += sectionSpacer

  overviewBarX = tickIndex + sectionSpacer
  series = list(categories.values())

  extraColorIndex = len(categories)

  if show_grade_breakdown:
      # Ensure grade_breakdown exists and is a dict
      grade_breakdown = grade_summary.get('grade_breakdown', {})
      if not isinstance(grade_breakdown, dict):
          grade_breakdown = {}
      
      for section in six.itervalues(grade_breakdown):
          if section['percent'] > 0:
              if section['category'] in categories:
                  color = categories[section['category']]['color']
              else:
                  color = colors[extraColorIndex % len(colors)]
                  extraColorIndex += 1

              series.append({
                  'label': section['category'] + "-grade_breakdown",
                  'data': [[overviewBarX, section['percent']]],
                  'color': color
              })

              detail_tooltips[section['category'] + "-grade_breakdown"] = [
                  section['detail']
              ]

      ticks.append([overviewBarX, "Total"])
      tickIndex = overviewBarX + 1 + sectionSpacer

  # Ensure percent exists, default to 0
  totalScore = grade_summary.get('percent', 0)
  detail_tooltips['Dropped Scores'] = dropped_score_tooltips

  grade_cutoff_ticks = []
  if show_grade_cutoffs:
      grade_cutoff_ticks = [[1, "100%"], [0, "0%"]]
      descending_grades = sorted(grade_cutoffs, key=lambda x: grade_cutoffs[x], reverse=True)
      for grade in descending_grades:
          percent = grade_cutoffs[grade]
          grade_cutoff_ticks.append([percent, u"{0} {1:.0%}".format(grade, percent)])
  %>

  var series = ${ dump_js_escaped_json(series) };
  var ticks = ${ dump_js_escaped_json(ticks) };
  var detail_tooltips = ${ dump_js_escaped_json(detail_tooltips) };
  var droppedScores = ${ dump_js_escaped_json(droppedScores) };
  var grade_cutoff_ticks = ${ dump_js_escaped_json(grade_cutoff_ticks) };

  var yAxisTooltips = {};

  // Build yAxis tooltips
  for (var s = 0; s < series.length; s++) {
      for (var d = 0; d < series[s].data.length; d++) {
          var tx = series[s].data[d][0];

          if (yAxisTooltips[tx]) {
              yAxisTooltips[tx].push(detail_tooltips[series[s].label][d]);
          } else {
              yAxisTooltips[tx] = [detail_tooltips[series[s].label][d]];
          }

          for (var k = 0; k < droppedScores.length; k++) {
              if (tx === droppedScores[k][0]) {
                  yAxisTooltips[tx].push(detail_tooltips["Dropped Scores"][k]);
              }
          }
      }
  }

  for (var i = 0; i < grade_cutoff_ticks.length; i++) {
      grade_cutoff_ticks[i][1] = edx.HtmlUtils.joinHtml(
          edx.HtmlUtils.HTML('<span aria-hidden="true">'),
          grade_cutoff_ticks[i][1],
          edx.HtmlUtils.HTML('</span>')
      ).text;
  }

  series.push({
      label: "Dropped Scores",
      data: droppedScores,
      points: { symbol: "cross", show: true, radius: 3 },
      bars: { show: false },
      color: "#333"
  });

  var ascending_grades = grade_cutoff_ticks.map(function(el){ return el[0]; });
  ascending_grades.sort();

  var colors = ['#f8f9fa','#e9ecef','#dee2e6'];
  var markings = [];
  for (var i = 1; i < ascending_grades.length - 1; i++) {
      markings.push({
          yaxis: { from: ascending_grades[i], to: ascending_grades[i+1] },
          color: colors[(i-1) % colors.length]
      });
  }

  var options = {
      series: {
          stack: true,
          lines: { show: false },
          bars: {
              show: true,
              barWidth: 0.8,
              align: "center",
              lineWidth: 0,
              fill: 0.8
          }
      },
      xaxis: {
          tickLength: 0,
          min: 0,
          max: ${ dump_js_escaped_json(tickIndex - sectionSpacer) },
          ticks: function() {
              for (var i = 0; i < ticks.length; i++) {
                  var label = ticks[i][1];

                  var tickLabel = edx.HtmlUtils.joinHtml(
                      edx.HtmlUtils.HTML(i < ticks.length - 1 ? "<span aria-hidden='true'>" : "<span>"),
                      label,
                      edx.HtmlUtils.HTML("</span>")
                  );

                  var tooltips = yAxisTooltips[ticks[i][0]];
                  if (tooltips) {
                      for (var t = 0; t < tooltips.length; t++) {
                          tickLabel = edx.HtmlUtils.joinHtml(
                              tickLabel,
                              edx.HtmlUtils.HTML("<span class='sr'>"),
                              tooltips[t],
                              edx.HtmlUtils.HTML("<br></span>")
                          );
                      }
                  }

                  ticks[i][1] = tickLabel;
              }
              return ticks;
          },
          labelAngle: 90
      },
      yaxis: {
          ticks: grade_cutoff_ticks,
          min: 0,
          max: 1,
          labelWidth: 100
      },
      grid: {
          hoverable: true,
          clickable: true,
          borderWidth: 1,
          borderColor: "#707070",
          markings: markings
      },
      legend: { show: false }
  };

  var $grade_detail_graph = $("#${ graph_div_id | n, js_escaped_string }");
  $grade_detail_graph.width($grade_detail_graph.parent().width());

  if ($grade_detail_graph.length > 0) {
      var plot = $.plot($grade_detail_graph, series, options);

      % if show_grade_breakdown:
      var o = plot.pointOffset({
          x: ${ dump_js_escaped_json(overviewBarX) },
          y: ${ dump_js_escaped_json(totalScore) }
      });

      edx.HtmlUtils.append(
          $grade_detail_graph,
          edx.HtmlUtils.joinHtml(
              edx.HtmlUtils.HTML('<div class="overallGrade" style="position:absolute;left:'+(o.left-12)+'px;top:'+(o.top-20)+'px">'),
              edx.HtmlUtils.HTML('<span class="sr">'),
              gettext("Overall Score"),
              edx.HtmlUtils.HTML("<br></span>"),
              "${'{totalscore:.0%}'.format(totalscore=totalScore)}",
              edx.HtmlUtils.HTML("</div>")
          )
      );
      % endif
  }

  var previousPoint = null;

  $grade_detail_graph.bind("plothover", function(event, pos, item) {
      if (item) {
          if (previousPoint !== item.dataIndex + "-" + item.seriesIndex) {
              previousPoint = item.dataIndex + "-" + item.seriesIndex;

              if (detail_tooltips[item.series.label]) {
                  var tooltip = detail_tooltips[item.series.label][item.dataIndex];
                  showTooltip(item.pageX, item.pageY, tooltip);
              }
          }
      } else {
          $("#tooltip").remove();
          previousPoint = null;
      }
  });

});
</script>
