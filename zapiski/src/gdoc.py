# -*- coding: utf-8 -*-
"""Облегчённый GativusDoc (копия claude/gnss351/gdoc.py; рисунки и формулы LibreOffice Math)."""
import re, itertools
from odf.opendocument import load
from odf.style import (Style, TextProperties, TableColumnProperties,
                       TableRowProperties, ListLevelProperties,
                       TableProperties, TableCellProperties)
from odf.text import (H, P, Span, List, ListItem, ListStyle,
                      ListLevelStyleBullet, Note, NoteBody, NoteCitation)
from odf.table import (Table, TableColumn, TableRow, TableCell,
                       TableHeaderRows)
from odf.namespaces import FONS

_ids = itertools.count(1)


class GDoc:
    def __init__(self, base, book_name=None):
        self.doc = load(base)
        self.book_name = book_name
        body = self.doc.text
        for ch in list(body.childNodes):
            body.removeChild(ch)
        self._fn = 0
        self.acr_on = True
        self._mono = Style(name="Mono", family="text")
        self._mono.addElement(TextProperties(
            fontname="Liberation Mono", fontfamily="'Liberation Mono'",
            fontsize="10pt"))
        self.doc.automaticstyles.addElement(self._mono)
        self._table_styles()
        self._index_styles()

    def _table_styles(self):
        A = self.doc.automaticstyles.addElement
        t = Style(name="GativusTable", family="table")
        tp = TableProperties(width="6.5in", marginleft="0in", margintop="0in",
                             marginbottom="0.35in", align="left",
                             writingmode="lr-tb")
        tp.setAttribute("maybreakbetweenrows", "false")
        tp.setAttrNS(FONS, "keep-together", "always")
        t.addElement(tp); A(t)
        tl = Style(name="GativusTableLong", family="table")
        tpl = TableProperties(width="6.5in", marginleft="0in", margintop="0in",
                              marginbottom="0.35in", align="left",
                              writingmode="lr-tb")
        tpl.setAttribute("maybreakbetweenrows", "true")
        tl.addElement(tpl); A(tl)
        for name, bg in (("GativusTblCellHeader", "#1b3a5c"),
                         ("GativusTblCellEven", "#eaf1f8"),
                         ("GativusTblCellOdd", None)):
            c = Style(name=name, family="table-cell")
            kw = dict(paddingleft="0.0833in", paddingright="0.0833in",
                      paddingtop="0.0556in", paddingbottom="0.0556in",
                      border="0.1pt solid #cccccc")
            if bg:
                kw["backgroundcolor"] = bg
            if name.endswith("Header"):
                kw["verticalalign"] = "middle"
            c.addElement(TableCellProperties(**kw)); A(c)

    def _index_styles(self):
        from odf.style import ParagraphProperties as _PP
        A = self.doc.automaticstyles.addElement
        mono = dict(fontname="Liberation Mono", fontfamily="'Liberation Mono'",
                    fontsize="90%")
        self._st = {}
        for it in (False, True):
            for bold in (False, True):
                extra = {}
                if it:
                    extra["fontstyle"] = "italic"
                sfx = ("It" if it else "") + ("B" if bold else "")
                st = Style(name="TAcr" + sfx, family="text")
                st.addElement(TextProperties(
                    fontweight="bold" if bold else "normal", **mono, **extra))
                A(st); self._st[("acr", it, bold)] = st
                st = Style(name="TSubM" + sfx, family="text")
                st.addElement(TextProperties(textposition="sub 62%",
                                             fontweight="bold", **mono, **extra))
                A(st); self._st[("sub", it, bold)] = st
                if it or bold:
                    kw = dict(extra)
                    if bold:
                        kw["fontweight"] = "bold"
                    st = Style(name="TTxt" + sfx, family="text")
                    st.addElement(TextProperties(**kw))
                    A(st); self._st[("txt", it, bold)] = st
        for it in (False, True):
            for bold in (False, True):
                for letter in (False, True):
                    kw = {"textposition": "sub 58%"}
                    if it or letter:
                        kw["fontstyle"] = "italic"
                    if bold:
                        kw["fontweight"] = "bold"
                    st = Style(name="TSubV%d%d%d" % (it, bold, letter),
                               family="text")
                    st.addElement(TextProperties(**kw)); A(st)
                    self._st[("vsub", it, bold, letter)] = st
        fp = Style(name="PFormula", family="paragraph",
                   parentstylename="Text_20_body")
        fp.addElement(_PP(textalign="center", margintop="0.06in",
                          marginbottom="0.10in"))
        A(fp); self._formula_st = fp

    ACR = re.compile(r'(?<![A-Za-z0-9])([A-Z][A-Z0-9]*[A-Z0-9])(?![A-Za-z0-9])')
    ROMAN = re.compile(r'^[IVXL]+$')

    def _span(self, parent, text, kind, it, bold):
        st = self._st.get((kind, it, bold))
        parent.addElement(Span(stylename=st, text=text) if st
                          else Span(text=text))

    def _plain(self, parent, text, it, bold):
        if not self.acr_on:
            self._span(parent, text, "txt", it, bold)
            return
        pos = 0
        for m in self.ACR.finditer(text):
            if self.ROMAN.match(m.group(1)):
                continue
            if m.start() > pos:
                self._span(parent, text[pos:m.start()], "txt", it, bold)
            self._span(parent, m.group(1), "acr", it, bold)
            pos = m.end()
        if pos < len(text):
            self._span(parent, text[pos:], "txt", it, bold)

    def _runs(self, parent, text, it=False, bold=False):
        prev_acr = False
        for tok in re.split(r'(_\{[^}]*\}|\$[^$]+\$)', text):
            if not tok:
                continue
            if tok.startswith('_{'):
                if prev_acr:
                    self._span(parent, tok[2:-1], "sub", it, bold)
                else:
                    for part in re.split(r'([A-Za-z]+)', tok[2:-1]):
                        if part:
                            st = self._st[("vsub", it, bold, part.isalpha())]
                            parent.addElement(Span(stylename=st, text=part))
            elif tok.startswith('$'):
                self._span(parent, tok[1:-1], "txt", True, bold)
                prev_acr = False
            else:
                self._plain(parent, tok, it, bold)
                m = None
                for m in self.ACR.finditer(tok):
                    pass
                prev_acr = bool(m and m.end() == len(tok)
                                and not self.ROMAN.match(m.group(1)))

    def formula(self, t):
        p = P(stylename=self._formula_st); self._runs(p, t); self._add(p)

    def _add(self, el):
        self.doc.text.addElement(el)

    def h1_unnumbered(self, t):
        h = H(outlinelevel=1, stylename="Heading_20_1")
        self._runs(h, t)
        h.setAttribute("islistheader", "true"); self._add(h)

    def h2_unnumbered(self, t):
        h = H(outlinelevel=2, stylename="Heading_20_2")
        self._runs(h, t)
        h.setAttribute("islistheader", "true"); self._add(h)

    def h3_unnumbered(self, t):
        h = H(outlinelevel=3, stylename="Heading_20_3")
        self._runs(h, t)
        h.setAttribute("islistheader", "true"); self._add(h)

    def subtitle(self, t):
        p = P(stylename="Caption")
        p.addElement(Span(stylename="Emphasis", text=t)); self._add(p)

    def page_break(self):
        from odf.style import ParagraphProperties as _PPb
        if not hasattr(self, "_pb_st"):
            st = Style(name="P_20_PageBreak", family="paragraph",
                       parentstylename="Text_20_body")
            st.addElement(_PPb(breakbefore="page", margintop="0in",
                               marginbottom="0in", lineheight="100%"))
            st.addElement(TextProperties(fontsize="2pt"))
            self.doc.automaticstyles.addElement(st)
            self._pb_st = st
        self._add(P(stylename=self._pb_st))

    def blank(self):
        self._add(P(stylename="Text_20_body"))

    def p(self, t):
        p = P(stylename="Text_20_body"); self._inline(p, t); self._add(p)

    def bullets(self, items):
        n = next(_ids)
        ls = ListStyle(name=f"BL_{n}")
        lv = ListLevelStyleBullet(level="1", bulletchar="•")
        lv.addElement(ListLevelProperties(spacebefore="0.25in",
                                          minlabelwidth="0.25in"))
        ls.addElement(lv); self.doc.automaticstyles.addElement(ls)
        ul = List(stylename=ls)
        for it in items:
            li = ListItem(); p = P(stylename="Text_20_body")
            self._inline(p, it); li.addElement(p); ul.addElement(li)
        self._add(ul)

    def table(self, rows, col_widths=None, long=False):
        n = next(_ids); nc = len(rows[0])
        if len(rows) > 8:
            long = True
        if not col_widths:
            col_widths = [round(6.5 / nc, 3)] * nc
        t = Table(stylename="GativusTableLong" if long
                  else "GativusTable")
        for i, w in enumerate(col_widths):
            cs = Style(name=f"C{n}_{i}", family="table-column")
            cs.addElement(TableColumnProperties(columnwidth=f"{w}in"))
            self.doc.automaticstyles.addElement(cs)
            t.addElement(TableColumn(stylename=cs))
        rk = Style(name=f"RK{n}", family="table-row")
        trp = TableRowProperties(keeptogether="always")
        trp.setAttrNS(FONS, "keep-with-next", "always"); rk.addElement(trp)
        rl = Style(name=f"RL{n}", family="table-row")
        rl.addElement(TableRowProperties(keeptogether="always"))
        self.doc.automaticstyles.addElement(rk)
        self.doc.automaticstyles.addElement(rl)
        last = len(rows) - 1
        hdr = None
        for i, row in enumerate(rows):
            glue = (i != last) and not long
            tr = TableRow(stylename=rk if glue else rl)
            k = "_keep" if glue else ""
            for c in row:
                if i == 0:
                    tc = TableCell(stylename="GativusTblCellHeader")
                    p = P(stylename="P_20_TblHeader" + k)
                else:
                    tc = TableCell(stylename="GativusTblCellEven" if i % 2
                                   else "GativusTblCellOdd")
                    p = P(stylename="P_20_TblData" + k)
                self._inline(p, c); tc.addElement(p); tr.addElement(tc)
            if long and i == 0:
                hdr = TableHeaderRows(); hdr.addElement(tr)
                t.addElement(hdr)
            else:
                t.addElement(tr)
        self._add(t)

    def _inline(self, parent, text, notes=True):
        ital = r'_(?!\{)(?:_\{[^}]*\}|[^_])+_(?!\{)'
        pat = (r'(\*\*[^*]+\*\*|`[^`]+`|\[\^[^\]]+\]|' + ital + ')'
               if notes else
               r'(\*\*[^*]+\*\*|`[^`]+`|' + ital + ')')
        for tok in re.split(pat, text):
            if not tok:
                continue
            if tok.startswith('**'):
                self._runs(parent, tok[2:-2], bold=True)
            elif tok.startswith('`'):
                parent.addElement(Span(stylename=self._mono, text=tok[1:-1]))
            elif notes and tok.startswith('[^'):
                self._fn += 1
                note = Note(noteclass="footnote", id=f"ftn{self._fn}")
                note.addElement(NoteCitation(text=str(self._fn)))
                b = NoteBody(); np_ = P(stylename="Footnote")
                np_.addElement(Span(text=" "))
                _acr, self.acr_on = self.acr_on, False
                self._inline(np_, tok[2:-1], notes=False)
                self.acr_on = _acr
                b.addElement(np_); note.addElement(b)
                parent.addElement(note)
            elif tok.startswith('_') and tok.endswith('_') and len(tok) > 2:
                self._runs(parent, tok[1:-1], it=True)
            else:
                self._runs(parent, tok)

    def figure(self, path, width_cm=16.0, height_cm=None, caption=None,
               label="Рис.", brk_before=False, brk_after=False):
        from odf.draw import Frame as _Fr, Image as _Im, TextBox as _TB
        from odf.text import Sequence, SequenceDecls, SequenceDecl
        from odf.style import (GraphicProperties as _GP,
                               ParagraphProperties as _PP)
        if height_cm is None:
            try:
                from PIL import Image as _PI
                with _PI.open(path) as im:
                    w, h = im.size
                height_cm = width_cm * h / w
            except Exception:
                height_cm = width_cm * 0.6
        if not hasattr(self, "_seq"):
            decls = SequenceDecls()
            for nm in ("Illustration", "Table", "Text", "Drawing", "Figure"):
                decls.addElement(SequenceDecl(displayoutlinelevel="0", name=nm))
            self.doc.text.insertBefore(decls, self.doc.text.firstChild)
            self._seq = decls
            self._fig_n = 0
            st = Style(name="P_20_Figure_20_Image", family="paragraph",
                       parentstylename="Standard")
            st.addElement(_PP(textalign="center", margintop="0.12in",
                              marginbottom="0.02in"))
            self.doc.styles.addElement(st)
            cap = Style(name="Figure", family="paragraph",
                        parentstylename="Standard", nextstylename="Standard")
            cap.addElement(_PP(textalign="center", margintop="0.02in",
                               marginbottom="0.18in"))
            cap.addElement(TextProperties(fontsize="10pt", fontstyle="italic",
                                          color="#555555"))
            self.doc.styles.addElement(cap)
        href = self.doc.addPicture(path)
        gs = Style(name="FrFig_%d" % (abs(hash(path)) % 100000), family="graphic",
                   parentstylename="Graphics")
        gs.addElement(_GP(wrap="none", horizontalpos="center",
                          horizontalrel="paragraph", verticalpos="top",
                          verticalrel="paragraph-content"))
        self.doc.automaticstyles.addElement(gs)
        self._fig_n += 1
        n = self._fig_n
        img = _Fr(width="%.2fcm" % width_cm, height="%.2fcm" % height_cm,
                  anchortype="as-char" if caption else "paragraph",
                  stylename=gs, name="Fig_%d" % n)
        img.addElement(_Im(href=href, type="simple", show="embed",
                           actuate="onLoad"))
        if not caption:
            p = P(stylename="P_20_Figure_20_Image"); p.addElement(img)
            self._add(p); return
        outer_st = Style(name="FrBox_%d" % n, family="graphic",
                         parentstylename="Frame")
        outer_st.addElement(_GP(wrap="none", horizontalpos="center",
                                horizontalrel="paragraph", verticalpos="top",
                                verticalrel="paragraph-content",
                                backgroundcolor="transparent", padding="0in",
                                borderlinewidth="none", border="none"))
        self.doc.automaticstyles.addElement(outer_st)
        outer = _Fr(width="%.2fcm" % width_cm, anchortype="paragraph",
                    stylename=outer_st, name="FigBox_%d" % n, zindex="0")
        tb = _TB(minheight="%.2fcm" % height_cm)
        pi = P(stylename="P_20_Figure_20_Image"); pi.addElement(img)
        tb.addElement(pi)
        cp = P(stylename="Figure"); cp.addText(label + " ")
        seq = Sequence(refname="refFigure%d" % (n - 1), name="Figure",
                       formula="ooow:Figure+1", numformat="1")
        seq.addText(str(n)); cp.addElement(seq); cp.addText(": ")
        self._inline(cp, caption)
        tb.addElement(cp)
        outer.addElement(tb)
        hst = "P_20_Figure_20_Image"
        if brk_before or brk_after:
            hs = Style(name="FigHold_%d" % n, family="paragraph",
                       parentstylename="P_20_Figure_20_Image")
            kw = dict(margintop="0in")
            if brk_before:
                kw["breakbefore"] = "page"
            if brk_after:
                kw["breakafter"] = "page"
            hs.addElement(_PP(**kw)); self.doc.automaticstyles.addElement(hs)
            hst = hs
        holder = P(stylename=hst); holder.addElement(outer)
        self._add(holder)

    def figure_page(self, path, caption, max_w_cm=17.0, max_h_cm=19.5,
                    before=True, after=True):
        from PIL import Image as _PI
        with _PI.open(path) as im:
            w, h = im.size
        wc = min(max_w_cm, max_h_cm * w / h)
        self.figure(path, width_cm=wc, height_cm=wc * h / w, caption=caption,
                    brk_before=before, brk_after=after)

    def save(self, path):
        self.doc.save(path)


