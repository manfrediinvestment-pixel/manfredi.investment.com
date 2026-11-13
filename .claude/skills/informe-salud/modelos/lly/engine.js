<script>
/* ---- Motor de gráficos propio, sin dependencias externas (Canvas 2D) ---- */
(function(){
  var PALETTE = {ink:'#161a20', muted:'#1c2a44', line:'#e3e9f0', navy:'#0b1f3a', navy2:'#15335c', blue:'#2f5f9e', blueLight:'#5f8fc7', pale:'#c7d9ec', red:'#a8291f', gold:'#c99a3c'};

  function setupCanvas(canvas, cssHeight){
    var dpr = window.devicePixelRatio || 1;
    var cssWidth = canvas.parentElement.clientWidth - 44;
    canvas.style.height = cssHeight + 'px';
    canvas.width = Math.max(1, Math.round(cssWidth * dpr));
    canvas.height = Math.max(1, Math.round(cssHeight * dpr));
    var ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return {ctx: ctx, w: cssWidth, h: cssHeight};
  }

  function drawVBars(canvas, opts){
    var cssH = parseInt(canvas.getAttribute('height'), 10) || 260;
    var setup = setupCanvas(canvas, cssH);
    var ctx = setup.ctx, W = setup.w, H = setup.h;
    ctx.clearRect(0,0,W,H);
    ctx.font = '11px "IBM Plex Mono", monospace';

    var labels = opts.labels, values = opts.values, colors = opts.colors;
    var log = !!opts.log;
    var padL = 46, padR = 10, padT = 16, padB = 46;
    var plotW = W - padL - padR, plotH = H - padT - padB;

    var maxV = Math.max.apply(null, values);
    var minV = log ? Math.min.apply(null, values) : 0;
    function scaleY(v){
      if(log){
        var lv = Math.log10(Math.max(v,0.01)), lmax = Math.log10(maxV*1.15), lmin = Math.log10(Math.max(minV*0.5,1));
        return padT + plotH - ((lv - lmin) / (lmax - lmin)) * plotH;
      }
      return padT + plotH - (v / (maxV*1.15)) * plotH;
    }

    ctx.strokeStyle = PALETTE.line; ctx.lineWidth = 1;
    var gridSteps = 4;
    for(var g=0; g<=gridSteps; g++){
      var yy = padT + (plotH/gridSteps)*g;
      ctx.beginPath(); ctx.moveTo(padL, yy); ctx.lineTo(W-padR, yy); ctx.stroke();
    }
    ctx.strokeStyle = PALETTE.navy; ctx.lineWidth = 1.3;
    ctx.beginPath(); ctx.moveTo(padL, padT+plotH); ctx.lineTo(W-padR, padT+plotH); ctx.stroke();

    var n = values.length;
    var slot = plotW / n;
    var barW = Math.min(slot * 0.56, 64);

    for(var i=0;i<n;i++){
      var cx = padL + slot*i + slot/2;
      var y0 = scaleY(values[i]);
      var yBase = padT + plotH;
      ctx.fillStyle = colors[i % colors.length];
      var bw = barW;
      ctx.fillRect(cx - bw/2, y0, bw, yBase - y0);

      ctx.fillStyle = PALETTE.ink;
      ctx.textAlign = 'center';
      ctx.font = '600 11px "IBM Plex Mono", monospace';
      var vLabel = opts.valueFmt ? opts.valueFmt(values[i]) : values[i];
      ctx.fillText(vLabel, cx, y0 - 6);

      ctx.fillStyle = PALETTE.muted;
      ctx.font = '10px "Inter", sans-serif';
      wrapLabel(ctx, labels[i], cx, yBase + 16, slot + 6);
    }
  }

  function wrapLabel(ctx, text, cx, y, maxW, align){
    var words = String(text).split(' ');
    var lines = [];
    var cur = '';
    for(var i=0;i<words.length;i++){
      var test = cur ? cur + ' ' + words[i] : words[i];
      if(ctx.measureText(test).width > maxW && cur){ lines.push(cur); cur = words[i]; }
      else cur = test;
    }
    if(cur) lines.push(cur);
    lines = lines.slice(0,2);
    ctx.textAlign = align || 'center';
    for(var j=0;j<lines.length;j++){
      ctx.fillText(lines[j], cx, y + j*11);
    }
  }

  function drawHBars(canvas, opts){
    var cssH = parseInt(canvas.getAttribute('height'), 10) || 260;
    var setup = setupCanvas(canvas, cssH);
    var ctx = setup.ctx, W = setup.w, H = setup.h;
    ctx.clearRect(0,0,W,H);

    var labels = opts.labels, values = opts.values, colors = opts.colors;
    var padL = opts.padL || 128, padR = 54, padT = 10, padB = 10;
    var plotW = W - padL - padR, plotH = H - padT - padB;
    var maxV = Math.max.apply(null, values) * 1.12;

    var n = values.length;
    var slot = plotH / n;
    var barH = Math.min(slot * 0.5, 30);

    ctx.strokeStyle = PALETTE.line; ctx.lineWidth = 1;
    for(var g=0; g<=4; g++){
      var xx = padL + (plotW/4)*g;
      ctx.beginPath(); ctx.moveTo(xx, padT); ctx.lineTo(xx, padT+plotH); ctx.stroke();
    }
    ctx.strokeStyle = PALETTE.navy;
    ctx.beginPath(); ctx.moveTo(padL, padT); ctx.lineTo(padL, padT+plotH); ctx.stroke();

    for(var i=0;i<n;i++){
      var cy = padT + slot*i + slot/2;
      var x0 = padL;
      var w = (values[i]/maxV) * plotW;
      ctx.fillStyle = colors[i % colors.length];
      ctx.fillRect(x0, cy - barH/2, w, barH);

      ctx.fillStyle = PALETTE.ink;
      ctx.font = '12px "Inter", sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(labels[i], padL - 10, cy + 4);

      ctx.fillStyle = PALETTE.ink;
      ctx.font = '600 11px "IBM Plex Mono", monospace';
      ctx.textAlign = 'left';
      var vLabel = opts.valueFmt ? opts.valueFmt(values[i]) : values[i];
      ctx.fillText(vLabel, x0 + w + 8, cy + 4);
    }
  }

  function drawRangeBars(canvas, opts){
    var cssH = parseInt(canvas.getAttribute('height'), 10) || 260;
    var setup = setupCanvas(canvas, cssH);
    var ctx = setup.ctx, W = setup.w, H = setup.h;
    ctx.clearRect(0,0,W,H);

    var labels = opts.labels, ranges = opts.ranges, colors = opts.colors, refLines = opts.refLines || [];
    var padL = opts.padL || 200, padR = 40, padT = 34, padB = 10;
    var plotW = W - padL - padR, plotH = H - padT - padB;

    var allVals = [];
    ranges.forEach(function(r){ allVals.push(r[0], r[1]); });
    refLines.forEach(function(r){ allVals.push(r.value); });
    var domMin = (opts.domMin != null) ? opts.domMin : Math.min.apply(null, allVals) * 0.94;
    var domMax = Math.max.apply(null, allVals) * 1.04;
    function scaleX(v){ return padL + ((v - domMin)/(domMax - domMin)) * plotW; }

    var n = ranges.length;
    var slot = plotH / n;
    var barH = Math.min(slot * 0.42, 22);

    ctx.strokeStyle = PALETTE.line; ctx.lineWidth = 1;
    for(var g=0; g<=4; g++){
      var xx = padL + (plotW/4)*g;
      ctx.beginPath(); ctx.moveTo(xx, padT); ctx.lineTo(xx, padT+plotH); ctx.stroke();
    }

    for(var i=0;i<n;i++){
      var cy = padT + slot*i + slot/2;
      var x0 = scaleX(ranges[i][0]), x1 = scaleX(ranges[i][1]);
      ctx.fillStyle = colors[i % colors.length];
      ctx.fillRect(x0, cy - barH/2, Math.max(x1-x0,2), barH);
      ctx.beginPath(); ctx.arc(x0, cy, barH/2, 0, Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.arc(x1, cy, barH/2, 0, Math.PI*2); ctx.fill();

      ctx.fillStyle = PALETTE.ink;
      ctx.font = '12px "Inter", sans-serif';
      ctx.textAlign = 'right';
      wrapLabel(ctx, labels[i], padL - 12, cy - 11, padL - 20, 'right');

      ctx.font = '600 10.5px "IBM Plex Mono", monospace';
      var vf = opts.valueFmt || function(v){ return '$'+v.toFixed(0); };
      ctx.textAlign = 'right';
      ctx.fillText(vf(ranges[i][0]), x0 - barH/2 - 4, cy + 12);
      ctx.textAlign = 'left';
      ctx.fillText(vf(ranges[i][1]), x1 + barH/2 + 4, cy + 12);
    }

    var sortedRefs = refLines.slice().sort(function(a,b){ return a.value - b.value; });
    var lastLabelX = null;
    sortedRefs.forEach(function(r){
      var x = scaleX(r.value);
      ctx.strokeStyle = r.color; ctx.lineWidth = 1.6; ctx.setLineDash([4,3]);
      ctx.beginPath(); ctx.moveTo(x, padT-6); ctx.lineTo(x, padT+plotH); ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = r.color;
      ctx.font = '600 10.5px "IBM Plex Mono", monospace';
      ctx.textAlign = 'center';
      var stagger = (lastLabelX !== null && Math.abs(x - lastLabelX) < 60);
      var ly = stagger ? padT - 24 : padT - 12;
      ctx.fillText(r.label, x, ly);
      lastLabelX = x;
    });
  }

  function drawLines(canvas, opts){
    var cssH = parseInt(canvas.getAttribute('height'), 10) || 260;
    var setup = setupCanvas(canvas, cssH);
    var ctx = setup.ctx, W = setup.w, H = setup.h;
    ctx.clearRect(0,0,W,H);

    var labels = opts.labels, series = opts.series;
    var padL = 40, padR = 28, padT = 16, padB = 54;
    var plotW = W - padL - padR, plotH = H - padT - padB;

    var allVals = [];
    series.forEach(function(s){ allVals = allVals.concat(s.values); });
    var maxV = Math.max.apply(null, allVals) * 1.08;
    var minV = Math.min.apply(null, allVals) * 0.92;

    function scaleX(i){ return padL + (plotW/(labels.length-1)) * i; }
    function scaleY(v){ return padT + plotH - ((v - minV)/(maxV-minV)) * plotH; }

    ctx.strokeStyle = PALETTE.line; ctx.lineWidth = 1;
    for(var g=0; g<=4; g++){
      var yy = padT + (plotH/4)*g;
      ctx.beginPath(); ctx.moveTo(padL, yy); ctx.lineTo(W-padR, yy); ctx.stroke();
    }
    ctx.strokeStyle = PALETTE.navy;
    ctx.beginPath(); ctx.moveTo(padL, padT+plotH); ctx.lineTo(W-padR, padT+plotH); ctx.stroke();

    series.forEach(function(s){
      ctx.strokeStyle = s.color; ctx.lineWidth = 2.2;
      ctx.beginPath();
      s.values.forEach(function(v,i){
        var x = scaleX(i), y = scaleY(v);
        if(i===0) ctx.moveTo(x,y); else ctx.lineTo(x,y);
      });
      ctx.stroke();
      s.values.forEach(function(v,i){
        var x = scaleX(i), y = scaleY(v);
        ctx.fillStyle = s.color;
        ctx.beginPath(); ctx.arc(x,y,2.6,0,Math.PI*2); ctx.fill();
        if(opts.valueFmt){
          ctx.font = '600 10px "IBM Plex Mono", monospace';
          ctx.textAlign = 'center';
          ctx.fillText(opts.valueFmt(v), x, y - 8);
        }
      });
    });

    ctx.fillStyle = PALETTE.muted;
    ctx.font = '10px "IBM Plex Mono", monospace';
    ctx.textAlign = 'center';
    labels.forEach(function(l,i){ ctx.fillText(l, scaleX(i), padT+plotH+16); });

    var lx = padL, ly = H - 12;
    ctx.font = '11px "Inter", sans-serif';
    series.forEach(function(s){
      ctx.fillStyle = s.color;
      ctx.fillRect(lx, ly-8, 10, 10);
      ctx.fillStyle = PALETTE.ink;
      ctx.textAlign = 'left';
      ctx.fillText(s.name, lx+14, ly);
      lx += 14 + ctx.measureText(s.name).width + 22;
    });
  }


