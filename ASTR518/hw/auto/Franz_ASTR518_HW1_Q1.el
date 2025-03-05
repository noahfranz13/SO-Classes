;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "Franz_ASTR518_HW1_Q1"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "12pt")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("graphicx" "") ("amsmath" "") ("amssymb" "") ("mathalpha" "") ("subfig" "caption=false") ("fancyhdr" "") ("geometry" "margin=1in" "headsep=36pt") ("hyperref" "") ("cancel" "") ("natbib" "") ("longtable" "")))
   (TeX-run-style-hooks
    "latex2e"
    "article"
    "art12"
    "graphicx"
    "amsmath"
    "amssymb"
    "mathalpha"
    "subfig"
    "fancyhdr"
    "geometry"
    "hyperref"
    "cancel"
    "natbib"
    "longtable")
   (TeX-add-symbols
    "title"
    "author"
    "duedate"
    "class")
   (LaTeX-add-labels
    "tab:motivation"
    "tab:tdes"))
 :latex)

