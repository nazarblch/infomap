function selectComm(comm) {
  var i;
  if (selected_comm == comm) {
    return;
  }
    
  for (i = 0; i < comms_ps[comm].length; i++) {
    glow_ps.push(comms_ps[comm][i].glow({color: comms_colors[comm], width: 20, opacity: 1}).toBack());
  }
  for (i = 0; i < comms[comm].length; i++) {
    glow_ps.push(users[comms[comm][i]].userpic.glow({color: comms_colors[comm], width: 60, opacity: 1}).toBack());
  }
  selected_comm = comm;
}
function deselectComm(comm) {
  var i;
  if (selected_comm != comm) {
    return;
  }
    
  for (i = 0; i < glow_ps.length; i++) {
    glow_ps[i].remove();
  }
  glow_ps = [];
  selected_comm = -1;
}
function UserWithGroups(paper, cx, cy, r, r0, ucomms, name, imageurl, stroke) {
  var rad = Math.PI / 180;
  this.cx = cx;
  this.cy = cy;
  this.tx = 0;
  this.ty = 0;
  this.px = cx;
  this.py = cy;
  this.ps = [];
  this.vx = 0;
  this.vy = 0;
  this.dragged = false;
    function sector(cx, cy, r, startAngle, endAngle, params) {
        var x1 = cx + r * Math.cos(-startAngle * rad),
            x2 = cx + r * Math.cos(-endAngle * rad),
            y1 = cy + r * Math.sin(-startAngle * rad),
            y2 = cy + r * Math.sin(-endAngle * rad),
            ix1 = cx + r0 * Math.cos(-startAngle * rad),
            ix2 = cx + r0 * Math.cos(-endAngle * rad),
            iy1 = cy + r0 * Math.sin(-startAngle * rad),
            iy2 = cy + r0 * Math.sin(-endAngle * rad);

        //return paper.path(["M", cx, cy, "L", x1, y1, "A", r, r, 0, +(endAngle - startAngle > 180), 0, x2, y2, "z"]).attr(params);
        return paper.path(["M", ix1, iy1, "L", x1, y1,
                           "A", r, r, 0, +(endAngle - startAngle > 180), 0, x2, y2,
                           "L", ix2, iy2,
                           "A", r0, r0, 0, +(endAngle - startAngle > 180), 1, ix1, iy1, "z"]
                         ).attr(params);
    }
    var angle = 0,
        process = function (u, i) {
            var value = 1,
                comm = ucomms[i],
                angleplus = Math.min(360 / ucomms.length, 355),
                popangle = angle + (angleplus / 2),
                color = comms_colors[comm],
                ms = 500,
                delta = 30,
                bcolor = comms_bcolors[comm],
                p = sector(cx, cy, r, angle, angle + angleplus, {fill: "90-" + bcolor + "-" + color, stroke: stroke, "stroke-width": 1});
                u.ps.push(p);
		comms_ps[comm].push(p);
                //txt = paper.text(cx + (r + delta + 55) * Math.cos(-popangle * rad), cy + (r + delta + 25) * Math.sin(-popangle * rad), comm).attr({fill: bcolor, stroke: "none", opacity: 0, "font-size": 20});
            p.mouseover(function () {
	      if (!u.dragged) {
		selectComm(comm);
	      }
                //p.stop().animate({transform: "s1.1 1.1 " + (u.cx) + " " + (u.cy) + "T" + u.tx +","+u.ty }, ms, "elastic");
                //txt.stop().animate({opacity: 1}, ms, "elastic");
            }).mouseout(function () {
	      deselectComm(comm);
                //p.stop().animate({transform: "T" + u.tx +","+u.ty}, ms, "elastic");
                //txt.stop().animate({opacity: 0}, ms);
            });
            angle += angleplus;
        };
    for (i = 0; i < ucomms.length; i++) {
        process(this, i);
    }
  var
    u = this,
    onmove = function (dx, dy) {
      u.moveRel(dx-u.dragx, dy-u.dragy);
      u.dragx = dx;
      u.dragy = dy;
    },
    onstart = function () {
      u.dragx = 0;
      u.dragy = 0;
      u.dragged = true;
    },
    onend = function() {
      u.dragged = false;
    },
    txt = paper.text(cx+20, cy, name).attr({stroke: "none", opacity: 0, "font-size": 20, "text-anchor": "start"});
  this.userpic = paper.image(imageurl, cx-16, cy-16, 32, 32);
  if (u.ps.length > 0) {
    this.userpic.insertBefore(this.ps[0]);
  }
  u.ps.push(this.userpic);
  txt.toBack();
  u.ps.push(txt);
  this.userpic.drag(onmove, onstart, onend);
  this.userpic.mouseover(function () {
    txt.toFront();
    txt.stop().animate({opacity: 1}, 500, "elastic");
  }).mouseout(function () {
    txt.toBack();
    txt.stop().animate({opacity: 0}, 500);
  });
};
UserWithGroups.prototype.moveRel = function(dx, dy) {
   this.tx += dx;
   this.ty += dy;
   this.px += dx;
   this.py += dy;
   for (i = 0; i < this.ps.length; i++) {
     this.ps[i].attr({transform: "T" + (this.tx) + "," + (this.ty)});
   }
   for (i = 0; i < edges.length; i++) {
      var e = edges[i], l = e[0], r = e[1];
      edgeps[i].attr("path", "M"+users[l].getCanvasPos()+"L"+users[r].getCanvasPos());
   }
};
UserWithGroups.prototype.adjustToP = function() {
   this.tx = this.px - this.cx;
   this.ty = this.py - this.cy;
   for (i = 0; i < this.ps.length; i++) {
     this.ps[i].attr({transform: "T" + (this.tx) + "," + (this.ty)});
   }
};
UserWithGroups.prototype.getCanvasPos = function() {
  return (this.cx+this.tx) + "," + (this.cy+this.ty);
};


