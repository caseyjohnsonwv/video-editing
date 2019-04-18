from moviepy.editor import *
import os
import sys


"""
ARGUMENT PARSING FUNCTION
"""

def parse_arg(arg, rejections=[], default=None):
	arg = arg.lower()
	for test in rejections:
		if (arg == test):
			return default
	return arg
	
	
	
"""
BEGIN MAIN SCRIPT
"""

#parse args
if (len(sys.argv) != 6):
	print("\nERROR: Expected 'vidcut.py <src_path> <dest_file> <start_time> <end_time> <use_cutout?>'")
	exit()
	
rejs = ['no', 'none', 'n', 'f', 'false']
input_file = sys.argv[1]
output_file = sys.argv[2]
start_time = float(parse_arg(sys.argv[3], rejs, 0))
end_time = float(parse_arg(sys.argv[4], rejs, -1))
include = False if not parse_arg(sys.argv[5], rejs, False) else True

#cut setup
clip = None

#open clip
input_file = os.getcwd() + "/" + input_file
clip = VideoFileClip(input_file, target_resolution=(1080,1920))
start_time = max(start_time, 0)
end_time = min(end_time, clip.duration)

if include:
	clip = clip.subclip(start_time, end_time)
else:
	clip1 = clip.subclip(0, start_time)
	clip2 = clip.subclip(end_time, clip.duration)
	clip = concatenate_videoclips([clip1, clip2])

#export video
print("---\nNew clip length: {0:.1f} sec.\n---".format(clip.duration))
output_path_full = os.getcwd() + "/%" + output_file
clip.write_videofile(output_path_full)