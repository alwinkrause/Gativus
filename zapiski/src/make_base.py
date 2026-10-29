# -*- coding: utf-8 -*-
"""Пустой ODT со стилями серии Gativus (копия claude/gtrn352/make_base.py)."""
import os
from odf.opendocument import OpenDocumentText
from odf.style import (Style, TextProperties, ParagraphProperties,
                       TableProperties, TableCellProperties,
                       ListLevelProperties, FontFace, PageLayout,
                       PageLayoutProperties, HeaderStyle, FooterStyle,
                       HeaderFooterProperties, MasterPage, Footer, FooterLeft,
                       TabStops, TabStop, ListLevelLabelAlignment)
from odf.text import (P, Span, PageNumber, Tab, OutlineStyle,
                      OutlineLevelStyle)
from odf.namespaces import FONS

HERE = os.path.dirname(os.path.abspath(__file__))


def make(book_name, out):
    doc = OpenDocumentText()
    for n, fam, gen, pitch in (("Liberation Sans", "'Liberation Sans'", "swiss", "variable"),
                               ("Liberation Serif", "'Liberation Serif'", "roman", "variable"),
                               ("Liberation Mono", "'Liberation Mono'", "modern", "fixed"),
                               ("Arial", "Arial", "swiss", "variable")):
        doc.fontfacedecls.addElement(FontFace(name=n, fontfamily=fam,
                                              fontfamilygeneric=gen,
                                              fontpitch=pitch))
    S = doc.styles.addElement
    hb = Style(name="Heading", family="paragraph", parentstylename="Standard",
               nextstylename="Text_20_body", displayname="Heading")
    hb.addElement(ParagraphProperties(margintop="0.1665in",
                                      marginbottom="0.0835in",
                                      keepwithnext="always",
                                      contextualspacing="false"))
    hb.addElement(TextProperties(fontname="Liberation Sans",
                                 fontfamily="'Liberation Sans'",
                                 fontfamilygeneric="swiss",
                                 fontpitch="variable", fontsize="14pt"))
    S(hb)
    tb = Style(name="Text_20_body", family="paragraph",
               parentstylename="Standard", displayname="Text body")
    tb.addElement(ParagraphProperties(margintop="0in", marginbottom="0.0972in",
                                      lineheight="115%", textalign="justify",
                                      contextualspacing="false"))
    tb.addElement(TextProperties(fontsize="11pt"))
    S(tb)
    fn = Style(name="Footnote", family="paragraph", parentstylename="Standard",
               displayname="Footnote")
    fn.addElement(ParagraphProperties(margintop="0in", marginbottom="0.02in",
                                      lineheight="105%", textalign="justify",
                                      marginleft="0.16in", textindent="-0.16in",
                                      contextualspacing="false"))
    fn.addElement(TextProperties(fontsize="9pt"))
    S(fn)
    for name, color, size, extra in (("Heading_20_1", "#355269", "130%", True),
                                     ("Heading_20_2", "#3465a4", "115%", False),
                                     ("Heading_20_3", "#5983b0", "101%", False)):
        lvl = name[-1]
        h = Style(name=name, family="paragraph", parentstylename="Heading",
                  nextstylename="Text_20_body",
                  displayname="Heading " + lvl, defaultoutlinelevel=lvl)
        kw = dict(margintop="0.1665in" if lvl == "1" else
                  ("0.139in" if lvl == "2" else "0.0972in"),
                  marginbottom="0.0835in", contextualspacing="false")
        if extra:
            kw["breakbefore"] = "page"
        h.addElement(ParagraphProperties(**kw))
        h.addElement(TextProperties(color=color, fontsize=size,
                                    fontweight="bold"))
        S(h)
    st = Style(name="Strong_20_Emphasis", family="text",
               displayname="Strong Emphasis")
    st.addElement(TextProperties(fontweight="bold")); S(st)
    em = Style(name="Emphasis", family="text")
    em.addElement(TextProperties(fontstyle="italic")); S(em)
    cap = Style(name="Caption", family="paragraph", parentstylename="Standard")
    cap.addElement(ParagraphProperties(margintop="0.0835in",
                                       marginbottom="0.0835in",
                                       textalign="center",
                                       contextualspacing="false"))
    cap.addElement(TextProperties(fontsize="11pt", fontstyle="italic"))
    S(cap)
    for name, color, bold in (("P_20_TblHeader", "#ffffff", True),
                              ("P_20_TblData", "#222222", False)):
        s = Style(name=name, family="paragraph", parentstylename="Standard")
        s.addElement(ParagraphProperties(margintop="0in", marginbottom="0in",
                                         orphans="0", widows="0",
                                         contextualspacing="false"))
        kw = dict(color=color, fontname="Arial", fontfamily="Arial",
                  fontsize="10pt")
        if bold:
            kw["fontweight"] = "bold"
        s.addElement(TextProperties(**kw)); S(s)
        k = Style(name=name + "_keep", family="paragraph", parentstylename=name)
        k.addElement(ParagraphProperties(keepwithnext="always")); S(k)
    A = doc.automaticstyles.addElement
    t = Style(name="GativusTable", family="table")
    tp = TableProperties(width="6.5in", marginleft="0in", margintop="0in",
                         marginbottom="0.35in", align="left",
                         writingmode="lr-tb")
    tp.setAttribute("maybreakbetweenrows", "false")
    tp.setAttrNS(FONS, "keep-together", "always")
    t.addElement(tp); A(t)
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
    outline = OutlineStyle(name="Outline")
    for lvl, fmt, pre, suf, disp, follow in (("1", "1", "Глава ", ". ", None, "nothing"),
                                             ("2", "1", " ", ". ", "2", "nothing"),
                                             ("3", "a", " ", ")", None, "space")):
        kw = dict(level=lvl, numformat=fmt, numprefix=pre, numsuffix=suf)
        if disp:
            kw["displaylevels"] = disp
        o = OutlineLevelStyle(**kw)
        lp = ListLevelProperties(listlevelpositionandspacemode="label-alignment")
        lp.addElement(ListLevelLabelAlignment(labelfollowedby=follow))
        o.addElement(lp); outline.addElement(o)
    S(outline)

    for name in ("Footer", "Footer_20_left"):
        f = Style(name=name, family="paragraph", parentstylename="Standard",
                  displayname=name)
        pp = ParagraphProperties(textalign="left", margintop="0in",
                                 marginbottom="0in")
        ts = TabStops()
        ts.addElement(TabStop(position="3.25in", type="center"))
        ts.addElement(TabStop(position="6.5in", type="right"))
        pp.addElement(ts); f.addElement(pp)
        f.addElement(TextProperties(fontname="Liberation Serif",
                                    fontsize="9pt", color="#555555"))
        S(f)
    bs = Style(name="FooterBook", family="text")
    bs.addElement(TextProperties(fontsize="8pt", color="#777777")); A(bs)
    pl = PageLayout(name="GativusPageLayout")
    pl.setAttribute("pageusage", "mirrored")
    pl.addElement(PageLayoutProperties(pagewidth="8.5in", pageheight="11in",
                                       margintop="0.7874in",
                                       marginbottom="0.7874in",
                                       marginleft="0.7874in",
                                       marginright="0.7874in",
                                       printorientation="portrait",
                                       writingmode="lr-tb"))
    pl.addElement(HeaderStyle())
    fs = FooterStyle()
    fs.addElement(HeaderFooterProperties(minheight="0.3in", margintop="0.2in"))
    pl.addElement(fs); A(pl)
    mp = MasterPage(name="Standard", pagelayoutname="GativusPageLayout")
    fo = Footer(); p = P(stylename="Footer")
    p.addElement(PageNumber(selectpage="current", numformat="1"))
    p.addElement(Tab()); p.addElement(Tab())
    p.addElement(Span(stylename=bs, text=book_name)); fo.addElement(p)
    mp.addElement(fo)
    fl = FooterLeft(); p2 = P(stylename="Footer_20_left")
    p2.addElement(Span(stylename=bs, text=book_name))
    p2.addElement(Tab()); p2.addElement(Tab())
    p2.addElement(PageNumber(selectpage="current", numformat="1"))
    fl.addElement(p2); mp.addElement(fl)
    doc.masterstyles.addElement(mp)
    doc.text.addElement(P(stylename="Text_20_body"))
    doc.save(out)