function CommVis(paper_el) {
  var i, j, cw, ch, rout=30, rin=18;
  
  if( typeof(window.innerWidth) == 'number' ) {
    //Non-IE
    cw = window.innerWidth;
    ch = window.innerHeight;
  } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
    //IE 6+ in 'standards compliant mode'
    cw = document.documentElement.clientWidth;
    ch = document.documentElement.clientHeight;
  } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
    //IE 4 compatible
    cw = document.body.clientWidth;
    ch = document.body.clientHeight;
  }
  cw -= 50;
  ch -= 50;
  if (cw < 500) {
    cw = 500;
  }
  if (ch < 500) {
    ch = 500;
  }
  
  minx = rout;
  maxx = cw-rout-150;
  miny = rout;
  maxy = ch-rout;
  this.el = paper_el;

  paper = new Raphael(paper_el, cw, ch);
  comms_colors = Array();
  comms_bcolors = Array();
  comms_ps = Array();
  selected_comm = -1;
  glow_ps = [];
  var start = 0;
  for (i = 0; i < comms.length; i++) {
    comms_colors[i] = Raphael.hsb(start, .75, 1);
    comms_bcolors[i] = Raphael.hsb(start, 1, 1);
    comms_ps[i] = [];
    start += .085;
  }

  ucomms = [];
  for (i = 0; i < names.length; i++) {
    ucomms[i] = [];
  }
  for (i = 0; i < comms.length; i++) {
    for (j = 0; j < comms[i].length; j++) {
      ucomms[comms[i][j]].push(i);
    }
  }
  users = [];
  for (i = 0; i < names.length; i++) {
    users[i] = new UserWithGroups(paper, minx + Math.random()*(maxx-minx), miny + Math.random()*(maxy-miny), rout, rin, ucomms[i], names[i], imageurls[i], "#fff");
  }

  edgeps = []
  for (i = 0; i < edges.length; i++) {
    var e = edges[i], l = e[0], r = e[1];
    edgeps[i] = paper.path("M"+users[l].getCanvasPos()+"L"+users[r].getCanvasPos()).toBack().attr({"stroke-width": 1, stroke: "gray"});
  }

  maxv = 50; //max velocity per axis
  near_repulsion = 10;
  spring_length = rout*3;
  attraction = 0.05;
  unattraction = 10;
  sdamping = 0.7;
  speed = 0.3;
  
  comm_attraction = 1;
  repulsion = 1000;
  near_range = 1;
  for (i = 0; i < 200; i++) {
    calc_forces();
  }
  comm_attraction = 0.1;
  repulsion = 50000;
  near_range = rout*2;
  speed = 0.1
  sdamping = 0.2;
  for (i = 0; i < 600; i++) {
    calc_forces();
  }

  speed = 0.1;
  sdamping = 0.7;
  for (i = 0; i < 200; i++) {
    calc_forces();
  }

  redraw();
  animate = false;
  iterate();
}
CommVis.prototype.setAnimate = function(v) {
  animate = v;
}

