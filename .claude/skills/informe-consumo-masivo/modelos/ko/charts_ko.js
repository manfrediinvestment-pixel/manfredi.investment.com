
  function renderAll(){
    drawVBars(document.getElementById('historyChart'), {
      labels:["'16","'17","'18","'19","'20","'21","'22","'23","'24","'25"],
      values:[{{rev_hist.2016|js2}},{{rev_hist.2017|js2}},{{rev_hist.2018|js2}},{{rev_hist.2019|js2}},{{rev_hist.2020|js2}},{{rev_hist.2021|js2}},{{rev_hist.2022|js2}},{{rev_hist.2023|js2}},{{rev_hist.2024|js2}},{{rev_hist.2025|js2}}],
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.blue,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return '$'+v.toFixed(W520() ? 0 : 1); }
    });

    drawHBars(document.getElementById('stakesChart'), {
      labels:['Monster Beverage','Coca-Cola Europacific','Coca-Cola FEMSA','Coca-Cola HBC','Coca-Cola Bottlers Japan','Coca-Cola İçecek','Embotelladora Andina'],
      values:[{{stakes.MNST.now|js2}},{{stakes.CCEP.now|js2}},{{stakes.KOF.now|js2}},{{stakes.CCH.now|js2}},{{stakes.CCBJ.now|js2}},{{stakes.CCI.now|js2}},{{stakes.AKO.now|js2}}],
      colors:[PALETTE.gold,PALETTE.navy,PALETTE.navy2,PALETTE.blue,PALETTE.blueLight,PALETTE.blueLight,PALETTE.pale],
      padL:190,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawHBars(document.getElementById('segChart'), {
      labels:['Norteamérica','Europa, Medio Oriente y África','Latinoamérica','Bottling Investments','Asia Pacífico'],
      values:[{{seg.na.0|js2}},{{seg.emea.0|js2}},{{seg.latam.0|js2}},{{seg.bi.0|js2}},{{seg.apac.0|js2}}],
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.gold,PALETTE.pale,PALETTE.blueLight],
      padL:210,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawGroupedBars(document.getElementById('orgChart'), {
      labels:{{js_q}},
      series:[{name:'Ventas de concentrado', color:PALETTE.navy, values:{{js_conc}}},
              {name:'Precio/mix', color:PALETTE.gold, values:{{js_pm}}},
              {name:'Volumen de cajas (sistema)', color:PALETTE.blueLight, values:{{js_ucv}}}],
      markers:{name:'Orgánico total', values:{{js_org}}}
    });

    drawGroupedBars(document.getElementById('annualOrgChart'), {
      labels:{{js_ann_y}},
      series:[{name:'Orgánico', color:PALETTE.navy, values:{{js_ann_org}}},
              {name:'Volumen de cajas (sistema)', color:PALETTE.blueLight, values:{{js_ann_ucv}}}]
    });

    drawLines(document.getElementById('marginChart'), {
      labels:['2022','2023','2024','2025'],
      minV:0, maxV:80,
      yFmt:function(v){ return v.toFixed(0)+'%'; },
      series:[{name:'Margen bruto', color:PALETTE.navy, values:[{{comp_gm.2022|js1}},{{comp_gm.2023|js1}},{{comp_gm.2024|js1}},{{comp_gm.2025|js1}}]},
              {name:'Margen operativo', color:PALETTE.blueLight, values:[{{comp_om.2022|js1}},{{comp_om.2023|js1}},{{comp_om.2024|js1}},{{comp_om.2025|js1}}]},
              {name:'Publicidad / ventas', color:PALETTE.gold, values:[{{adv_pct.2022|js1}},{{adv_pct.2023|js1}},{{adv_pct.2024|js1}},{{adv_pct.2025|js1}}]}],
      valueFmt:function(v){ return v.toFixed(1)+'%'; }
    });

    drawLines(document.getElementById('cashChart'), {
      labels:['2019','2020','2021','2022','2023','2024','2025','2026G'],
      minV:0, maxV:16,
      yFmt:function(v){ return '$'+v.toFixed(0); },
      series:[{name:'Flujo op. reportado', color:PALETTE.red, values:[{{ocf.2019|js2}},{{ocf.2020|js2}},{{ocf.2021|js2}},{{ocf.2022|js2}},{{ocf.2023|js2}},{{ocf.2024|js2}},{{ocf.2025|js2}},{{ocf_g26|js2}}]},
              {name:'Flujo op. ajustado', color:PALETTE.navy, values:[{{ocf_adj.2019|js2}},{{ocf_adj.2020|js2}},{{ocf_adj.2021|js2}},{{ocf_adj.2022|js2}},{{ocf_adj.2023|js2}},{{ocf_adj.2024|js2}},{{ocf_adj.2025|js2}},{{ocf_g26|js2}}]},
              {name:'Capex', color:PALETTE.gold, values:[{{capex.2019|js2}},{{capex.2020|js2}},{{capex.2021|js2}},{{capex.2022|js2}},{{capex.2023|js2}},{{capex.2024|js2}},{{capex.2025|js2}},{{capex_g26|js2}}]}]
    });

    drawHBars(document.getElementById('compsChart'), {
      labels:['Monster Beverage','Coca-Cola','Colgate-Palmolive','Philip Morris','Procter & Gamble','PepsiCo','Keurig Dr Pepper'],
      values:[{{peers.MNST.pe|js2}},{{pe_ntm_now|js2}},{{peers.CL.pe|js2}},{{peers.PM.pe|js2}},{{peers.PG.pe|js2}},{{peers.PEP.pe|js2}},{{peers.KDP.pe|js2}}],
      colors:[PALETTE.blueLight,PALETTE.navy,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight],
      padL:170,
      valueFmt:function(v){ return v.toFixed(1)+'x'; }
    });

    drawVBars(document.getElementById('estChart'), {
      labels:['2024 real','2025 real','2026 guía','2027 consenso','2028 consenso'],
      values:[2.88,{{eps25|js2}},{{guide_mid|js2}},{{c27|js2}},{{c28|js2}}],
      colors:[PALETTE.pale,PALETTE.blueLight,PALETTE.navy,PALETTE.blue,PALETTE.blueLight],
      valueFmt:function(v){ return '$'+v.toFixed(2); }
    });

    drawLines(document.getElementById('peChart'), {
      labels:{{js_pe_labels}},
      minV:16, maxV:32,
      yFmt:function(v){ return v.toFixed(0)+'x'; },
      series:[{name:'P/E forward (ex post)', color:PALETTE.navy, values:{{js_pe_vals}}},{name:'Promedio ventana limpia', color:PALETTE.gold, values:{{js_pe_avg}}}]
    });

    drawRangeBars(document.getElementById('footballChart'), {
      labels:['M1: DCF (Bear a Bull)','M2: Comparables','M3: Reversión histórica','M4: Consenso Wall Street'],
      domMin:30,
      ranges:[[{{dcf_bear|js2}},{{dcf_bull|js2}}],[{{comp_low|js2}},{{comp_high|js2}}],[{{rev_low|js2}},{{rev_high|js2}}],[{{cons_low|js2}},{{cons_high|js2}}]],
      colors:[PALETTE.blue,PALETTE.blueLight,PALETTE.pale,PALETTE.gold],
      refLines:[{value:{{price|js2}},color:PALETTE.red,label:'Mercado {{price|usd0}}'},{value:{{blend|js2}},color:PALETTE.navy,label:'Blend {{blend|usd0}}'}],
      padL: W520() ? 120 : 190,
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
