  function P(names){ return names.map(function(n){ return PALETTE[n]; }); }
  function renderAll(){
    drawVBars(document.getElementById('historyChart'), {
      labels:['FY2021','FY2022','FY2023','FY2024','FY2025','TTM'],
      values:{{ch.hist|json}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return '$'+v.toFixed(1); }
    });

    drawHBars(document.getElementById('mixChart'), {
      labels:{{ch.mix_l|json}},
      values:{{ch.mix_v|json}},
      colors:P({{ch.mix_c|json}}),
      padL:180,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawHBars(document.getElementById('mtChart'), {
      labels:{{ch.mt_l|json}},
      values:{{ch.mt_v|json}},
      colors:P({{ch.mt_c|json}}),
      padL:170,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawHBars(document.getElementById('loeChart'), {
      labels:{{ch.loe_l|json}},
      values:{{ch.loe_v|json}},
      colors:P({{ch.loe_c|json}}),
      padL:170,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawLines(document.getElementById('prodChart'), {
      labels:['3T2025','4T2025','1T2026','2T2026','3T2026'],
      series:[{name:'Darzalex', color:PALETTE.navy, values:{{prod_q.dara|json}}},{name:'Tremfya', color:PALETTE.blue, values:{{prod_q.trem|json}}},{name:'Stelara', color:PALETTE.red, values:{{prod_q.ste|json}}},{name:'Carvykti', color:PALETTE.gold, values:{{prod_q.car|json}}}]
    });

    drawLines(document.getElementById('marginChart'), {
      labels:['3T2025','4T2025','1T2026','2T2026','3T2026'],
      series:[{name:'Margen bruto', color:PALETTE.navy, values:{{ch.gm|json}}},{name:'Mktg., ventas y adm.', color:PALETTE.blueLight, values:{{ch.sga|json}}},{name:'I+D', color:PALETTE.gold, values:{{ch.rd|json}}}],
      valueFmt:function(v){ return v.toFixed(1)+'%'; }
    });

    drawLines(document.getElementById('cashChart'), {
      labels:['2022','2023','2024','2025','TTM'],
      series:[{name:'Flujo operativo', color:PALETTE.navy, values:{{ch.cf_ocf|json}}},{name:'Capex', color:PALETTE.red, values:{{ch.cf_capex|json}}},{name:'Flujo de caja libre', color:PALETTE.blueLight, values:{{ch.cf_fcf|json}}}]
    });

    drawHBars(document.getElementById('compsChart'), {
      labels:{{ch.comps_l|json}},
      values:{{ch.comps_v|json}},
      colors:P({{ch.comps_c|json}}),
      valueFmt:function(v){ return v.toFixed(2)+'x'; }
    });

    drawVBars(document.getElementById('estChart'), {
      labels:['TTM (real)','2026E guía (punto medio)','2026E consenso','2027E consenso'],
      values:{{ch.est|json}},
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.blueLight,PALETTE.pale],
      valueFmt:function(v){ return '$'+v.toFixed(1)+'B'; }
    });

    drawHBars(document.getElementById('sotpChart'), {
      labels:{{ch.sotp_l|json}},
      values:{{ch.sotp_v|json}},
      colors:P({{ch.sotp_c|json}}),
      padL:250,
      valueFmt:function(v){ return '$'+v.toFixed(1)+'B'; }
    });

    drawRangeBars(document.getElementById('footballChart'), {
      labels:['M1: Suma de partes','M2: Comparables','M3: Reversión histórica','M4: Consenso Wall Street'],
      domMin:0,
      ranges:{{ch.ff|json}},
      colors:[PALETTE.blue,PALETTE.blueLight,PALETTE.pale,PALETTE.gold],
      refLines:[{value:{{price|js2}},color:PALETTE.red,label:'Mercado {{price|usd0}}'},{value:{{blend|js2}},color:PALETTE.navy,label:'Blend {{blend|usd0}}'}],
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
