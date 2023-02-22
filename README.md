<a href="https://codeclimate.com/github/iwatkot/slytest01/maintainability"><img src="https://api.codeclimate.com/v1/badges/0db7338bb82431b7cf00/maintainability" /></a>

## Overview
The repo contains of the two scripts, which are designed to work with **Sliding window** method for splitting the image into the tiles, and after recreates the image and check if the merged image has any diffrerences from the original file. Both scripts are built on `cv2`, the script for merging the image is also using `numpy`. In addition the repo contains a simple logger, which uses Python's built-in logging module, and writes logs both to the file and stdout. The log_handler module is also contains a decorator for measuring the runtime of the functions.<br>

## Get started
_Bot of the scripts are designed to be launched from the command line with different arguments._<br><br>
**Example of splitting the image:** `python3 split_image.py --image_path path/to/file --output_dir path/to/output/dir --window_height  --window_width  --stride_height  --stride_width `<br>
Where **--image_path** and **--output_dir** are requried, other arguments have a default values and can be skipped while launching the script.<br>
<br>
Full list of split_image optional arguments:<br>

`--window_height`: the height of the sliding image. Has a default value of 100 pixels.<br>
`--window_width`: the width of the sliding image. Has a default value of 100 pixels.<br>
`--window_percent`: use this argument if you want to specify window's height and width in percents, not pixels.<br>
`--stride_height`: the height of the stride for sliding window. Has a default value of 100 pixels.<br>
`--stride_width`: the width of the stride for sliding window. Has a default value of 100 pixels.<br>
`--stride_percent`: same as window_percent, use it if you want to specify stride's height and width in percents, not pixels.<br>
<br>

**Example of merging the image:**  `python3 merge_image.py --input_dir ./output --output_path result.png --test_file test.jpg`<br>
Where all three arguments are required: input directory which contains image tiles, output path for the merged file and the path to the original file to verify that there's no difference between files.<br>
<br>

## Asciinema examples
**Splitting the image:**<br>
[![asciicast](https://asciinema.org/a/HHz9izJQoXpu3QIHNeHdGwLiP.svg)](https://asciinema.org/a/HHz9izJQoXpu3QIHNeHdGwLiP)<br>
<br>
**Merging the image:**<br>
[![asciicast](https://asciinema.org/a/MTsB1oqP2ZrNMYNYobcqc6flo.svg)](https://asciinema.org/a/MTsB1oqP2ZrNMYNYobcqc6flo)<br>
<br>

## Report
Since I wasn't familiar with the details of the sliding window method, the approach for solving the problem started with researching how the solution should met the requirements of the method.<br>
After I understood the basics of the method, I faced the challenge of storing the splitted tiles coordinates after the original image was splitted. I decided that easiest solution for this problem will be is to store the coordinates right in the tile filename and then parse filenames and extract the coordinates from them. In addition to it I spent some time while trying to find out a good solution for working with input arguments such as window size. I considered that named tuple will be a good option for this, since I can use dot notation for accessing height and width values, without creating extra variables or using index numbers. The named tuple come in handy when I decided to store is_percent argument in the same object for easy-to-understand code such as: if sizes.is_percent. Mostly, after those decisions I don't faced any challenges while working on a split_image.py.<br>
But the challenges appear when I first tried to merge the tiles back. At first I started with easiest approach: find images with same X or Y coordinates and merge them into the one column or a row, and after it merge those files into original size. On final stages of developing a "raw" version of this algorithm I fully understand that this solution is bad in so many ways, and it will be slow, generate a lot of side effects, and the code will be much more harder to understand. So I jumped back to the beginning and start to thinking about solution, which will create the image at once. I started to looking for solutions and suggested that I may try to use numpy arrays. It turned out that this solution is way more easier to implement and understand from code, than it seemed at first. And it's worked perfectly, it recreated the image, which looked exactly the same as original file. But it was until I checked the difference between the files.<br>
And they were. I was kind of frustrated since the images looked exactly the same, I even tried to check it manually with a huge zoom, but didn't manage to find any differences at all. The images was looking exactly the same, but they weren't the same. So I started my research. Firstly, I used cv2.absdiff() to check if I may found any visual differences between the images. After that it was obvious that I would never see those difference just by checking the files, because the difference I faced was just barely distinguishable artifacts, which, I assume, appeared because of the jpg compression. At first I tried to specify the jpg image quality, but it's just turned my work into "guess the compression" game. So I decided to move from jpg to png files and it's work perfectly. There's no artifacts and the script can start working with jpg file, split it into the png, than recreate original to png format and there will be no differences between original jpg and merged png file.

## Nice to know
Both of the scripts has only a few checks for the input parameters. It's obvious that there's a lot of edge cases, such as extra small, zero or even a negative number window or stride sizes, but I wasn't implementing those checks in this case, since they just look like "show that you can think about it and then turn the code into a mess of checks that may have never be needed". So it's easy to get some errors just by providing the script obviosly wrong parameters. On the other hand I've implemented some useful checks (for example, cheking if the image size are smaller than image), which can be handy even the wrong parameters was sent witout anyt malicious intent.