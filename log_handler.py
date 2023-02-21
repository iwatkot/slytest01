import logging
import os
import sys

from time import perf_counter
from enum import Enum

absolute_path = os.path.dirname(__file__)

os.makedirs(os.path.join(absolute_path, 'logs'), exist_ok=True)

LOG_FORMATTER = "%(name)s | %(asctime)s | %(levelname)s | %(message)s"
LOG_FILE = os.path.join(absolute_path, 'logs/main_log.txt')


class Logger(logging.getLoggerClass()):
    """Handles logging to the file and stroudt with timestamps."""
    def __init__(self, name: str):
        super().__init__(name)
        self.setLevel(logging.DEBUG)
        self.stdout_handler = logging.StreamHandler(sys.stdout)
        self.file_handler = logging.FileHandler(
            filename=LOG_FILE, mode='a')
        self.fmt = LOG_FORMATTER
        self.stdout_handler.setFormatter(logging.Formatter(LOG_FORMATTER))
        self.file_handler.setFormatter(logging.Formatter(LOG_FORMATTER))
        self.addHandler(self.stdout_handler)
        self.addHandler(self.file_handler)


class LogTemplates(Enum):
    """Storing log templates for the split_image.py"""
    NO_IMAGE = "Can't find the image in the path: {}."
    IMAGE_LOADED = "Successfully loaded image. Height: {height} px, "\
        "width: {width} px."
    PERCENT_WINDOW = "Using the window with percent values."
    WINDOW_SIZE = "Window height: {height} px, width: {width} px."
    PERCENT_STRIDE = "Using the stride with percent values."
    STRIDE_SIZE = "Stride height: {height} px, width: {width} px."
    FINISHED = "The script splitted the image into {count} parts."
    SIZE_ERROR = "At least one of the sizes (window or stride) is bigger "\
        "than image size."
    PARTS_READED = "Successfully read {} images in the input directory."
    SIZE_CALCULATED = "Calculated the size of the image to merge. Height: "\
        "{height} px, width: {width} px."
    IMAGE_MERGED = "Successfully merged the image from the splitted parts."
    IMAGE_VERIFIED = "The images successfully passed difference check."
    IMAGE_DIFF = "Found difference in the images."
    IMAGE_MISSING = "Missing at least one of the splitted parts."
    RUNTIME = "The function was executed in {run_time:.6f} seconds."

    def format(self, *args, **kwargs):
        return self.value.format(*args, **kwargs)

    def __str__(self):
        return self.value


def runtime(function: callable) -> callable:
    def wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = function(*args, **kwargs)
        end_time = perf_counter()
        run_time = end_time - start_time
        logger = Logger(__name__)
        logger.info(LogTemplates.RUNTIME.format(run_time=run_time))
        return result
    return wrapper
