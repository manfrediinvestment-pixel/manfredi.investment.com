  function renderAll(){
    drawVBars(document.getElementById('historyChart'), {
      labels:['FY2016','FY2017','FY2018','FY2019','FY2020','FY2021','FY2022','FY2023','FY2024','FY2025','TTM'],
      values:{{hist|json}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.blue,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return '$'+v.toFixed(1); }
    });

    var MIXC = {'Skyrizi':PALETTE.navy,'Rinvoq':PALETTE.navy,'Humira':PALETTE.red,'Botox Cosmetic':PALETTE.gold,'Juvederm':PALETTE.gold};
    var mixL = {{mix_labels|json}};
    drawHBars(document.getElementById('mixChart'), {
      labels:mixL,
      values:{{mix_values|json}},
      colors:mixL.map(function(l){ return MIXC[l] || PALETTE.blueLight; }),
      padL:150,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawHBars(document.getElementById('loeChart'), {
      labels:{{loe_labels|json}},
      values:{{loe_values|json}},
      colors:[PALETTE.red,PALETTE.red,PALETTE.gold,PALETTE.gold,PALETTE.gold,PALETTE.navy,PALETTE.blueLight,PALETTE.blueLight,PALETTE.navy],
      padL:150,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawLines(document.getElementById('humiraChart'), {
      labels:{{hum_hist.y|json}},
      series:[{name:'Humira EE.UU.', color:PALETTE.navy, values:{{hum_us_b|json}}},{name:'Humira fuera de EE.UU.', color:PALETTE.gold, values:{{hum_int_b|json}}}],
      valueFmt:function(v){ return v.toFixed(1); }
    });

    drawLines(document.getElementById('skyrinChart'), {
      labels:{{q_lab|json}},
      series:[{name:'Skyrizi', color:PALETTE.navy, values:{{sky_q|json}}},{name:'Rinvoq', color:PALETTE.blueLight, values:{{rin_q|json}}},{name:'Humira', color:PALETTE.red, values:{{hum_q|json}}}],
      valueFmt:function(v){ return (v/1000).toFixed(1)+'B'; }
    });

    drawLines(document.getElementById('aesChart'), {
      labels:{{q_lab|json}},
      series:[{name:'Botox Cosmetic', color:PALETTE.navy, values:{{btxc_q|json}}},{name:'Juvederm', color:PALETTE.gold, values:{{juv_q|json}}}],
      valueFmt:function(v){ return v.toFixed(0); }
    });

    drawHBars(document.getElementById('bridgeChart'), {
      labels:['EPS GAAP','Amortización','Pagos contingentes','Compras','Otros'],
      values:{{bridge_chart|json}},
      colors:[PALETTE.navy,PALETTE.blueLight,PALETTE.gold,PALETTE.pale,PALETTE.pale],
      padL:140,
      valueFmt:function(v){ return '$'+v.toFixed(2); }
    });

    drawLines(document.getElementById('marginChart'), {
      labels:{{q_lab|json}},
      series:[{name:'Margen bruto GAAP', color:PALETTE.navy, values:{{gm_q|json}}},{name:'I+D / ventas', color:PALETTE.blueLight, values:{{rd_q_pct|json}}}],
      valueFmt:function(v){ return v.toFixed(1)+'%'; }
    });

    drawVBars(document.getElementById('debtChart'), {
      labels:['4T2026','2027','2028','2029','2030','2031+'],
      values:{{mat_vals|json}},
      colors:[PALETTE.blue,PALETTE.blue,PALETTE.blue,PALETTE.blue,PALETTE.blue,PALETTE.pale],
      valueFmt:function(v){ return '$'+v.toFixed(1); }
    });

    drawLines(document.getElementById('cashChart'), {
      labels:['2021','2022','2023','2024','2025','TTM'],
      series:[{name:'Flujo operativo', color:PALETTE.navy, values:{{cash_ocf|json}}},{name:'Flujo de caja libre', color:PALETTE.blueLight, values:{{cash_fcf|json}}},{name:'Dividendos', color:PALETTE.gold, values:{{cash_div|json}}}]
    });

    var cl = {{comps_labels|json}};
    drawHBars(document.getElementById('compsChart'), {
      labels:cl,
      values:{{comps_values|json}},
      colors:cl.map(function(l){ return l.indexOf('ABBV') === 0 ? PALETTE.navy : PALETTE.pale; }),
      padL:110,
      valueFmt:function(v){ return v.toFixed(2)+'x'; }
    });

    drawVBars(document.getElementById('estChart'), {
      labels:['TTM (real)','2026E guía','2026E consenso','2027E consenso'],
      values:{{est_values|json}},
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.blueLight,PALETTE.pale],
      valueFmt:function(v){ return '$'+v.toFixed(1)+'B'; }
    });

    drawLines(document.getElementById('pathChart'), {
      labels:{{m1_rev_years|json}},
      series:[{name:'Ingresos totales (Base)', color:PALETTE.navy, values:{{m1_rev_path|json}}},{name:'Skyrizi + Rinvoq', color:PALETTE.gold, values:{{m1_sr_path|json}}}]
    });

    drawHBars(document.getElementById('sotpChart'), {
      labels:['Skyrizi','Rinvoq','Botox y estética','Neurociencia','Oncología','Humira y resto','Pipeline (rNPV)','Terminal Botox/estética','Plataforma I+D','I+D (se resta)','Deuda neta (se resta)','Contingentes (se resta)'],
      values:{{sotp_chart|json}},
      colors:[PALETTE.navy,PALETTE.navy,PALETTE.gold,PALETTE.blue,PALETTE.blue,PALETTE.blueLight,PALETTE.blueLight,PALETTE.pale,PALETTE.pale,PALETTE.red,PALETTE.red,PALETTE.red],
      padL:170,
      valueFmt:function(v){ return '$'+v.toFixed(1)+'B'; }
    });

    drawRangeBars(document.getElementById('footballChart'), {
      labels:['M1: Suma de partes + rNPV','M2: Comparables','M3: Reversión histórica','M4: Consenso Wall Street'],
      domMin:0,
      ranges:{{ranges|json}},
      colors:[PALETTE.blue,PALETTE.blueLight,PALETTE.pale,PALETTE.gold],
      refLines:[{value:{{price|json}},color:PALETTE.red,label:'Mercado {{price|usd0}}'},{value:{{blend|json}},color:PALETTE.navy,label:'Blend {{blend|usd0}}'}],
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
