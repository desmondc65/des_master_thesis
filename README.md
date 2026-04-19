<!-- Badge for License -->
<div align="right">

  [![](https://img.shields.io/badge/docs-Wiki-F7D360.svg?logo=&style=flat-square)](https://hsins.me/NTU-Thesis/)
  [![](https://img.shields.io/github/license/Hsins/NTU-Thesis.svg?style=flat-square)](./LICENSE)

</div>

<!-- Logo -->
<p align="center">
  <img src="https://i.imgur.com/x2M158J.png" alt="NTU Thesis" height="150px">
</p>

</div>

<!-- Title and Description -->
<div align="center">

# NTU Thesis

📖 _Unofficial LaTeX and Word templates for your master/doctor thesis at National Taiwan University._

![](https://img.shields.io/badge/LaTeX%202%CE%B5-3.14159265-blueviolet?logo=latex&style=flat-square)
![](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg?style=flat-square)
<br>
[![](https://img.shields.io/badge/GitHub%20Actions%20-Open%20as%20Template-2088ff?logo=github-actions&style=flat-square)](https://github.com/Hsins/NTU-Thesis-CI/)
[![](https://img.shields.io/badge/Overleaf%20-Open%20as%20Template-46a247?logo=overleaf&style=flat-square)](https://www.overleaf.com/latex/templates/national-taiwan-university-thesis-template/hvfybyfxgztt)

</div>

## Structures

```
├── back
│   ├── appendix-*.tex              // 附錄
│   ├── references.bib              // 參考文獻
│   └── ...
├── contents
│   ├── chapter-*.tex               // 論文內容
│   └── ...
├── figures
│   └── ...
├── fonts
│   ├── chinese
│   │   ├── BiauKai.ttf             // 標楷體
│   │   ├── Arphic-*.ttf            // 文鼎字體
│   │   ├── MOE-*.ttf               // 教育部字體
│   │   ├── WHZ-*.ttf               // 王漢宗字體
│   │   ├── cwTeX-*.ttf             // cwTeX 字體
│   │   └── ...
│   └── english
│       ├── Times New Roman-*.ttf   // Times New Roman 字體
│       └── ...
├── front
│   ├── abstract.tex                // 摘要
│   ├── acknowledgement.tex         // 致謝
│   └── denotation.tex              // 符號列表
├── main.tex                        // 主文件
├── ntusetup.tex                    // 模板設定
├── ntuthesis.cls                   // 模板文件
└── ...
```

## Building on Linux

This template uses **XeLaTeX** (required for the CJK fonts bundled under `fonts/`) together with **BibTeX** for the bibliography. On Debian/Ubuntu, install a TeX Live distribution that includes XeTeX, `latexmk`, and the usual font/graphics packages:

```bash
sudo apt update
sudo apt install -y \
    texlive-xetex \
    texlive-latex-extra \
    texlive-fonts-extra \
    texlive-lang-chinese \
    texlive-publishers \
    texlive-science \
    texlive-bibtex-extra \
    biber \
    latexmk \
    fonts-noto-cjk
```

On Fedora:

```bash
sudo dnf install -y texlive-scheme-full latexmk
```

On Arch:

```bash
sudo pacman -S texlive-most texlive-lang biber
```

If you prefer the upstream TeX Live installer (recommended if your distro ships an old version), follow <https://www.tug.org/texlive/quickinstall.html> and make sure `tlmgr` is on your `PATH`.

### Compile

From inside the template directory:

```bash
# one-shot
latexmk -xelatex -bibtex main.tex

# or the manual four-pass sequence
xelatex main.tex
bibtex  main
xelatex main.tex
xelatex main.tex
```

`latexmk -c` cleans auxiliary files; `latexmk -C` also removes the final PDF.

## License

Licensed under the MIT License, Copyright © 2017-present Hsins.