# --- формулы LibreOffice Math: объекты, сохранённые самим LibreOffice ---
import json as _json, shutil as _shutil, zipfile as _zip
from odf.draw import Frame as _Frame, Object as _Object
from odf.style import ParagraphProperties as _PPf, GraphicProperties as _GPf

_MANI = ('<manifest:file-entry manifest:full-path="{n}/" manifest:version="1.3" '
         'manifest:media-type="application/vnd.oasis.opendocument.formula"/>'
         '<manifest:file-entry manifest:full-path="{n}/content.xml" '
         'manifest:media-type="text/xml"/><manifest:file-entry '
         'manifest:full-path="{n}/settings.xml" manifest:media-type="text/xml"/>')


class GMathDoc(GDoc):
    """GDoc с формулами LibreOffice Math из formulas.json (math_build.py)."""

    def __init__(self, base, formulas):
        super().__init__(base)
        self._fdb = _json.load(open(formulas, encoding="utf-8"))
        self._objs = []
        ps = Style(name="P_20_MathFormula", family="paragraph",
                   parentstylename="Text_20_body")
        ps.addElement(_PPf(textalign="center", margintop="0.06in",
                           marginbottom="0.12in", keepwithnext="auto"))
        gs = Style(name="FrMath", family="graphic")
        gs.addElement(_GPf(verticalpos="middle", verticalrel="text",
                           wrap="none", padding="0in", border="none"))
        self.doc.automaticstyles.addElement(ps)
        self.doc.automaticstyles.addElement(gs)
        self._mps, self._mgs = ps, gs

    def mformula(self, key):
        r = self._fdb[key]
        n = "Object %d" % (len(self._objs) + 1)
        self._objs.append((n, r["content"], r["settings"]))
        fr = _Frame(stylename=self._mgs, anchortype="as-char",
                    width="%.3fcm" % r["w_cm"], height="%.3fcm" % r["h_cm"],
                    name="Formula%d" % len(self._objs))
        fr.addElement(_Object(href="./" + n, type="simple", show="embed",
                              actuate="onLoad"))
        p = P(stylename=self._mps); p.addElement(fr); self._add(p)

    def save(self, path):
        super().save(path)
        if not self._objs:
            return
        tmp = path + ".tmp"
        with _zip.ZipFile(path) as zi, _zip.ZipFile(tmp, "w") as zo:
            for it in zi.infolist():
                data = zi.read(it.filename)
                if it.filename == "META-INF/manifest.xml":
                    add = "".join(_MANI.format(n=n) for n, _, _ in self._objs)
                    data = data.decode().replace(
                        "</manifest:manifest>", add + "</manifest:manifest>").encode()
                zo.writestr(it.filename, data, compress_type=(
                    _zip.ZIP_STORED if it.filename == "mimetype"
                    else _zip.ZIP_DEFLATED))
            for n, c, s in self._objs:
                zo.writestr(n + "/content.xml", c, compress_type=_zip.ZIP_DEFLATED)
                zo.writestr(n + "/settings.xml", s, compress_type=_zip.ZIP_DEFLATED)
        _shutil.move(tmp, path)