// requestAnim shim layer by Paul Irish
// http://paulirish.com/2011/requestanimationframe-for-smart-animating/
window.requestAnimFrame = (function(){
  return  window.requestAnimationFrame       || 
	  window.webkitRequestAnimationFrame || 
	  window.mozRequestAnimationFrame    || 
	  window.oRequestAnimationFrame      || 
	  window.msRequestAnimationFrame     || 
	  function(/* function */ callback, /* DOMElement */ element){
	    window.setTimeout(callback, 1000 / 60);
	  };
})();

calc_forces = function () {
  var k, i, j, u, v, dsq, f, d, maxd = 0;
  for (i = 0; i < users.length; i++) {
    u = users[i];
    u.fx = u.fy = 0;
    for (j = 0; j < users.length; j++) {
      if (i == j) {
	continue;
      }
      v = users[j];
      dsq = (u.px-v.px)*(u.px-v.px) + (u.py-v.py)*(u.py-v.py);
      dsq = Math.max(dsq, 0.001);
      d = Math.sqrt(dsq)
      f = repulsion / (dsq * d);
      if (d < near_range) {
	f += near_repulsion * (Math.exp((near_range-d)/100)-1);
      }
      u.fx += f * (u.px - v.px);
      u.fy += f * (u.py - v.py);
    }
  }
  var slsq = spring_length*spring_length;
  f = attraction * users.length / edges.length;
  for (i = 0; i < edges.length; i++) {
    var e = edges[i], u = users[e[0]], v = users[e[1]];
    //FIXME: this not really a spring model
    dsq = (u.px-v.px)*(u.px-v.px) + (u.py-v.py)*(u.py-v.py);
    if (dsq > slsq) {
      u.fx += f*(v.px - u.px);
      u.fy += f*(v.py - u.py);
      v.fx += f*(u.px - v.px);
      v.fy += f*(u.py - v.py);
    } else {
      /*
      f = unattraction*(spring_length - Math.sqrt(dsq));
      alert(f+"," +Math.sqrt(dsq));
      u.fx -= f*(v.px - u.px);
      u.fy -= f*(v.py - u.py);
      v.fx -= f*(u.px - v.px);
      v.fy -= f*(u.py - v.py);
      */
    }
  }
  
  //comm attraction
  for (k = 0; k < comms.length; k++) {
    f = comm_attraction / (comms[k].length*comms[k].length*comms.length);
    for (i = 0; i < comms[k].length; i++) {
      for (j = i+1; j < comms[k].length; j++) {
	var u = users[comms[k][i]], v = users[comms[k][j]];
	dsq = (u.px-v.px)*(u.px-v.px) + (u.py-v.py)*(u.py-v.py);
	if (dsq > slsq) {
          u.fx += f*(v.px - u.px);
          u.fy += f*(v.py - u.py);
          v.fx += f*(u.px - v.px);
          v.fy += f*(u.py - v.py);
	}
      }
    }
  }
  
  for (i = 0; i < users.length; i++) {
    u = users[i];
    if (u.dragged) {
      u.vx = u.vy = 0;
      continue;
    }
    u.vx = (u.vx + u.fx)*sdamping;
    u.vy = (u.vy + u.fy)*sdamping;
    if (u.px + u.vx < minx) {
      u.vx = minx - u.px;
    }
    if (u.px + u.vx > maxx) {
      u.vx = maxx - u.px;
    }
    if (u.py + u.vy < miny) {
      u.vy = miny - u.py;
    }
    if (u.py + u.vy > maxy) {
      u.vy = maxy - u.py;
    }
    d = Math.abs(u.vx) + Math.abs(u.vy);
    if (maxd < d) {
      maxd = d;
    }
    if (u.vx > maxv)
      u.vx = maxv;
    if (u.vy > maxv)
      u.vy = maxv;
    u.px += u.vx * speed;
    u.py += u.vy * speed;
  }
}

redraw = function () {
  var i;
  for (i = 0; i < users.length; i++) {
    users[i].adjustToP();
  }
  for (i = 0; i < edges.length; i++) {
    var e = edges[i], l = e[0], r = e[1];
    edgeps[i].attr("path", "M"+users[l].getCanvasPos()+"L"+users[r].getCanvasPos());
  }
}
iterate = function () {
  requestAnimFrame(iterate); //FIXME: params
  if (!animate) return;
  calc_forces();
  redraw();
}
