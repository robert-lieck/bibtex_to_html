import sys
import os
import pathlib
import shutil
import subprocess
import re
import json


def compile_to_html(file_name_base):
    pdflatex_command = ["pdflatex",
                        "-file-line-error",
                        # "-shell-escape",
                        # "--synctex=1",
                        "-interaction=nonstopmode",
                        file_name_base]
    biber_command = ["biber", file_name_base]
    html_commend = ["htlatex", file_name_base]
    subprocess.run(pdflatex_command)
    subprocess.run(pdflatex_command)
    subprocess.run(biber_command)
    subprocess.run(pdflatex_command)
    subprocess.run(pdflatex_command)
    subprocess.run(html_commend)


def post_process_html(file_name_base, cwd):
    config = json.load(open('config.json'))
    # remove and re-create output directory
    rel_out_dir = file_name_base
    abs_out_dir = os.path.join(cwd, rel_out_dir)
    if os.path.isdir(abs_out_dir):
        shutil.rmtree(abs_out_dir)
    os.makedirs(abs_out_dir)
    # copy css
    shutil.copyfile(file_name_base + ".css", os.path.join(abs_out_dir, file_name_base + ".css"))
    # read file
    file_content = open(file_name_base + ".html", 'rb').read().decode(encoding=config['encoding'])
    # open output file (same name but in output directory
    out_file = open(os.path.join(abs_out_dir, file_name_base + ".html"), 'wb')
    # convert to pathlib Path objects
    rel_out_dir = pathlib.Path(rel_out_dir)
    abs_out_dir = pathlib.Path(abs_out_dir)
    # split at pdf tokens and replace
    for idx, section in enumerate(file_content.split(config['split_token'])):
        # only every second section corresponds to pdf
        if idx % 2 == 0:
            pass
        # if section is empty ignore (remains empty)
        elif section == '':
            pass
        else:
            # get list of files from section
            file_path_regex = re.compile('^' +
                                         config['file_link_start'] +
                                         '([^' + config['file_link_mid'][0] +
                                         ']+)' +
                                         config['file_link_mid'] +
                                         '([^' +
                                         config['file_link_end'][0] +
                                         ']+)' +
                                         config['file_link_end'] +
                                         '$')
            file_list = file_path_regex.search(section).group(1).split(";")
            # fill section with new content
            section = ""
            # go through files
            for file in file_list:
                if not file.endswith(".pdf"):
                    # ignore non-pdf files
                    continue
                if section == "":
                    # open bracket on first entry
                    section = "["
                else:
                    # add space between entries
                    section += " "
                # get paths for copying and referencing pdfs
                orig_file_path = pathlib.Path(file)
                prefix = pathlib.Path(config['file_prefix'])
                if orig_file_path.parts[:len(prefix.parts)] != prefix.parts[:]:
                    raise UserWarning(f"File prefix does not match\n"
                                      f"    prefix: {prefix}\n"
                                      f"    actual path: {orig_file_path}")
                new_abs_file_path = pathlib.Path('/').joinpath(*abs_out_dir.parts[:],
                                                               config['pdf_dir'],
                                                               *orig_file_path.parts[len(prefix.parts):])
                new_rel_file_path = pathlib.Path('.').joinpath(*rel_out_dir.parts[1:],
                                                               config['pdf_dir'],
                                                               *orig_file_path.parts[len(prefix.parts):])
                # print(f"orig_file_path: {orig_file_path}")
                # print(f"prefix: {prefix}")
                # print(f"abs_out_dir: {abs_out_dir}")
                # print(f"rel_out_dir: {rel_out_dir}")
                # print(f"new_abs_file_path: {new_abs_file_path}")
                # print(f"new_rel_file_path: {new_rel_file_path}")
                # create containing directory and copy file
                os.makedirs(new_abs_file_path.parent)
                shutil.copyfile(orig_file_path, new_abs_file_path)
                # add relative link to file
                section += r'''<a href="''' + str(new_rel_file_path) + r'''">PDF</a>'''
            if section != "":
                # close bracket if any file was referenced
                section += "]"
        # write to out file
        out_file.write(section.encode(encoding=config['encoding']))


if __name__ == '__main__':
    # check number of arguments
    if len(sys.argv) < 2:
        print("please specify file name without extension")
        exit()
    # get file names and check they actually exist
    file_name_base = sys.argv[1]
    tex_file = file_name_base + ".tex"
    if not os.path.isfile(tex_file):
        print(f"file '{tex_file}' does not exist")
        exit()
    # compile to html
    compile_to_html(file_name_base)
    # post-process html
    post_process_html(file_name_base, os.getcwd())

