from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)
import sys
import os
from os import path

def to_png(parent_folder,file):
    file_path = path.join(parent_folder, file)
    images = convert_from_path(file_path)
    for i, image in enumerate(images):
        fname = path.join('./pngs',file.replace('.pdf',''))+"_"+ str(i) + ".png"
        image.save(fname, "PNG")


def transform_to_png(parent_folder,file):
    try:
        to_png(parent_folder,file)
    except FileNotFoundError:
        os.mkdir('pngs')
        to_png(parent_folder,file)


def main(parent_folder,file):
    transform_to_png(parent_folder,file)

if __name__ == "__main__":
    parent_folder = sys.argv[1]
    file = sys.argv[2]
    main(parent_folder,file)
