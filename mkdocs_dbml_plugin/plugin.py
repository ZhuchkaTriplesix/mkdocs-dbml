import os
import re
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options
from .renderer import DbmlRenderer


class DbmlPlugin(BasePlugin):
    config_scheme = (
        ("theme", config_options.Type(str, default="black")),
        ("show_indexes", config_options.Type(bool, default=True)),
        ("show_notes", config_options.Type(bool, default=True)),
    )

    def on_page_markdown(self, markdown, page, config, files):
        pattern = r"```dbml\n(.*?)```"
        docs_dir = config.get("docs_dir", "docs")

        def replace_dbml(match):
            raw = match.group(1)
            if not raw:
                return '<div class="dbml-error">Empty DBML block</div>'
            dbml_code = raw.strip()
            lines = dbml_code.split("\n")
            first = lines[0].strip() if lines else ""

            # Include from .dbml file: "file: path/to/schema.dbml" or just "path/to/schema.dbml" (single line)
            file_path = None
            if first.startswith("file:") or first.startswith("include:"):
                file_path = first.split(":", 1)[1].strip()
            elif len(lines) == 1 and first.endswith(".dbml") and " " not in first:
                file_path = first

            if file_path:
                # Resolve relative to docs_dir, normalize to prevent path traversal
                resolved = os.path.normpath(os.path.join(docs_dir, file_path))
                if not os.path.abspath(resolved).startswith(os.path.abspath(docs_dir)):
                    return f'<div class="dbml-error">DBML file path outside docs: {file_path!r}</div>'
                try:
                    with open(resolved, "r", encoding="utf-8") as f:
                        dbml_code = f.read()
                except FileNotFoundError:
                    return f'<div class="dbml-error">DBML file not found: {file_path!r}</div>'
                except OSError as e:
                    return f'<div class="dbml-error">Cannot read DBML file: {e}</div>'

            renderer = DbmlRenderer(
                theme=self.config["theme"],
                show_indexes=self.config["show_indexes"],
                show_notes=self.config["show_notes"],
            )
            try:
                html = renderer.render(dbml_code)
                return html
            except Exception as e:
                return f'<div class="dbml-error">Error parsing DBML: {str(e)}</div>'

        markdown = re.sub(pattern, replace_dbml, markdown, flags=re.DOTALL)
        return markdown

    def on_post_page(self, output, page, config):
        if "<!-- dbml-styles -->" in output:
            css = DbmlRenderer.get_css(self.config["theme"])
            js = self._get_interactive_js()
            output = output.replace("</head>", f"<style>{css}</style></head>")
            output = output.replace("</body>", f"<script>{js}</script></body>")
        return output

    def _get_interactive_js(self):
        return """
        (function(){
        var D = document;
        D.addEventListener('DOMContentLoaded', function() {
            var wraps = D.querySelectorAll('.dbml-diagram-wrapper');
            for (var wi = 0; wi < wraps.length; wi++) { (function(W) {
                var svg = W.querySelector('.dbml-diagram');
                if (!svg) return;
                var fsBtn = W.querySelector('.dbml-fullscreen-btn');
                if (fsBtn) {
                    fsBtn.addEventListener('pointerdown', function(e) { e.stopPropagation(); });
                    fsBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        var el = D.fullscreenElement || D.webkitFullscreenElement;
                        if (!el) {
                            var req = W.requestFullscreen || W.webkitRequestFullscreen;
                            if (req) { req.call(W); fsBtn.setAttribute('title', 'Exit fullscreen (Esc)'); }
                        } else {
                            var exit = D.exitFullscreen || D.webkitExitFullscreen;
                            if (exit) { exit.call(D); fsBtn.setAttribute('title', 'Fullscreen'); }
                        }
                    });
                }
                function inlineAllStyles(orig, copy, skipDefs) {
                    var tag = orig.tagName ? orig.tagName.toLowerCase() : '';
                    if (tag === 'defs') return;
                    if (orig.getBoundingClientRect && orig.getBoundingClientRect().width === 0
                        && tag !== 'svg' && tag !== 'g') return;
                    try {
                        var cs = getComputedStyle(orig);
                        var props = ['opacity','fill','stroke','stroke-width','font-size','font-weight',
                            'font-family','visibility','display','color'];
                        for (var p = 0; p < props.length; p++) {
                            var v = cs.getPropertyValue(props[p]);
                            if (v) copy.setAttribute(props[p], v);
                        }
                    } catch(e) {}
                    var oc = orig.children, cc = copy.children;
                    for (var c = 0; c < oc.length; c++) {
                        if (oc[c].nodeType === 1 && cc[c]) inlineAllStyles(oc[c], cc[c]);
                    }
                }

                function prepareExportClone() {
                    var clone = svg.cloneNode(true);
                    inlineAllStyles(svg, clone);

                    clone.removeAttribute('class');
                    clone.removeAttribute('style');

                    var pad = 40;
                    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
                    for (var i = 0; i < TN; i++) {
                        var t = TA[i];
                        var lx = t.ox + t.dx, ly = t.oy + t.dy;
                        if (lx < minX) minX = lx;
                        if (ly < minY) minY = ly;
                        if (lx + t.ow > maxX) maxX = lx + t.ow;
                        if (ly + t.oh > maxY) maxY = ly + t.oh;
                    }
                    if (minX === Infinity) {
                        var vb = (svg.getAttribute('viewBox') || '0 0 800 600').split(/\\s+/);
                        minX = 0; minY = 0; maxX = +vb[2] || 800; maxY = +vb[3] || 600;
                    }
                    minX -= pad; minY -= pad; maxX += pad; maxY += pad;
                    var vw = Math.ceil(maxX - minX);
                    var vh = Math.ceil(maxY - minY);
                    clone.setAttribute('viewBox', minX + ' ' + minY + ' ' + vw + ' ' + vh);
                    clone.setAttribute('width', vw);
                    clone.setAttribute('height', vh);

                    var bgRect = D.createElementNS('http://www.w3.org/2000/svg', 'rect');
                    bgRect.setAttribute('x', minX);
                    bgRect.setAttribute('y', minY);
                    bgRect.setAttribute('width', vw);
                    bgRect.setAttribute('height', vh);
                    var wrapBg = svg.getAttribute('data-bg') || '#000';
                    bgRect.setAttribute('fill', wrapBg);
                    clone.insertBefore(bgRect, clone.firstChild);

                    var allHits = clone.querySelectorAll('[class*="relationship-hit"]');
                    for (var i = allHits.length - 1; i >= 0; i--) {
                        allHits[i].parentNode.removeChild(allHits[i]);
                    }

                    var grps = clone.querySelectorAll('[data-table]');
                    for (var i = 0; i < TN; i++) {
                        if (grps[i] && TA[i].e.style.transform) {
                            grps[i].setAttribute('transform', 'translate(' + TA[i].dx + ',' + TA[i].dy + ')');
                        }
                    }

                    return { clone: clone, vw: vw, vh: vh };
                }

                var exportSvgBtn = W.querySelector('.dbml-export-svg-btn');
                if (exportSvgBtn) {
                    exportSvgBtn.addEventListener('pointerdown', function(e) { e.stopPropagation(); });
                    exportSvgBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        var r = prepareExportClone();
                        var s = new XMLSerializer().serializeToString(r.clone);
                        var blob = new Blob([s], { type: 'image/svg+xml;charset=utf-8' });
                        var url = URL.createObjectURL(blob);
                        var a = D.createElement('a');
                        a.href = url;
                        a.download = 'diagram.svg';
                        a.click();
                        URL.revokeObjectURL(url);
                    });
                }
                var exportPngBtn = W.querySelector('.dbml-export-png-btn');
                if (exportPngBtn) {
                    exportPngBtn.addEventListener('pointerdown', function(e) { e.stopPropagation(); });
                    exportPngBtn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        var r = prepareExportClone();
                        var scale = 2;
                        var svgStr = new XMLSerializer().serializeToString(r.clone);
                        var dataUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgStr);
                        var img = new Image();
                        img.onload = function() {
                            var canvas = D.createElement('canvas');
                            canvas.width = r.vw * scale;
                            canvas.height = r.vh * scale;
                            var ctx = canvas.getContext('2d');
                            ctx.fillStyle = svg.getAttribute('data-bg') || '#000';
                            ctx.fillRect(0, 0, canvas.width, canvas.height);
                            ctx.drawImage(img, 0, 0, r.vw * scale, r.vh * scale);
                            var pngUrl = canvas.toDataURL('image/png');
                            var a = D.createElement('a');
                            a.href = pngUrl;
                            a.download = 'diagram.png';
                            a.click();
                        };
                        img.src = dataUrl;
                    });
                }

                var S = 1, TX = 0, TY = 0;
                var M = 0; // 0=idle 1=table 2=canvas
                var DR = null;
                var MX0 = 0, MY0 = 0, IX = 0, IY = 0, CX0 = 0, CY0 = 0;

                svg.style.transformOrigin = '0 0';
                svg.style.willChange = 'transform';
                W.style.cursor = 'grab';
                W.style.userSelect = 'none';
                W.style.touchAction = 'none';

                // ---- cache tables ----
                var tg = svg.querySelectorAll('.dbml-table-group');
                var TD = Object.create(null); // name -> data
                var TA = []; // flat array
                var TN = tg.length;
                for (var i = 0; i < TN; i++) {
                    var g = tg[i];
                    var nm = g.getAttribute('data-table');
                    var bg = g.querySelector('.dbml-table-bg');
                    var d = {
                        e: g, n: nm,
                        ox: +bg.getAttribute('x'),
                        oy: +bg.getAttribute('y'),
                        ow: +bg.getAttribute('width'),
                        oh: +bg.getAttribute('height'),
                        dx: 0, dy: 0
                    };
                    TD[nm] = d;
                    TA[i] = d;
                    g.style.cursor = 'move';
                    g.style.willChange = 'transform';
                }

                // ---- cache connections ----
                var rg = svg.querySelectorAll('.dbml-relationship-group');
                var CN = rg.length;
                var C_path = new Array(CN);
                var C_line = new Array(CN);
                var C_fi = new Array(CN); // from table index in TA
                var C_ti = new Array(CN); // to table index in TA
                var C_ft = new Array(CN); // from table name
                var C_tt = new Array(CN);
                var C_sy = new Float64Array(CN);
                var C_ey = new Float64Array(CN);

                var C_hit = new Array(CN);
                for (var i = 0; i < CN; i++) {
                    var g = rg[i];
                    var fa = g.getAttribute('data-from') || '';
                    var ta = g.getAttribute('data-to') || '';
                    var allPaths = g.querySelectorAll('path');
                    var hitP = allPaths.length > 1 ? allPaths[0] : null;
                    var visP = allPaths.length > 1 ? allPaths[1] : allPaths[0];
                    C_path[i] = visP;
                    C_hit[i] = hitP;
                    C_line[i] = visP;
                    var fn = fa.split('.')[0];
                    var tn = ta.split('.')[0];
                    C_ft[i] = fn;
                    C_tt[i] = tn;
                    C_fi[i] = -1;
                    C_ti[i] = -1;
                    for (var j = 0; j < TN; j++) {
                        if (TA[j].n === fn) C_fi[i] = j;
                        if (TA[j].n === tn) C_ti[i] = j;
                    }
                    var nums = visP.getAttribute('d').match(/-?[\\d.]+/g);
                    if (nums) {
                        C_sy[i] = +nums[1];
                        C_ey[i] = +nums[nums.length - 1];
                    }
                }

                // ---- cache highlight ----
                var HL_line = new Array(CN);
                var HL_ft = new Array(CN);
                var HL_tt = new Array(CN);
                for (var i = 0; i < CN; i++) {
                    HL_line[i] = C_line[i];
                    HL_ft[i] = C_ft[i];
                    HL_tt[i] = C_tt[i];
                }

                // ---- pre-alloc typed arrays for updateConns ----
                var _sxA = new Float64Array(4);
                var _exA = new Float64Array(4);

                // ---- events ----
                for (var i = 0; i < TN; i++) { (function(td) {
                    td.e.addEventListener('pointerdown', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        M = 1; DR = td;
                        IX = td.dx; IY = td.dy;
                        MX0 = e.clientX; MY0 = e.clientY;
                        W.setPointerCapture(e.pointerId);
                    });
                    td.e.addEventListener('pointerenter', function() {
                        if (M === 0) hl(td.n);
                    });
                    td.e.addEventListener('pointerleave', function() {
                        if (M === 0) uhl();
                    });
                })(TA[i]); }

                W.addEventListener('pointerdown', function(e) {
                    if (M !== 0) return;
                    e.preventDefault();
                    M = 2;
                    CX0 = TX; CY0 = TY;
                    MX0 = e.clientX; MY0 = e.clientY;
                    W.setPointerCapture(e.pointerId);
                    W.style.cursor = 'grabbing';
                });

                W.addEventListener('pointermove', function(e) {
                    if (M === 1) {
                        var invS = 1 / S;
                        DR.dx = IX + (e.clientX - MX0) * invS;
                        DR.dy = IY + (e.clientY - MY0) * invS;
                        DR.e.style.transform = 'translate(' + DR.dx + 'px,' + DR.dy + 'px)';
                        uc();
                    } else if (M === 2) {
                        TX = CX0 + e.clientX - MX0;
                        TY = CY0 + e.clientY - MY0;
                        svg.style.transform = 'translate(' + TX + 'px,' + TY + 'px) scale(' + S + ')';
                    }
                });

                W.addEventListener('pointerup', function(e) {
                    W.releasePointerCapture(e.pointerId);
                    if (M === 2) W.style.cursor = 'grab';
                    M = 0; DR = null;
                });

                W.addEventListener('wheel', function(e) {
                    e.preventDefault();
                    var ns = S * (e.deltaY > 0 ? 0.92 : 1.08);
                    if (ns < 0.1) ns = 0.1; else if (ns > 3) ns = 3;
                    var r = W.getBoundingClientRect();
                    var px = e.clientX - r.left, py = e.clientY - r.top;
                    var c = ns / S;
                    TX = px - (px - TX) * c;
                    TY = py - (py - TY) * c;
                    S = ns;
                    svg.style.transform = 'translate(' + TX + 'px,' + TY + 'px) scale(' + S + ')';
                }, {passive: false});

                // ---- AABB segment-rect overlap (inlined) ----
                // seg(x1,y1,x2,y2) vs rect(rL,rT,rR,rB)
                // returns true if axis-aligned segment overlaps rect
                
                // ---- update connections (hot path, zero alloc) ----
                function uc() {
                    for (var i = 0; i < CN; i++) {
                        var fi = C_fi[i], ti = C_ti[i];
                        if (fi < 0 || ti < 0) continue;
                        var f = TA[fi], t = TA[ti];
                        var fL = f.ox + f.dx, fR = fL + f.ow;
                        var tL = t.ox + t.dx, tR = tL + t.ow;
                        var sy = C_sy[i] + f.dy, ey = C_ey[i] + t.dy;

                        _sxA[0] = fR + 12; _sxA[1] = fR + 12; _sxA[2] = fL - 12; _sxA[3] = fL - 12;
                        _exA[0] = tL - 12; _exA[1] = tR + 12; _exA[2] = tL - 12; _exA[3] = tR + 12;

                        var bc = 1e18, bs = 0, be = 0, bm = 0;

                        for (var j = 0; j < 4; j++) {
                            var sx = _sxA[j], ex = _exA[j];
                            var mx = (sx + ex) * 0.5;
                            var co = (sx > ex ? sx - ex : ex - sx) + (sy > ey ? sy - ey : ey - sy);

                            // Check all 3 segments for collision with any table
                            // Seg1: horizontal (sx,sy) -> (mx,sy)
                            // Seg2: vertical   (mx,sy) -> (mx,ey)
                            // Seg3: horizontal (mx,ey) -> (ex,ey)
                            var s1L = sx < mx ? sx : mx, s1R = sx > mx ? sx : mx;
                            var s3L = mx < ex ? mx : ex, s3R = mx > ex ? mx : ex;
                            var vT = sy < ey ? sy : ey, vB = sy > ey ? sy : ey;

                            for (var k = 0; k < TN; k++) {
                                if (k === fi || k === ti) continue;
                                var b = TA[k];
                                var bL = b.ox + b.dx - 5, bR = bL + b.ow + 10;
                                var bT = b.oy + b.dy - 5, bB = bT + b.oh + 10;

                                if (sy >= bT && sy <= bB && s1R >= bL && s1L <= bR) {
                                    co += 100000; break;
                                }
                                if (mx >= bL && mx <= bR && vB >= bT && vT <= bB) {
                                    co += 100000; break;
                                }
                                if (ey >= bT && ey <= bB && s3R >= bL && s3L <= bR) {
                                    co += 100000; break;
                                }
                            }
                            if (co < bc) { bc = co; bs = sx; be = ex; bm = mx; }
                        }

                        var nd = 'M ' + bs + ' ' + sy +
                            ' L ' + bm + ' ' + sy +
                            ' L ' + bm + ' ' + ey +
                            ' L ' + be + ' ' + ey;
                        C_path[i].setAttribute('d', nd);
                        if (C_hit[i]) C_hit[i].setAttribute('d', nd);
                    }
                }

                function hl(n) {
                    for (var i = 0; i < CN; i++) {
                        var s = HL_line[i].style;
                        if (HL_ft[i] === n || HL_tt[i] === n) {
                            s.opacity = '1'; s.strokeWidth = '2.5';
                        } else {
                            s.opacity = '0.15'; s.strokeWidth = '';
                        }
                    }
                }
                function uhl() {
                    if (selIdx >= 0) return;
                    for (var i = 0; i < CN; i++) {
                        var s = HL_line[i].style;
                        s.opacity = ''; s.strokeWidth = '';
                    }
                }

                // ---- click-to-select line ----
                var selIdx = -1;
                
                var hitPaths = svg.querySelectorAll('.dbml-relationship-hit');
                for (var i = 0; i < hitPaths.length; i++) { (function(idx) {
                    hitPaths[idx].addEventListener('pointerdown', function(e) {
                        e.stopPropagation();
                        e.preventDefault();
                        if (selIdx === idx) {
                            deselect();
                        } else {
                            selectLine(idx);
                        }
                    });
                })(i); }
                
                W.addEventListener('pointerdown', function() {
                    if (selIdx >= 0 && M === 0) deselect();
                }, true);
                
                function selectLine(idx) {
                    deselect();
                    selIdx = idx;
                    var g = rg[idx];
                    var line = g.querySelector('.dbml-relationship-line');
                    line.classList.add('selected');
                    
                    var fn = g.getAttribute('data-from');
                    var tn = g.getAttribute('data-to');
                    
                    for (var i = 0; i < CN; i++) {
                        if (i !== idx) HL_line[i].style.opacity = '0.1';
                    }
                    
                    var fromField = svg.querySelector('[data-field="' + fn + '"]');
                    var toField = svg.querySelector('[data-field="' + tn + '"]');
                    if (fromField) fromField.classList.add('selected');
                    if (toField) toField.classList.add('selected');
                }
                
                function deselect() {
                    if (selIdx < 0) return;
                    var g = rg[selIdx];
                    var line = g.querySelector('.dbml-relationship-line');
                    line.classList.remove('selected');
                    selIdx = -1;
                    
                    for (var i = 0; i < CN; i++) {
                        HL_line[i].style.opacity = '';
                    }
                    
                    var sel = svg.querySelectorAll('.dbml-field-row.selected');
                    for (var i = 0; i < sel.length; i++) sel[i].classList.remove('selected');
                }

            })(wraps[wi]); }
            function onFullscreenChange() {
                var fsEl = D.fullscreenElement || D.webkitFullscreenElement;
                var btns = D.querySelectorAll('.dbml-fullscreen-btn');
                for (var i = 0; i < btns.length; i++) {
                    var inFs = fsEl && fsEl.contains(btns[i]);
                    btns[i].setAttribute('title', inFs ? 'Exit fullscreen (Esc)' : 'Fullscreen');
                }
            }
            D.addEventListener('fullscreenchange', onFullscreenChange);
            D.addEventListener('webkitfullscreenchange', onFullscreenChange);
        });
        })();
        """
