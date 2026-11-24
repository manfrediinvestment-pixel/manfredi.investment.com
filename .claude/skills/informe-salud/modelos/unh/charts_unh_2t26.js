
  function W520(){ return (document.getElementById('footballChart').parentElement.clientWidth || 999) < 520; }
  function renderAll(){
    drawVBars(document.getElementById('historyChart'), {
      labels:['2019','2020','2021','2022','2023','2024','2025'],
      values:[{{ann.rev.2019|js2}},{{ann.rev.2020|js2}},{{ann.rev.2021|js2}},{{ann.rev.2022|js2}},{{ann.rev.2023|js2}},{{ann.rev.2024|js2}},{{ann.rev.2025|js2}}],
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return '$'+v.toFixed(0); }
    });

    drawHBars(document.getElementById('segChart'), {
      labels:['UnitedHealthcare','Optum Rx','Optum Insight','Optum Health'],
      values:[{{seg.uhc.oe26|js2}},{{seg.rx.oe26|js2}},{{seg.insight.oe26|js2}},{{seg.health.oe26|js2}}],
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.gold,PALETTE.blueLight],
      padL:150,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawLines(document.getElementById('mcrChart'), {
      labels:{{js_mcr_years}},
      minV:77, maxV:93,
      yFmt:function(v){ return v.toFixed(0)+'%'; },
      series:[{name:'MLR anual', color:PALETTE.navy, values:{{js_mcr_vals}}},{name:'Mitad de ciclo (2023-2026E)', color:PALETTE.gold, values:{{js_mcr_mid}}}]
    });

    drawGroupedBars(document.getElementById('yoyChart'), {
      labels:{{js_yoy_labels}},
      series:[{name:'Variación interanual del MLR (pp)', color:PALETTE.navy, values:{{js_yoy_vals}}}]
    });

    drawLines(document.getElementById('segMarginChart'), {
      labels:['2023','2024','2025','2026G'],
      minV:0, maxV:8,
      yFmt:function(v){ return v.toFixed(1)+'%'; },
      series:[{name:'UnitedHealthcare', color:PALETTE.navy, values:[{{seg_hist.uhc.2023|js1}},{{seg_hist.uhc.2024|js1}},2.8,{{seg.uhc.m26|js1}}]},
              {name:'Optum Health', color:PALETTE.gold, values:[{{seg_hist.health.2023|js1}},{{seg_hist.health.2024|js1}},{{seg_hist.health.2025|js1}},{{seg.health.m26|js1}}]},
              {name:'Optum Rx', color:PALETTE.blueLight, values:[{{seg_hist.rx.2023|js1}},{{seg_hist.rx.2024|js1}},{{seg_hist.rx.2025|js1}},{{seg.rx.m26|js1}}]}]
    });

    drawLines(document.getElementById('cashChart'), {
      labels:['2019','2020','2021','2022','2023','2024','2025','2026G'],
      minV:0, maxV:32,
      yFmt:function(v){ return '$'+v.toFixed(0); },
      series:[{name:'Flujo operativo', color:PALETTE.navy, values:[18.46,22.17,22.34,26.21,29.07,24.20,19.70,24.00]},
              {name:'Capex', color:PALETTE.red, values:[2.07,2.05,2.45,2.80,3.39,3.50,3.62,3.80]}]
    });

    drawHBars(document.getElementById('compsChart'), {
      labels:['Humana (excluido)','Molina (excluido)','UnitedHealth','Elevance Health','Centene (excluido)','CVS Health','Cigna Group'],
      values:[{{peers.HUM.pe|js2}},{{peers.MOH.pe|js2}},{{pe_ntm_now|js2}},{{peers.ELV.pe|js2}},{{peers.CNC.pe|js2}},{{peers.CVS.pe|js2}},{{peers.CI.pe|js2}}],
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.navy,PALETTE.blueLight,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight],
      padL:170,
      valueFmt:function(v){ return v.toFixed(1)+'x'; }
    });

    drawVBars(document.getElementById('estChart'), {
      labels:['2024 real','2025 real','2026 guía','2027 consenso','2028 consenso'],
      values:[27.66,16.35,{{guide_mid|js2}},{{c27|js2}},{{c28|js2}}],
      colors:[PALETTE.pale,PALETTE.red,PALETTE.navy,PALETTE.blue,PALETTE.blueLight],
      valueFmt:function(v){ return '$'+v.toFixed(2); }
    });

    drawHBars(document.getElementById('sotpChart'), {
      labels:['UnitedHealthcare','Optum Rx','Optum Insight','Optum Health'],
      values:[{{sotp.uhc.ev|js1}},{{sotp.rx.ev|js1}},{{sotp.insight.ev|js1}},{{sotp.health.ev|js1}}],
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.gold,PALETTE.blueLight],
      padL:150,
      valueFmt:function(v){ return '$'+v.toFixed(1)+'B'; }
    });

    drawLines(document.getElementById('peChart'), {
      labels:{{js_pe_labels}},
      minV:10, maxV:34,
      yFmt:function(v){ return v.toFixed(0)+'x'; },
      series:[{name:'P/E forward (ex post)', color:PALETTE.navy, values:{{js_pe_vals}}},{name:'Promedio ventana limpia 2016-2024', color:PALETTE.gold, values:{{js_pe_avg}}}]
    });

    drawRangeBars(document.getElementById('footballChart'), {
      labels:(W520() ? ['M1: Suma de partes','M2: Comparables','M3: Reversión','M4: Consenso'] : ['M1: Suma de partes (Bear a Bull)','M2: Comparables managed care','M3: Reversión (EPS normalizado)','M4: Consenso Wall Street']),
      domMin:150,
      ranges:[[{{dcf_bear|js2}},{{dcf_bull|js2}}],[{{comp_low|js2}},{{comp_high|js2}}],[{{rev_low|js2}},{{rev_high|js2}}],[{{cons_low|js2}},{{cons_high|js2}}]],
      colors:[PALETTE.blue,PALETTE.blueLight,PALETTE.pale,PALETTE.gold],
      refLines:[{value:{{price|js2}},color:PALETTE.red,label:'Mercado {{price|usd0}}'},{value:{{blend|js2}},color:PALETTE.navy,label:'Blend {{blend|usd0}}'}],
      padL:(W520() ? 118 : 210),
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
