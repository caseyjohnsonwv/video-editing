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
if (len(sys.argv) != 4):
	print("\nERROR: Expected 'vidconcat.py <src_dir> <dest_file> <black_cuts?>'")
	exit()
	
rejs = ['no', 'none', 'n', 'f', 'false']
input_dir_name = sys.argv[1]
output_file = sys.argv[2]
black_cuts = False if not parse_arg(sys.argv[3], rejections=rejs, default=False) else True

#concat setup
total_time = 0
clip = None
clip_list = []
blackscreen = ColorClip(size=(1920, 1080), color=(0,0,0), duration=1.0)

#open every clip
input_dir = os.getcwd() + "/" + input_dir_name
print("---\nFound %i files in '%s' --> Initializing editor.\n---" % (len(os.listdir(input_dir)), input_dir_name))
clip_num = 0
for filename in os.listdir(input_dir):
	clip_num += 1
	
	if (clip is not None):
		del clip
		
	clip = VideoFileClip(input_dir + "/" + filename, target_resolution=(1080,1920), audio=True, fps_source='fps')
	clip_list.append(clip)
	total_time += clip.duration
	
	print("%i: %s (%.1f sec)" % (clip_num, filename, clip.duration))
	
	#add black screen after every clip, if desired
	if (black_cuts):
		clip_list.append(blackscreen)

#add black screens to start/end
clip_list.insert(0, blackscreen)
if (not black_cuts):
	clip_list.append(blackscreen)

#concat clips
final_cut = concatenate_videoclips(clip_list)
del clip_list
del blackscreen
del clip

#export video
print("---\nFinal video length: {0:.1f} sec.\n---".format(final_cut.duration))
output_path_full = os.getcwd() + "/%" + output_file
final_cut.write_videofile(output_path_full)