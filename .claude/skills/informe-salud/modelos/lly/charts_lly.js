  function renderAll(){
    drawVBars(document.getElementById('historyChart'), {
      labels:['FY2016','FY2017','FY2018','FY2019','FY2020','FY2021','FY2022','FY2023','FY2024','FY2025','TTM'],
      values:{{hist|json}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.blue,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return '$'+v.toFixed(1); }
    });

    var MIXC = {'Mounjaro':PALETTE.navy,'Zepbound':PALETTE.navy,'Verzenio':PALETTE.blue,'Jardiance':PALETTE.blueLight,'Trulicity':PALETTE.blueLight,'Taltz':PALETTE.blueLight};
    var mixL = {{mix_labels|json}};
    drawHBars(document.getElementById('mixChart'), {
      labels:mixL,
      values:{{mix_values|json}},
      colors:mixL.map(function(l){ return MIXC[l] || PALETTE.pale; }),
      padL:180,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawHBars(document.getElementById('loeChart'), {
      labels:['Trulicity (2027)','Jardiance (2029*)','Taltz (2030)','Verzenio (2031)','Tirzepatida (2036)'],
      values:{{loe_values|json}},
      colors:[PALETTE.red,PALETTE.red,PALETTE.gold,PALETTE.gold,PALETTE.navy],
      padL:170,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawLines(document.getElementById('tirzChart'), {
      labels:['1T25','2T25','3T25','4T25','1T26','2T26','3T26'],
      series:[{name:'Ingresos totales', color:PALETTE.navy, values:{{rev_q|json}}},{name:'Tirzepatida (Mounjaro + Zepbound)', color:PALETTE.gold, values:{{tirz_q|json}}}],
      pointLabels:true,
      valueFmt:function(v){ return (v/1000).toFixed(1)+'B'; }
    });

    drawDiverging(document.getElementById('vpChart'), {
      labels:['EE.UU. · volumen','EE.UU. · precio','Fuera de EE.UU. · volumen','Fuera de EE.UU. · precio','Consolidado · volumen','Consolidado · precio'],
      values:{{vp_chart|json}},
      padL:190,
      valueFmt:function(v){ return (v>0?'+':'−')+Math.abs(v)+' pp'; }
    });

    drawLines(document.getElementById('marginChart'), {
      labels:['1T25','2T25','3T25','4T25','1T26','2T26','3T26'],
      series:[{name:'Margen bruto GAAP', color:PALETTE.navy, values:{{gm_q|json}}},{name:'Margen de desempeño (calc.)', color:PALETTE.blueLight, values:{{pm_q|json}}}],
      pointLabels:true,
      valueFmt:function(v){ return v.toFixed(1)+'%'; }
    });

    drawLines(document.getElementById('cashChart'), {
      labels:['2021','2022','2023','2024','2025','TTM'],
      series:[{name:'Flujo operativo', color:PALETTE.navy, values:{{cash_ocf|json}}},{name:'Capex', color:PALETTE.red, values:{{cash_capex|json}}},{name:'Flujo de caja libre', color:PALETTE.blueLight, values:{{cash_fcf|json}}}]
    });

    drawHBars(document.getElementById('compsChart'), {
      labels:['LLY','JNJ','ABBV','MRK','AZN','NVO','PFE'],
      values:{{comps_values|json}},
      colors:[PALETTE.navy,PALETTE.blueLight,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.gold,PALETTE.pale],
      valueFmt:function(v){ return v.toFixed(2)+'x'; }
    });

    drawVBars(document.getElementById('estChart'), {
      labels:['TTM (real)','2026E guía (punto medio)','2026E consenso','2027E consenso'],
      values:{{est_values|json}},
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.blueLight,PALETTE.pale],
      valueFmt:function(v){ return '$'+v.toFixed(1)+'B'; }
    });

    drawHBars(document.getElementById('sotpChart'), {
      labels:['Tirzepatida','Resto del portafolio comercial','Plataforma I+D post-2040','Retatrutida (rNPV)','Foundayo','Pipeline fase 3 (rNPV)','Verzenio, Taltz, Trulicity, Jardiance','Activos adquiridos 2025-26','I+D corporativa (se resta)','Deuda neta (se resta)'],
      values:{{sotp_chart|json}},
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.pale,PALETTE.gold,PALETTE.gold,PALETTE.blueLight,PALETTE.blueLight,PALETTE.pale,PALETTE.red,PALETTE.red],
      padL:250,
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
