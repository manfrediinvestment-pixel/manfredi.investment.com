  function W520(){ return (document.getElementById('footballChart').parentElement.clientWidth || 999) < 520; }
  function NARROW(){ return (document.getElementById('compChart').parentElement.clientWidth || 999) < 560; }
  function fyl(a){ return NARROW() ? a.map(function(l){ return "'" + l.slice(2); }) : a; }
  function ql(a){ return NARROW() ? a.map(function(l){ return l.replace(' FY', ' '); }) : a; }
  function tail(a){ return NARROW() ? a.slice(-8) : a; }
  function renderAll(){
    drawVBars(document.getElementById('historyChart'), {
      labels:fyl({{js_fy}}),
      values:{{js_ns}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return (NARROW() ? '' : '$')+v.toFixed(0); }
    });

    drawLines(document.getElementById('feeChart'), {
      labels:fyl({{js_fy}}),
      minV:0, maxV:7,
      yFmt:function(v){ return '$'+v.toFixed(1); },
      series:[{name:'Cuotas de membresía', color:PALETTE.navy, values:{{js_fees}}},
              {name:(NARROW() ? 'Resultado de la mercadería' : 'Resultado de la mercadería (resultado operativo − cuotas)'), color:PALETTE.gold, values:{{js_merch_oi}}}]
    });

    drawVBars(document.getElementById('shareChart'), {
      labels:fyl({{js_fy}}),
      values:{{js_fee_share}},
      colors:[PALETTE.navy,PALETTE.navy,PALETTE.navy2,PALETTE.navy2,PALETTE.blue,PALETTE.blue,PALETTE.blue,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight],
      valueFmt:function(v){ return NARROW() ? v.toFixed(0) : v.toFixed(0)+'%'; }
    });

    drawHBars(document.getElementById('segChart'), {
      labels:['Estados Unidos','Canadá','Otros internacionales'],
      values:[{{seg.us.oi|js2}},{{seg.ca.oi|js2}},{{seg.oi.oi|js2}}],
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.gold],
      padL:160,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawGroupedBars(document.getElementById('compChart'), {
      labels:ql(tail({{js_ql}})),
      series:[{name:'Frecuencia (tráfico)', color:PALETTE.navy, values:tail({{js_trx}})},{name:'Ticket promedio', color:PALETTE.gold, values:tail({{js_tkt}})}],
      markers:{name:'Comparable total', values:tail({{js_comp}})},
      minV:0, maxV:10
    });

    drawGroupedBars(document.getElementById('usChart'), {
      labels:ql(tail({{js_ql}})),
      series:[{name:'Frecuencia (tráfico)', color:PALETTE.navy, values:tail({{js_us_trx}})},{name:'Ticket promedio', color:PALETTE.gold, values:tail({{js_us_tkt}})}],
      markers:{name:'Comparable EE.UU.', values:tail({{js_us_comp}})},
      minV:0, maxV:10
    });

    var rc = {{js_reg_comp}};
    var rl = {{js_ql_m}};
    drawLines(document.getElementById('regionChart'), {
      labels:(NARROW() ? rl.map(function(l, i){ return (i % 2 === 1 || i === rl.length - 1) ? l.replace(' FY', ' ') : ''; }) : rl.map(function(l){ return l.replace(' FY', ' '); })),
      minV:0, maxV:12,
      yFmt:function(v){ return v.toFixed(0)+'%'; },
      series:[{name:'EE.UU.', color:PALETTE.navy, values:rc[0]},{name:'Canadá', color:PALETTE.red, values:rc[1]},{name:'Otros internacionales', color:PALETTE.gold, values:rc[2]}]
    });

    drawVBars(document.getElementById('digChart'), {
      labels:ql({{js_ql}}),
      values:{{js_dig}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.blue,PALETTE.blue,PALETTE.navy],
      valueFmt:function(v){ return NARROW() ? '+'+v.toFixed(0) : '+'+v.toFixed(0)+'%'; }
    });

    drawLines(document.getElementById('renewChart'), {
      labels:ql({{js_mq}}).map(function(l, i){ return NARROW() && i % 2 === 1 ? '' : l; }),
      minV:88, maxV:94,
      yFmt:function(v){ return v.toFixed(1)+'%'; },
      series:[{name:'Renovación EE.UU. y Canadá', color:PALETTE.navy, values:{{js_ren_us}}},{name:'Renovación mundial', color:PALETTE.gold, values:{{js_ren_ww}}}]
    });

    drawLines(document.getElementById('membersChart'), {
      labels:ql({{js_mq}}).map(function(l, i){ return NARROW() && i % 2 === 1 ? '' : l; }),
      minV:30, maxV:90,
      yFmt:function(v){ return v.toFixed(0)+'M'; },
      series:[{name:'Socios pagos (millones)', color:PALETTE.navy, values:{{js_paid}}},{name:'Socios Executive (millones)', color:PALETTE.blueLight, values:{{js_exec}}}]
    });

    drawVBars(document.getElementById('feeqChart'), {
      labels:ql({{js_mq}}),
      values:{{js_fee_g}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blue,PALETTE.navy,PALETTE.navy,PALETTE.navy,PALETTE.blue,PALETTE.blueLight],
      valueFmt:function(v){ return NARROW() ? '+'+v.toFixed(0) : '+'+v.toFixed(1)+'%'; }
    });

    drawVBars(document.getElementById('whChart'), {
      labels:fyl({{js_wh_y}}).map(function(l){ return l.replace("'27E", '27E'); }),
      values:{{js_wh}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.navy2,PALETTE.navy,PALETTE.gold],
      valueFmt:function(v){ return v.toFixed(0); }
    });

    drawLines(document.getElementById('marginChart'), {
      labels:fyl({{js_fy}}),
      minV:0, maxV:14,
      yFmt:function(v){ return v.toFixed(0)+'%'; },
      series:[{name:'Margen bruto', color:PALETTE.navy, values:{{js_gm}}},
              {name:'Gastos (SG&A) / ventas', color:PALETTE.gold, values:{{js_sga}}},
              {name:'Margen operativo', color:PALETTE.blueLight, values:{{js_om}}},
              {name:'Margen de la mercadería', color:PALETTE.red, values:{{js_mm}}}]
    });

    drawVBars(document.getElementById('invChart'), {
      labels:fyl({{js_fy}}),
      values:{{js_turns}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return NARROW() ? v.toFixed(0) : v.toFixed(1)+'x'; }
    });

    drawLines(document.getElementById('cashChart'), {
      labels:fyl({{js_fy}}),
      minV:0, maxV:18,
      yFmt:function(v){ return '$'+v.toFixed(0); },
      series:[{name:'Flujo operativo', color:PALETTE.navy, values:{{js_ocf}}},{name:'Capex', color:PALETTE.red, values:{{js_capex}}},{name:'Flujo de caja libre', color:PALETTE.blueLight, values:{{js_fcf}}}]
    });

    drawHBars(document.getElementById('compsChart'), {
      labels:['Costco','Walmart','Amazon (referencia)',"BJ's Wholesale",'Dollar Tree','Target','Dollar General','Kroger'],
      values:[{{pe_ntm_now|js2}},{{peers.WMT.pe|js2}},{{amzn.pe|js2}},{{peers.BJ.pe|js2}},{{peers.DLTR.pe|js2}},{{peers.TGT.pe|js2}},{{peers.DG.pe|js2}},{{peers.KR.pe|js2}}],
      colors:[PALETTE.navy,PALETTE.blueLight,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight],
      padL:170,
      valueFmt:function(v){ return v.toFixed(1)+'x'; }
    });

    drawVBars(document.getElementById('estChart'), {
      labels:(NARROW() ? ['FY24','FY25','FY26','FY27e','FY28e'] : ['FY2024 real','FY2025 real','FY2026 real','FY2027 consenso','FY2028 consenso']),
      values:[{{eps_fy.2024|js2}},{{eps_fy.2025|js2}},{{eps_fy.2026|js2}},{{c27|js2}},{{c28|js2}}],
      colors:[PALETTE.pale,PALETTE.blueLight,PALETTE.navy,PALETTE.blue,PALETTE.blueLight],
      valueFmt:function(v){ return '$'+v.toFixed(2); }
    });

    drawHBars(document.getElementById('bizChart'), {
      labels:['Cuotas de membresía','Mercadería','Caja neta (30-ago-2026)'],
      values:[{{biz_base_memb_ps|js2}},{{biz_base_merch_ps|js2}},{{biz_netcash_ps|js2}}],
      colors:[PALETTE.navy,PALETTE.gold,PALETTE.blueLight],
      padL:170,
      valueFmt:function(v){ return '$'+v.toFixed(2); }
    });

    drawLines(document.getElementById('peChart'), {
      labels:{{js_pe_labels}},
      minV:15, maxV:60,
      yFmt:function(v){ return v.toFixed(0)+'x'; },
      series:[{name:'P/E (EPS de los 4 trimestres siguientes)', color:PALETTE.navy, values:{{js_pe_vals}}},
              {name:'Promedio 10 años', color:PALETTE.blueLight, values:{{js_pe_10}}},
              {name:'Promedio desde feb-2024', color:PALETTE.gold, values:{{js_pe_rr}}}]
    });

    drawRangeBars(document.getElementById('footballChart'), {
      padR:(W520() ? 54 : 40),
      labels:(W520() ? ['M1a: DCF','M1b: Cuotas + mercadería','M2: Comparables','M3: Reversión','M4: Consenso'] : ['M1a: DCF consolidado (Bear a Bull)','M1b: DCF por negocio (Bear a Bull)','M2: Comparables minoristas','M3: Reversión (propio y relativo)','M4: Consenso Wall Street']),
      domMin:0,
      ranges:[[{{dcf_bear|js2}},{{dcf_bull|js2}}],[{{biz_bear|js2}},{{biz_bull|js2}}],[{{comp_low|js2}},{{comp_high|js2}}],[{{rev_low|js2}},{{rev_high|js2}}],[{{cons_low|js2}},{{cons_high|js2}}]],
      colors:[PALETTE.blue,PALETTE.navy2,PALETTE.blueLight,PALETTE.pale,PALETTE.gold],
      refLines:[{value:{{price|js2}},color:PALETTE.red,label:'Mercado {{price|usd0}}'},{value:{{blend|js2}},color:PALETTE.navy,label:'Blend {{blend|usd0}}'}],
      padL:(W520() ? 118 : 220),
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
