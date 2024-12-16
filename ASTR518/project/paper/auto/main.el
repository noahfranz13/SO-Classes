;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "main"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("aastex631" "")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("graphicx" "") ("amsmath" "") ("natbib" "") ("longtable" "")))
   (TeX-run-style-hooks
    "latex2e"
    "aastex631"
    "aastex63110"
    "graphicx"
    "amsmath"
    "natbib"
    "longtable")
   (TeX-add-symbols
    "AJ")
   (LaTeX-add-labels
    "sec:method"
    "tab:obs"
    "fig:targ"
    "fig:aperture-counts"
    "eq:f0"
    "sec:res"
    "tab:res"
    "sec:snr_theory"
    "eq:snr"
    "sec:snr_obs"
    "fig:lc"
    "sec:conclusion")
   (LaTeX-add-bibliographies))
 :latex)

