  function renderAll(){
    var NARROW = W520();
    drawVBars(document.getElementById('historyChart'), {
      labels:["'16","'17","'18","'19","'20","'21","'22","'23","'24","'25"],
      values:[{{rev_hist.2016|js2}},{{rev_hist.2017|js2}},{{rev_hist.2018|js2}},{{rev_hist.2019|js2}},{{rev_hist.2020|js2}},{{rev_hist.2021|js2}},{{rev_hist.2022|js2}},{{rev_hist.2023|js2}},{{rev_hist.2024|js2}},{{rev_hist.2025|js2}}],
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.blue,PALETTE.navy2,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return '$'+v.toFixed(NARROW ? 0 : 1); }
    });

    drawGroupedBars(document.getElementById('segChart'), {
      labels:['PFNA','PBNA','Bebidas franq.','EMEA','LatAm Foods','Asia Pac. Foods'],
      series:[{name:'Margen op. core 2024', color:PALETTE.pale, values:[{{seg.PFNA.om24|js1}},{{seg.PBNA.om24|js1}},{{seg.IBF.om24|js1}},{{seg.EMEA.om24|js1}},{{seg.LAF.om24|js1}},{{seg.APF.om24|js1}}]},
              {name:'Margen op. core 2025', color:PALETTE.navy, values:[{{seg.PFNA.om|js1}},{{seg.PBNA.om|js1}},{{seg.IBF.om|js1}},{{seg.EMEA.om|js1}},{{seg.LAF.om|js1}},{{seg.APF.om|js1}}]}],
      minV:0, maxV:40
    });

    drawGroupedBars(document.getElementById('orgChart'), {
      labels:{{js_q}},
      series:[{name:'Volumen orgánico', color:PALETTE.navy, values:{{js_vol}}},
              {name:'Precio efectivo neto', color:PALETTE.gold, values:{{js_price}}}],
      markers:{name:'Orgánico total', values:{{js_org}}}
    });

    drawGroupedBars(document.getElementById('pfnaChart'), {
      labels:{{js_q8}},
      series:[{name:'Volumen', color:PALETTE.navy, values:{{js_pfna_vol}}},
              {name:'Precio', color:PALETTE.gold, values:{{js_pfna_price}}}],
      markers:{name:'Orgánico', values:{{js_pfna_org}}},
      minV:-6, maxV:8
    });
    drawGroupedBars(document.getElementById('pbnaChart'), {
      labels:{{js_q8}},
      series:[{name:'Volumen', color:PALETTE.navy, values:{{js_pbna_vol}}},
              {name:'Precio', color:PALETTE.gold, values:{{js_pbna_price}}}],
      markers:{name:'Orgánico', values:{{js_pbna_org}}},
      minV:-6, maxV:8
    });

    drawGroupedBars(document.getElementById('annualOrgChart'), {
      labels:{{js_ann_y}},
      series:[{name:'Orgánico', color:PALETTE.navy, values:{{js_ann_org}}},
              {name:'Volumen de snacks', color:PALETTE.gold, values:{{js_ann_cf}}},
              {name:'Volumen de bebidas', color:PALETTE.blueLight, values:{{js_ann_bev}}}]
    });

    drawLines(document.getElementById('marginChart'), {
      labels:['2022','2023','2024','2025'],
      minV:0, maxV:80,
      series:[{name:'Margen bruto core', color:PALETTE.navy, values:[{{comp_gm.2022|js1}},{{comp_gm.2023|js1}},{{comp_gm.2024|js1}},{{comp_gm.2025|js1}}]},
              {name:'Margen operativo core', color:PALETTE.blueLight, values:[{{comp_om.2022|js1}},{{comp_om.2023|js1}},{{comp_om.2024|js1}},{{comp_om.2025|js1}}]},
              {name:'Publicidad y marketing / ventas', color:PALETTE.gold, values:[{{am_pct.2022|js1}},{{am_pct.2023|js1}},{{am_pct.2024|js1}},{{am_pct.2025|js1}}]}],
      valueFmt:function(v){ return v.toFixed(1)+'%'; }
    });

    drawLines(document.getElementById('cashChart'), {
      labels:['2019','2020','2021','2022','2023','2024','2025'],
      minV:0, maxV:16,
      yFmt:function(v){ return '$'+v.toFixed(0); },
      series:[{name:'Flujo op. reportado', color:PALETTE.red, values:[{{ocf.2019|js2}},{{ocf.2020|js2}},{{ocf.2021|js2}},{{ocf.2022|js2}},{{ocf.2023|js2}},{{ocf.2024|js2}},{{ocf.2025|js2}}]},
              {name:'Flujo op. ajustado', color:PALETTE.navy, values:[{{ocf_adj.2019|js2}},{{ocf_adj.2020|js2}},{{ocf_adj.2021|js2}},{{ocf_adj.2022|js2}},{{ocf_adj.2023|js2}},{{ocf_adj.2024|js2}},{{ocf_adj.2025|js2}}]},
              {name:'Capex', color:PALETTE.gold, values:[{{capex.2019|js2}},{{capex.2020|js2}},{{capex.2021|js2}},{{capex.2022|js2}},{{capex.2023|js2}},{{capex.2024|js2}},{{capex.2025|js2}}]}]
    });

    drawHBars(document.getElementById('compsChart'), {
      labels:['Monster Beverage','Coca-Cola','Colgate-Palmolive','Philip Morris','Procter & Gamble','Mondelez','PepsiCo','Keurig Dr Pepper'],
      values:[{{peers.MNST.pe|js2}},{{peers.KO.pe|js2}},{{peers.CL.pe|js2}},{{peers.PM.pe|js2}},{{peers.PG.pe|js2}},{{peers.MDLZ.pe|js2}},{{pe_ntm_now|js2}},{{peers.KDP.pe|js2}}],
      colors:[PALETTE.blueLight,PALETTE.gold,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.navy,PALETTE.blueLight],
      padL:170,
      valueFmt:function(v){ return v.toFixed(1)+'x'; }
    });

    drawGroupedBars(document.getElementById('cmpPepChart'), {
      labels:{{js_q8}},
      series:[{name:'Volumen (efecto en ventas)', color:PALETTE.navy, values:{{js8_vol}}},
              {name:'Precio', color:PALETTE.gold, values:{{js8_price}}}],
      markers:{name:'Orgánico', values:{{js8_org}}},
      minV:-6, maxV:16
    });
    drawGroupedBars(document.getElementById('cmpKoChart'), {
      labels:{{js_q8}},
      series:[{name:'Volumen (efecto en ventas)', color:PALETTE.navy, values:{{js8_ko_conc}}},
              {name:'Precio', color:PALETTE.gold, values:{{js8_ko_pm}}}],
      markers:{name:'Orgánico', values:{{js8_ko_org}}},
      minV:-6, maxV:16
    });

    drawHBars(document.getElementById('cmpMetricsChart'), {
      labels:['Margen bruto · PEP','Margen bruto · KO','Margen operativo · PEP','Margen operativo · KO','Conversión de caja · PEP','Conversión de caja · KO','ROIC · PEP','ROIC · KO','Capex / ventas · PEP','Capex / ventas · KO'],
      values:[{{cmp.gm.pep|js1}},{{cmp.gm.ko|js1}},{{cmp.om_ttm.pep|js1}},{{cmp.om_ttm.ko|js1}},{{cmp.conv.pep|js1}},{{cmp.conv.ko|js1}},{{cmp.roic.pep|js1}},{{cmp.roic.ko|js1}},{{cmp.capex_pct.pep|js1}},{{cmp.capex_pct.ko|js1}}],
      colors:[PALETTE.navy,PALETTE.gold],
      padL: NARROW ? 150 : 200,
      valueFmt:function(v){ return v.toFixed(1)+'%'; }
    });

    drawHBars(document.getElementById('cmpValChart'), {
      labels:['P/E 12 meses · PEP','P/E 12 meses · KO','EV/EBITDA · PEP','EV/EBITDA · KO','Precio / FCF · PEP','Precio / FCF · KO'],
      values:[{{cmp.pe.pep|js1}},{{cmp.pe.ko|js1}},{{cmp.ev_ebitda.pep|js1}},{{cmp.ev_ebitda.ko|js1}},{{cmp.p_fcf.pep|js1}},{{cmp.p_fcf.ko|js1}}],
      colors:[PALETTE.navy,PALETTE.gold],
      padL: NARROW ? 150 : 200,
      valueFmt:function(v){ return v.toFixed(1)+'x'; }
    });

    drawVBars(document.getElementById('estChart'), {
      labels:['2024 real','2025 real','2026 guía','2027 consenso','2028 consenso'],
      values:[{{eps24|js2}},{{eps25|js2}},{{guide_mid|js2}},{{c27|js2}},{{c28|js2}}],
      colors:[PALETTE.pale,PALETTE.blueLight,PALETTE.navy,PALETTE.blue,PALETTE.blueLight],
      valueFmt:function(v){ return '$'+v.toFixed(2); }
    });

    drawLines(document.getElementById('peChart'), {
      labels:{{js_pe_labels}},
      minV:12, maxV:28,
      yFmt:function(v){ return v.toFixed(0)+'x'; },
      series:[{name:'P/E forward (ex post)', color:PALETTE.navy, values:{{js_pe_vals}}},
              {name:'Promedio 10 años limpio', color:PALETTE.gold, values:{{js_pe_avg}}},
              {name:'Promedio régimen nuevo', color:PALETTE.red, values:{{js_pe_step}}}]
    });

    drawRangeBars(document.getElementById('footballChart'), {
      labels:['M1: DCF (Bear a Bull)','M2: Suma de partes','M3: Comparables','M4: Reversión histórica','M5: Consenso Wall Street'],
      domMin:60,
      ranges:[[{{dcf_bear|js2}},{{dcf_bull|js2}}],[{{sotp_low|js2}},{{sotp_high|js2}}],[{{comp_low|js2}},{{comp_high|js2}}],[{{rev_low|js2}},{{rev_high|js2}}],[{{cons_low|js2}},{{cons_high|js2}}]],
      colors:[PALETTE.blue,PALETTE.navy2,PALETTE.blueLight,PALETTE.pale,PALETTE.gold],
      refLines:[{value:{{price|js2}},color:PALETTE.red,label:'Mercado {{price|usd0}}'},{value:{{blend|js2}},color:PALETTE.navy,label:'Blend {{blend|usd0}}'}],
      padL: NARROW ? 120 : 190,
      valueFmt:function(v){ return '$'+v.toFixed(0); }
    });
  }
  function W520(){ return (document.getElementById('footballChart').parentElement.clientWidth || 999) < 520; }

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
