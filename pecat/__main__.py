import os
import time
import hexdump
import coloredlogs
import logging
import re

from os.path import abspath, exists

__author__ = "Andrew Bae"
__contact__ = "dev4ndr3w@gmail.com"

log = logging.getLogger(__name__)

coloredlogs.install(
    fmt='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt="%H:%M:%S")

IMAGE_DOS_SIGNATURE = 0x5A4D  # big endian: 0x4D5A


def ifb(byte): return int.from_bytes(byte, byteorder="little", signed=False)

W = 0x02
L = 0x04

class PE:
    IMAGE_DOS_HEADER = {}
    __IMAGE_DOS_HEADER_format__ = ("IMAGE_DOS_HEADER", (
        "W,e_magic", "W,e_cblp", "W,e_cp", "W,e_crlc", "W,e_cparhdr",
        "W,e_minalloc", "W,e_maxalloc", "W,e_ss", "W,e_sp", "W,e_csum",
        "W,e_ip", "W,e_cs", "W,e_lfarlc", "W,e_ovno", "W4,e_res", "W,e_oemid",
        "W,e_oeminfo", "W10,e_res2", "L,e_lfanew"))

    # structure = return initialized provided struct: container
    def __init__(self, filename=""):
        self.invalid = 0
        self.filename = abspath(filename) if exists(filename) else None
        if self.filename is None:
            log.error("Must provide a valid filename")
        if self.parse() == 0:
            log.info("Parsing PE structure was successful")

    def parse(self):
        self.__data__ = open(self.filename, "rb").read()
        i = 0
        self.dos_header_data = self.__data__[:0x40]
        print(hexdump.hexdump(self.dos_header_data))

        self.structure(self.__data__, self.__IMAGE_DOS_HEADER_format__, 0)

    def show_info(self, structure=""):
        if self.invalid == 1:
            log.error("Provided file is not valid")
            return 1
        log.info("IMAGE_DOS_HEADER")
        for element in self.IMAGE_DOS_HEADER:
            print("{:12} {:#x}".format(
                element,
                self.IMAGE_DOS_HEADER[element]))

    def structure(self, data, pe_format, file_offset):
        element_offset = 0
        print(pe_format[0])
        for i in range(len(pe_format[1])):
            element = re.split(",", pe_format[1][i])
            element_name = element[1]
            try:
                element_size = int("".join(re.findall(
                    "\d?\d?\d?\d", element[0])))
            except:
                element_size = 1
            element_format = "".join(re.findall("(W|L)", element[0]))
            element_size = eval("{}*{}".format(element_format, element_size))

            element_data = ifb(data[
                (file_offset+element_offset):
                    (file_offset+element_offset+element_size)])
            exec("self.{}[\"{}\"]={}".format(
                pe_format[0], element_name, element_data))
            element_offset += element_size
