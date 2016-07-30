import os
from sys import argv
from shutil import copyfileobj
import struct


def add_extension(name, extension=".arch"):
    if name.endswith(extension):
        return name
    else:
        return name + extension


def pack(files, archive_name="archive"):
    archive_name = add_extension(archive_name)
    if os.path.isfile(archive_name):
        print "The archive already exists"
        exit(-4)
    result_file = open(archive_name, "ab")

    result_file.write("MAGIC")
    result_file.write(struct.pack("q", len(files)))
    for f in files:
        file_name = f.name.split(os.sep)[-1]
        f.seek(0, os.SEEK_END)
        file_length = f.tell()
        f.seek(0, os.SEEK_SET)
        meta = struct.pack("hq", len(file_name), file_length)
        result_file.write(meta)
        result_file.write(file_name)
        copyfileobj(f, result_file)
        result_file.seek(0, os.SEEK_END)

    result_file.close()


def unpack(archive_name, destination="."):
    try:
        arch = open(archive_name, "rb")
    except IOError:
        print "File not found"

    if not destination.endswith(os.sep):
        destination += os.sep

    signature = arch.read(5)
    if signature != "MAGIC":
        print "This is not an archive of mine"
        exit(-2)
    file_count = struct.unpack("q", arch.read(8))[0]
    for ii in range(file_count):
        meta = struct.unpack("hq", arch.read(16))
        file_name = arch.read(meta[0])
        f = open(destination + file_name, "ab")

        copy_file_part(arch, f, arch.tell(), arch.tell() + meta[1])
        f.close()


def copy_file_part(fsrc, fdst, start, end, buffer_length=1024 * 1024):
    while start != end:
        if end - start > buffer_length:
            buf = fsrc.read(buffer_length)
        else:
            buf = fsrc.read(end - start)
        fdst.write(buf)
        start += len(buf)


def _get_files(name_list):
    files_list = []
    print name_list
    for file_name in name_list:
        if not file_name.startswith(os.sep):
            file_path = os.curdir + os.sep + file_name
        if os.path.isfile(file_path):
            files_list.append(open(file_path, mode="rb"))
    return files_list


def _parameter_checker():
    if argv[1] == "pack":
        pack(_get_files(argv[2:-1]), argv[-1])
    elif argv[1] == "unpack":
        unpack(argv[2], argv[-1])
    else:
        print "Wrong command"
        _print_usage()
        exit(-3)


def _print_usage():
    print "Usage:"
    print "Packing: python filePacker.py pack <source_file_name> [next_source_file_name]... <archive_name>"
    print "Unpacking: python filePacker.py unpack <archive_name> <destination>"


def main():
    if len(argv) < 3:
        print "I need more parameters!"
        _print_usage()
        exit(-1)
    _parameter_checker()


if __name__ == "__main__":
    main()
