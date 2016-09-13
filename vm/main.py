import sys
from read_memory import *
from virt_machine import *
from vm_errors import *
from device import *


def print_error(line, error):
    print("%s: %s" % (line if line is not None else 'GLOBAL', error))


def print_errors(errors):
    for error in errors:
        print_error(error[0], error[1])


def main():
    if len(sys.argv) != 2:  # 1st - program name, 2nd - input filename
        print(ERR_INVALID_ARGS[1])
        return ERR_INVALID_ARGS[0]

    try:
        file_in = open(sys.argv[1], "r")
    except IOError as (errno, strerror):
        print(
            "%s (%s): %s" % (ERR_INVALID_INPUT_FILE[1], sys.argv[1], strerror))
        return ERR_INVALID_INPUT_FILE[0]

    memory, start_address, errors = read_memory(file_in.readlines())
    if len(errors) > 0:
        print(ERR_SYNTAX[1])
        print_errors(errors)
        return ERR_SYNTAX[0]

    vmachine = VMachine(memory, start_address)
    out_file = open("printer.out", "w")
    in_file = open("terminal.in", "r")
    vmachine.set_device(18, FileDevice(mode="w", block_size=24 * 5,
                                       lock_time=24 * 2,
                                       file_object=out_file))  # printer
    vmachine.set_device(19, FileDevice(mode="r", block_size=14 * 5,
                                       lock_time=14 * 2,
                                       file_object=in_file))  # input terminal

    try:
        while not vmachine.halted:
            print("----------------------")
            vmachine.debug_state(sys.stdout)
            vmachine.step()
        print("----------------------")
        vmachine.debug_state(sys.stdout)
    except VMError as error:
        print(ERR_VM_RUN[1])
        print_error(None, error)
        return ERR_VM_RUN[0]

    vmachine.debug_mem(sys.stdout, 128, 150)
    out_file.close()
    in_file.close()


# if we executing module
if __name__ == '__main__':
    main()
