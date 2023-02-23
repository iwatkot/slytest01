import os
import re
import argparse

from collections import defaultdict, namedtuple

import cv2
import numpy as np

from log_handler import Logger, LogTemplates, runtime

logger = Logger(__name__)

# Preparing examples of named tuples for convenient access to the data.
ImageSize = namedtuple('ImageSize', ['height', 'width'])


def get_files(directory: str) -> defaultdict:
    """Creates a defaultdict object, which has keys with X coordinates and as
    values - lists of filenames with same X coordinate sorted by Y coordinate.

    Args:
        directory (str): the path to the directory, containing input tiles

    Returns:
        defaultdict: dictionary, containing collections of filenames with same
            X coordinate as values, and X coordinates as a keys.
    """
    files_dict = defaultdict(list)
    filenames = [f"{directory}/{filename}" for
                 filename in os.listdir(directory)]
    logger.info(LogTemplates.PARTS_READED.format(len(filenames)))

    for filename in filenames:
        files_dict[get_x_coord(filename)].append(filename)

    for key in files_dict:
        # Sorting lists for the key in a dictionary by Y coordonate value.
        files_dict[key] = sorted(files_dict[key], key=get_y_coord)
    return files_dict


def get_image_size(last_image: str) -> ImageSize:
    """Calculates the size of the result image using size and coordinates of
    the last image (right bottom corner).

    Args:
        last_image (str): filename of the last image in grid

    Returns:
        ImageSize: named tuple, containing height and width of the image
            in pixels
    """

    x_coord, y_coord = get_x_coord(last_image), get_y_coord(last_image)

    last_image_height, last_image_width, _ = cv2.imread(last_image).shape
    image_size = ImageSize(y_coord + last_image_height,
                           x_coord + last_image_width)
    return image_size


def get_x_coord(filename: str) -> int:
    """Extracts the X coordinate from the filename.

    Args:
        filename (str): the path to the file to extract the coordinate from

    Returns:
        int: value of the X coordinate
    """
    match = re.search(r'x(\d+)_', filename)
    return int(match.group(1))


def get_y_coord(filename: str) -> int:
    """Extracts the Y coordinate from the filename.

    Args:
        filename (str): the path to the file to extract the coordinate from

    Returns:
        int: value of the Y coordinate
    """
    match = re.search(r'_y(\d+)', filename)
    return int(match.group(1))


@runtime
def merge_image(directory: str, output_path: str) -> None:
    """Merges the image from splitted parts, using path to the directory,
    containing image tiles.

    Args:
        directory (str): the path to the input directory with tile files
        output_path (str): the path for the output image
    """
    filenames = get_files(directory)

    last_image = filenames.get(max(filenames.keys()))[-1]
    image_size = get_image_size(last_image)

    logger.info(LogTemplates.SIZE_CALCULATED.format(height=image_size.height,
                                                    width=image_size.width))

    # Creating an empty NumPy array with dimensions of the merged image.
    merged_image = np.zeros((image_size.height, image_size.width, 3),
                            dtype=np.uint8)

    for image_row in filenames.values():
        for tile in image_row:
            tile_x = get_x_coord(tile)
            tile_y = get_y_coord(tile)

            tile_image = cv2.imread(tile)
            tile_height, tile_width, _ = tile_image.shape

            # Inserting a parts of image into the array with image's coords.
            try:
                merged_image[tile_y: tile_y + tile_height,
                             tile_x: tile_x + tile_width, :] = tile_image
            except ValueError:
                logger.error(LogTemplates.IMAGE_MISSING)

    cv2.imwrite(output_path, merged_image)
    logger.info(LogTemplates.IMAGE_MERGED)


def check_difference(test_file: str, merged_file: str) -> None:
    """Checks the difference between the merged image and test image.

    Args:
        test_file (str): the path to the original file
        merged_file (str): the path to the file after merging
    """
    test_file = cv2.imread(test_file)
    merged_file = cv2.imread(merged_file)

    if np.array_equal(test_file, merged_file):
        logger.info(LogTemplates.IMAGE_VERIFIED)
    else:
        logger.warning(LogTemplates.IMAGE_DIFF)
        diff = cv2.absdiff(test_file, merged_file)
        cv2.imshow("Diff", diff)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def parse_arguments() -> argparse.Namespace:
    """Creates parser and reads arguments from the command line.

    Returns:
        argparse.Namespace: An object containing the parsed command-line
            arguments.
    """
    parser = argparse.ArgumentParser(description="Recreates image after it was"
                                     "splitted with sliding window method.")
    # Reading arguments from the command line.
    parser.add_argument("--input_dir", type=str,
                        help="path to the directory with images")
    parser.add_argument("--output_path", type=str,
                        help="path for the output file")
    parser.add_argument("--test_file", type=str,
                        help="path to the original file for diff check")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    merge_image(args.input_dir, args.output_path)
    check_difference(args.test_file, args.output_path)
