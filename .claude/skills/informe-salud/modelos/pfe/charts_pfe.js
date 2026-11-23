  function renderAll(){
    drawLines(document.getElementById('historyChart'), {
      labels:{{hist_years|json}},
      series:[{name:'Ingresos totales', color:PALETTE.navy, values:{{hist_tot|json}}},{name:'Sin COVID', color:PALETTE.blue, values:{{hist_xcov|json}}},{name:'Comirnaty + Paxlovid', color:PALETTE.gold, values:{{hist_cov|json}}}],
      valueFmt:function(v){ return '$'+v.toFixed(0)+'B'; }
    });

    var mixL = {{mix_labels|json}}, mixLoe = {{mix_loe|json}};
    drawHBars(document.getElementById('mixChart'), {
      labels:mixL,
      values:{{mix_values|json}},
      colors:mixLoe.map(function(b){ return b ? PALETTE.red : PALETTE.blue; }),
      padL:150,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawHBars(document.getElementById('loeChart'), {
      labels:{{loe_chart_labels|json}},
      values:{{loe_chart_values|json}},
      colors:[PALETTE.red,PALETTE.red,PALETTE.red,PALETTE.red,PALETTE.gold,PALETTE.gold,PALETTE.navy],
      padL:200,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawLines(document.getElementById('marginChart'), {
      labels:{{margin_q_labels|json}},
      series:[{name:'Margen bruto GAAP', color:PALETTE.navy, values:{{gm_q|json}}}],
      valueFmt:function(v){ return v.toFixed(1)+'%'; }
    });

    drawLines(document.getElementById('cashChart'), {
      labels:{{cash_years|json}},
      series:[{name:'Flujo operativo', color:PALETTE.navy, values:{{cash_ocf|json}}},{name:'Flujo de caja libre', color:PALETTE.blueLight, values:{{cash_fcf|json}}},{name:'Dividendos pagados', color:PALETTE.red, values:{{cash_div|json}}}]
    });

    var cL = {{comps_labels|json}};
    drawHBars(document.getElementById('compsChart'), {
      labels:cL,
      values:{{comps_values|json}},
      colors:cL.map(function(t){ return t === 'PFE' ? PALETTE.navy : (['BMY','SNY','GSK','NVO'].indexOf(t) >= 0 ? PALETTE.gold : PALETTE.pale); }),
      padL:60,
      valueFmt:function(v){ return v.toFixed(1)+'x'; }
    });

    drawVBars(document.getElementById('estChart'), {
      labels:['TTM (real)','2026E guía','2026E consenso','2027E consenso','2027E modelo'],
      values:{{est_values|json}},
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.blueLight,PALETTE.pale,PALETTE.gold],
      valueFmt:function(v){ return '$'+v.toFixed(1)+'B'; }
    });

    drawLines(document.getElementById('pathChart'), {
      labels:['2026','2027','2028','2029','2030','2031','2032','2033','2034','2035'],
      series:[{name:'Ingresos totales', color:PALETTE.navy, values:{{rev_path|json}}},{name:'Precipicio (5 productos)', color:PALETTE.red, values:{{rev_path_loe|json}}},{name:'Motores nuevos', color:PALETTE.gold, values:{{rev_path_new|json}}}],
      valueFmt:function(v){ return '$'+v.toFixed(0)+'B'; }
    });

    var sv = {{sotp_chart|json}};
    drawHBars(document.getElementById('sotpChart'), {
      labels:{{sotp_chart_labels|json}},
      values:sv.map(Math.abs),
      colors:sv.map(function(v){ return v < 0 ? PALETTE.red : PALETTE.blue; }),
      padL:210,
      valueFmt:function(v){ return '$'+v.toFixed(1)+'B'; }
    });

    drawVBars(document.getElementById('peChart'), {
      labels:{{fy_pe_chart_years|json}},
      values:{{fy_pe_chart|json}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.gold,PALETTE.gold,PALETTE.gold,PALETTE.navy,PALETTE.navy],
      valueFmt:function(v){ return v.toFixed(1)+'x'; }
    });

    drawRangeBars(document.getElementById('footballChart'), {
      labels:['M1: Suma de partes + rNPV','M2: Comparables','M3: Reversión histórica','M4: Consenso Wall Street'],
      domMin:0,
      ranges:{{ranges|json}},
      colors:[PALETTE.blue,PALETTE.blueLight,PALETTE.pale,PALETTE.gold],
      refLines:[{value:{{price|json}},color:PALETTE.red,label:'Mercado {{price|usd2}}'},{value:{{blend|json}},color:PALETTE.navy,label:'Blend {{blend|usd2}}'}],
      padL:190,
      valueFmt:function(v){ return '$'+v.toFixed(0); }
    });
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', renderAll);
  } else {
    renderAll();
  }
  var resizeTimer;
  window.addEventListener('resize', function(){
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(renderAll, 150);
  });
})();
</script>
<script src="_preview-gate.js" defer></script>
</body>
</html>
