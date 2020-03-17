(TeX-add-style-hook
 "csssa2019_valentin-amira"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("article" "letterpaper" "11pt")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("inputenc" "utf8") ("fontenc" "T1") ("ulem" "normalem") ("geometry" "margin=1in")))
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperref")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "article"
    "art11"
    "inputenc"
    "fontenc"
    "graphicx"
    "grffile"
    "longtable"
    "wrapfig"
    "rotating"
    "ulem"
    "amsmath"
    "textcomp"
    "amssymb"
    "capt-of"
    "hyperref"
    "natbib"
    "tikz"
    "float"
    "ragged2e"
    "tabularx"
    "subfig"
    "geometry")
   (LaTeX-add-labels
    "sec:orgac54265"
    "sec:org78256a0"
    "sec:orgeda23d5"
    "sec:org657365d"
    "sec:orgb2ce29b"
    "fig:orgbe3c0a7"
    "sec:org477d8d5"
    "sec:org03bb9d1"
    "sec:org58dacc7"
    "sec:orgb0b6b88"
    "sec:org1a97377"
    "sec:orgfd0cdde"
    "sec:orgb6a48ec"
    "sec:org097db05"
    "tab:org8a0c816"
    "fig:org49f5a1f"
    "tab:orgcc80923"
    "fig:org7d8e959"
    "sec:org57dace3"
    "fig:orgb1afed9"
    "sec:org08fe74e"
    "fig:org168b7a5"
    "sec:orgbe1af86"
    "fig:orgca41e02"
    "sec:org5c5327f")
   (LaTeX-add-bibliographies
    "references"))
 :latex)

