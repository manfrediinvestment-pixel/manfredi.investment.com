  function W520(){ return (document.getElementById('footballChart').parentElement.clientWidth || 999) < 520; }
  function NARROW(){ return (document.getElementById('compChart').parentElement.clientWidth || 999) < 560; }
  function fyl(a){ return NARROW() ? a.map(function(l){ return "'" + l.slice(2); }) : a; }
  function ql(a){ return NARROW() ? a.map(function(l){ return l.replace(' FY',''); }) : a; }
  function tail(a){ return NARROW() ? a.slice(-8) : a; }
  function renderAll(){
    drawVBars(document.getElementById('historyChart'), {
      labels:fyl({{js_fy}}),
      values:{{js_rev}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return (NARROW() ? '' : '$')+v.toFixed(0); }
    });

    drawHBars(document.getElementById('segChart'), {
      labels:['Walmart U.S.','Walmart International',"Sam's Club U.S."],
      values:[{{seg.us.oi|js2}},{{seg.intl.oi|js2}},{{seg.sams.oi|js2}}],
      colors:[PALETTE.navy,PALETTE.blue,PALETTE.gold],
      padL:170,
      valueFmt:function(v){ return '$'+v.toFixed(2)+'B'; }
    });

    drawGroupedBars(document.getElementById('compChart'), {
      labels:ql(tail({{js_ql}})),
      series:[{name:'Transacciones (tráfico)', color:PALETTE.navy, values:tail({{js_us_trx}})},{name:'Ticket promedio', color:PALETTE.gold, values:tail({{js_us_tkt}})}],
      markers:{name:'Comparable total', values:tail({{js_us_comp}})}
    });

    drawGroupedBars(document.getElementById('samsChart'), {
      labels:ql(tail({{js_ql}})),
      series:[{name:'Transacciones (tráfico)', color:PALETTE.navy, values:tail({{js_sams_trx}})},{name:'Ticket promedio', color:PALETTE.gold, values:tail({{js_sams_tkt}})}],
      markers:{name:'Comparable total', values:tail({{js_sams_comp}})}
    });

    drawVBars(document.getElementById('ecomChart'), {
      labels:(NARROW() ? {{js_ecom_ql}}.map(function(l){ return l.indexOf('1T')===0 ? l.replace(' FY','') : l.slice(0,2); }) : {{js_ecom_ql}}),
      values:{{js_ecom_q}},
      colors:[PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.blue,PALETTE.blue,PALETTE.blue,PALETTE.navy,PALETTE.navy],
      valueFmt:function(v){ return '+'+v.toFixed(0)+'%'; }
    });

    drawLines(document.getElementById('marginChart'), {
      labels:{{js_fy}},
      minV:0, maxV:28,
      yFmt:function(v){ return v.toFixed(0)+'%'; },
      series:[{name:'Margen bruto', color:PALETTE.navy, values:{{js_gm}}},
              {name:'Gastos operativos / ventas', color:PALETTE.gold, values:{{js_opex}}},
              {name:'Margen operativo', color:PALETTE.blueLight, values:{{js_om}}}]
    });

    drawVBars(document.getElementById('invChart'), {
      labels:fyl({{js_fy}}),
      values:{{js_turns}},
      colors:[PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blue,PALETTE.navy2,PALETTE.navy],
      valueFmt:function(v){ return v.toFixed(1)+'x'; }
    });

    drawLines(document.getElementById('cashChart'), {
      labels:{{js_fy}},
      minV:0, maxV:48,
      yFmt:function(v){ return '$'+v.toFixed(0); },
      series:[{name:'Flujo operativo', color:PALETTE.navy, values:{{js_ocf}}},{name:'Capex', color:PALETTE.red, values:{{js_capex}}},{name:'Flujo de caja libre', color:PALETTE.blueLight, values:{{js_fcf}}}]
    });

    drawHBars(document.getElementById('compsChart'), {
      labels:['Costco','Walmart','Amazon (referencia)',"BJ's Wholesale",'Target','Dollar Tree','Dollar General','Kroger'],
      values:[{{peers.COST.pe|js2}},{{pe_ntm_now|js2}},{{amzn.pe|js2}},{{peers.BJ.pe|js2}},{{peers.TGT.pe|js2}},{{peers.DLTR.pe|js2}},{{peers.DG.pe|js2}},{{peers.KR.pe|js2}}],
      colors:[PALETTE.blueLight,PALETTE.navy,PALETTE.pale,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight,PALETTE.blueLight],
      padL:170,
      valueFmt:function(v){ return v.toFixed(1)+'x'; }
    });

    drawVBars(document.getElementById('estChart'), {
      labels:['FY2024 real','FY2025 real','FY2026 real','FY2027 consenso','FY2028 consenso','FY2029 consenso'],
      values:[{{eps_fy.2024|js2}},{{eps_fy.2025|js2}},{{eps_fy.2026|js2}},{{c27|js2}},{{c28|js2}},{{c29|js2}}],
      colors:[PALETTE.pale,PALETTE.blueLight,PALETTE.navy,PALETTE.blue,PALETTE.blueLight,PALETTE.pale],
      valueFmt:function(v){ return '$'+v.toFixed(2); }
    });

    var sotpSigned = [{{sotp.us.ps|js2}},{{sotp.sams.ps|js2}},{{sotp.intl_rest.ps|js2}},{{sotp.walmex.ps|js2}},{{sotp.flip.ps|js2}},{{sotp.pp.ps|js2}},{{sotp.corp.ps|js2}},{{sotp.netdebt.ps|js2}}];
    drawHBars(document.getElementById('sotpChart'), {
      labels:['Walmart U.S.',"Sam's Club U.S.",'Resto de Internacional','Walmex (mercado)','Flipkart (transacción)','PhonePe (salida a bolsa)','Corporativo','Deuda neta'],
      values:sotpSigned.map(function(v){ return Math.abs(v); }),
      colors:sotpSigned.map(function(v){ return v>0 ? PALETTE.blue : PALETTE.red; }),
      padL:180,
      valueFmt:function(v,i){ return (sotpSigned[i]>0?'+$':'−$')+v.toFixed(2); }
    });

    drawLines(document.getElementById('peChart'), {
      labels:{{js_pe_labels}},
      minV:8, maxV:48,
      yFmt:function(v){ return v.toFixed(0)+'x'; },
      series:[{name:'P/E (EPS de los 4 trimestres siguientes)', color:PALETTE.navy, values:{{js_pe_vals}}},
              {name:'Promedio 10 años', color:PALETTE.blueLight, values:{{js_pe_10}}},
              {name:'Promedio desde jul-2024', color:PALETTE.gold, values:{{js_pe_rr_full}}}]
    });

    drawRangeBars(document.getElementById('footballChart'), {
      labels:(W520() ? ['M1a: DCF','M1b: Suma de partes','M2: Comparables','M3: Reversión','M4: Consenso'] : ['M1a: DCF (Bear a Bull)','M1b: Suma de partes (Bear a Bull)','M2: Comparables minoristas','M3: Reversión (propio y relativo)','M4: Consenso Wall Street']),
      domMin:0,
      ranges:[[{{dcf_bear|js2}},{{dcf_bull|js2}}],[{{sotp_bear|js2}},{{sotp_bull|js2}}],[{{comp_low|js2}},{{comp_high|js2}}],[{{rev_low|js2}},{{rev_high|js2}}],[{{cons_low|js2}},{{cons_high|js2}}]],
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
