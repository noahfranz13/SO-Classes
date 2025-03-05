;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "Franz_ASTR518_HW1_Edits_texdiff"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "12pt")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("graphicx" "") ("amsmath" "") ("amssymb" "") ("mathalpha" "") ("subfig" "caption=false") ("fancyhdr" "") ("geometry" "margin=1in" "headsep=36pt") ("hyperref" "") ("cancel" "") ("natbib" "") ("longtable" "")))
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "href")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
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
    "tab:tdes")
   (LaTeX-add-pagestyles
    "hdr"))
 :latex)

