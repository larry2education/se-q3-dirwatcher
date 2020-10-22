#!/usr/bin/env python3
"""
Dirwatcher - A long-running program
"""

__author__ = "Larry Scott, Peter Mayor, and students"

import sys
import os
import argparse
import time
import signal
import logging

exit_flag = False
watch_dict = {}

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
logger = logging.getLogger(__name__)


def search_for_magic(filename, start_line, magic_string, path):
    """Searches within files in the dictionary for magic strings.
    If lines with magic strings are found, the file name and line number
    will be logged only once. 
    """
    with open(path + "/" + filename) as f:
        found_lines = []
        for line_num, line in enumerate(f):
            if line_num <= start_line:
                continue
            found_item = line.find(magic_string)
            watch_dict[filename] = line_num + 1
            if found_item != -1:
                found_lines.append(line_num + 1)
        if len(found_lines) > 0:
            logging.info(
                f"New Magic String Detected In {filename}, Line Numbers: {found_lines}")


def watch_directory(path, magic_string, extension, interval):
    """This function loops through the path to add files ending with .txt  
    to the dictionary. If a file is added, deleted or the path does
    not exist, that infomation will be logged.  
    """
    if not os.path.isdir(path):
        logger.warning(f"Directory {path} Does Not Exist")
        return

    file_list = os.listdir(path)
    for k in list(watch_dict):
        if k not in file_list:
            logger.info(f"File Deleted {k}")
            watch_dict.pop(k)

    for filename in file_list:
        if filename not in watch_dict and filename.endswith(extension):
            logger.info(f"New File Added {filename}")
            watch_dict[filename] = 0
        if filename.endswith(extension):
            search_for_magic(
                filename, watch_dict[filename], magic_string, path)

    return


def create_parser():
    """ Creates a command line argument parser that handles
    the directory to watch, polling interval, file extension
    filter, and magic string.
    """
    parser = argparse.ArgumentParser(description='Dirwatcher items')
    parser.add_argument('dir', help='directory that will be watched')
    parser.add_argument('-i', '--int', default=1,
                        help='seconds between polling')
    parser.add_argument('-e', '--ext', default='txt',
                        help='extension to be watched')
    parser.add_argument('text', help='magic text string to look for')

    arg = parser.parse_args()
    return arg


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically, it just sets a global flag, and main() will exit its loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name

    if signal.Signals(sig_num).name == 'SIGINT':
        logger.warning('Received ' + signal.Signals(sig_num).name)

    if signal.Signals(sig_num).name == 'SIGTERM':
        logger.warning('Received ' + signal.Signals(sig_num).name)

    global exit_flag
    exit_flag = True
    logger.info("Program Shutdown....")
    return


def main(args):
    """Parses args, runs signal and exception handlers"""
    args = create_parser()

    # Hook into these two signals from the OS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    # Now my signal_handler will get called if OS sends
    # either of these to my process.

    logger.info(
        f"Starting to watch directory {args.dir} for text of {args.text}")
    while not exit_flag:
        try:
            watch_directory(args.dir, args.text, args.ext, args.int)
            # print(watch_dict)
            # call my directory watching function
            pass
        except Exception as e:
            logger.error(e)
            # This is an UNHANDLED exception
            # Log an ERROR level message here
            pass

        # put a sleep inside my while loop so I don't peg the cpu usage at 100%
        time.sleep(args.int)

    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start


if __name__ == '__main__':
    main(sys.argv[1:])
