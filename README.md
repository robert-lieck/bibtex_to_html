# Bibtex to HTML
This script takes a `bibtex` file with links to local PDF files and creates a folder containing a static webpage and copies of the PDF files. The webpage contains a literature list in `LaTeX` style with additional links to the PDF files. You can simply copy over the folder to your webserver to publish your literature list.

## Running the script

Run the script by calling

```python path/to/make.py literature```

in a folder containing (modified) copies of `literature.tex`, `literature.bib`, and `config.json`. You need to have a working `python` and `LaTeX` installation for this to work. On Windows you will need to adapt `file_prefix` in `config.json` (see below).

## Dependencies

All dependencies should come with a basic `python` and `LaTeX` installation. Specifically, the following python packages are used

```sys, os, pathlib, shutil, subprocess, re, json```

and you will need `pdflatex`, `biblatex`, `biber`, and `tex4ht/htlatex`.

## Workflow

The script first compiles [literature.tex](literature.tex) using `pdflatex` and `biblatex` with `biber` backend by running

1. `pdflatex`
2. `pdflatex`
3. `biber`
4. `pdflatex`
5. `pdflatex`

to produce a literature list as `literature.pdf`. After that the `htlatex` command from the `tex4ht` package is used to generate an HTML version `literature.html`. The generated output contains special tags for the `file` fields in the `bibtex` entries.

The HTML file is then post-processed to extract the actual file paths, copy the files in a separate folder and produce a copy of `literature.html` with relative links to these local files.

**Example:** The file [literature.bib](literature.bib) is compiled to [literature.html](literature/literature.html).

## Zotero integration

If you are using `Zotero` with the `Better BibTeX` plugin, maintaining your literature list becomes particularly easy:

1. add all items to a (sub-)collection
2. add local PDF files to each item
3. export (and optionally `keep updated`) using the `Better BibLaTeX` format.

This will automatically add links to your local PDF files to the `bibtex` entries.

## Configuration and tweaking

### config.json

If you do not want the full path (including you home directory etc; see [literature.html](literature/literature.html)) to re-appear in the HTML you should replace `file_prefix` by the real absolute path to your Zotero storage (or where ever your PDF files are stored). Also, on Windows the default value of `/` for the root directory will probably not work.

The other values in `config.json` mean the following:

```"split_token": "#[PDF]#"```

- the token right before and after the file information, defined in `literature.tex`.

```"encoding": "iso-8859-1"```

- the encoding produced by `htlatex`, this is also specified in the HTML file and might be important if you encounter problem with special characters and the like

```"file_link_start": "<a \nhref=\""```
```"file_link_mid": "\" class=\"url\" ><span \nclass=\"cmtt-12\">"```
```"file_link_end": "</span></a>"```

- `htlatex` transforms the file information into a link with link text; this is the remaining HTML code in between the `split_token` separators, that are not just the file name

```"pdf_dir": "pdfs"```

- the subdirectory in which to copy the local PDF files

### literature.tex

`literature.tex` is a standard `LaTeX` file with some customisations for the `BibLaTeX` output, especially the different sections of the literature list. You can adapt it to your needs.

### literature.bib

`literature.bib` is a standard `bibtex` file with two exceptions:

1. It should contain `file` field for PDFs to be linked. Multiple PDF files can be separated by a semicolon `;`, which is how Zotero exports multiple attachments.

2. You can use the `author+an` field to specify highlighting of authors:

   ```author+an = {1=highlight}```

   will highlight the first author etc. In Zotero you can add this information by specifying

   ```bibtex*{'author+an':'1=highlight'}```

   in the `Extra` field.