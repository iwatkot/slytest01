import os
import argparse

from collections import namedtuple

import cv2

from log_handler import Logger, LogTemplates, runtime

logger = Logger(__name__)

# Preparing examples of named tuples for convenient access to the data.
Sizes = namedtuple("Sizes", ["height", "width", "is_percent"])
ImageSize = namedtuple("ImageSize", ["height", "width"])


@runtime
def split_image(image_path: str, window: Sizes,
                stride: Sizes, output_dir: str) -> None:
    """Loads the image from the file and splits it into the segments with
    specified values, using sliding window method.

    Args:
        image_path (str): the path to the original image
        window (Sizes): named tuple, containing size (height, width) of the
            sliding window and a bool is_percent values to determine if the
            sizes are in pixels or percentage
        stride (Sizes): named tuple, containing size (height, width) of the
            stride and a bool is_percent values to determine if the sizes are
            in pixels or percentage
        output_dir (str): the path for output directory, where tiles will be
            written to the files
    """
    # Opening image and cheking if it exists.
    image = cv2.imread(image_path)
    if image is None:
        logger.error(LogTemplates.NO_IMAGE.format(image_path))
        return
    # Extracting filename of the original file without extension.
    image_filename, _ = os.path.splitext(os.path.basename(image_path))

    image_size = ImageSize(*image.shape[:2])
    logger.info(LogTemplates.IMAGE_LOADED.format(height=image_size.height,
                                                 width=image_size.width))

    window_height, window_width = unpack_sizes(image_size, window)
    stride_height, stride_width = unpack_sizes(image_size, stride)

    if not (check_sizes(image_size, window_height, window_width) and
            check_sizes(image_size, stride_height, stride_width)):
        logger.error(LogTemplates.SIZE_ERROR)
        return

    logger.info(LogTemplates.WINDOW_SIZE.format(height=window_height,
                                                width=window_width))
    logger.info(LogTemplates.STRIDE_SIZE.format(height=stride_height,
                                                width=stride_width))

    tile_count = 0
    for x in range(0, image_size.width, stride_width):
        for y in range(0, image_size.height, stride_height):
            # Calculating x, y coordinates for begin and end of the rectangle.
            x1, y1 = x, y
            x2, y2 = x1 + window_width, y1 + window_height

            # Creating tile image from the original file.
            tile = image[y1:y2, x1:x2]
            tile_count += 1

            # Saving the tile image to the file.
            tile_filename = f"{image_filename}_x{x}_y{y}.png"

            cv2.imwrite(os.path.join(output_dir, tile_filename), tile)
    logger.info(LogTemplates.FINISHED.format(count=tile_count))


def unpack_sizes(image_size: ImageSize, sizes: Sizes) -> tuple[int]:
    """Unpacks values from the named tuple and converts percent values to
    pixels if is_percent value in named tuple is True.

    Args:
        image_size (ImageSize): named tuple, containing size of the image
        sizes (Sizes): named tuple, containing values of height and width,
            and bool is_percent value. If the bool value is True, sizes
            will be converted to pixels using image_size.

    Returns:
        tuple[int]: height and width of the object in pixels
    """
    height, width = sizes.height, sizes.width
    if sizes.is_percent:
        height = int(image_size.height * height / 100)
        width = int(image_size.width * width / 100)
    return height, width


def check_sizes(image_size: ImageSize, height: int, width: int) -> bool:
    """Checks if the sizes of the object is lower or equal than image size.

    Args:
        image_size (ImageSize): named tuple, containing size of the image
        height (int): the height of the object in pixels
        width (int): the width of the object in pixels

    Returns:
        bool: Returns False if any of the object's sizes is bigger
            than corresponding image size. Otherwise returns True.
    """
    return (False if width >= image_size.width or
            height >= image_size.height else True)


def parse_arguments() -> argparse.Namespace:
    """Creates parser and reads arguments from the command line.

    Returns:
        argparse.Namespace: An object containing the parsed command-line
            arguments.
    """
    parser = argparse.ArgumentParser(description="Split an image into multiple"
                                     "smaller windows.")
    # Reading arguments from the command line.
    parser.add_argument("--image_path", type=str,
                        help="path to the input image")
    parser.add_argument("--output_dir", type=str,
                        help="path to the output directory")
    parser.add_argument("--window_height", type=int, default=100,
                        help="height of the window")
    parser.add_argument("--window_width", type=int, default=100,
                        help="width of the window")
    parser.add_argument("--window_percent", action="store_true",
                        help="use percentages for window size")
    parser.add_argument("--stride_height", type=int, default=50,
                        help="stride height")
    parser.add_argument("--stride_width", type=int, default=50,
                        help="stride width")
    parser.add_argument("--stride_percent", action="store_true",
                        help="use percentages for stride")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # Creating named tuples for the window and the stride.
    window = Sizes(args.window_height, args.window_width, args.window_percent)
    stride = Sizes(args.stride_height, args.stride_width, args.stride_percent)

    # Creating the output directory.
    os.makedirs(args.output_dir, exist_ok=True)

    split_image(args.image_path, window, stride, args.output_dir)
