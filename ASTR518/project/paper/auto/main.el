;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "main"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("aastex631" "")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("graphicx" "")))
   (TeX-run-style-hooks
    "latex2e"
    "aastex631"
    "aastex63110"
    "graphicx")
   (LaTeX-add-labels
    "fig:aperture-counts"
    "fig:targ"
    "tab:res"))
 :latex)

