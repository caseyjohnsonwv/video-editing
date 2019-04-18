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
if (len(sys.argv) != 7):
	print("\nERROR: Expected 'vidconcat.py <src_dir> <dest_file> <audio_start> <audio_end> <fadein_time> <fadeout_time>'")
	exit()
	
rejs = ['no', 'none', 'n', 'f', 'false']
input_dir_name = sys.argv[1]
output_file = sys.argv[2]
audio_start = float(parse_arg(sys.argv[3], rejs, 0))
audio_end = float(parse_arg(sys.argv[4], rejs, 9999999))
fadein_time = float(parse_arg(sys.argv[5], rejs, 0))
fadeout_time = float(parse_arg(sys.argv[6], rejs, 0))

#concat setup
total_time = 0
clip = None
song = None
clip_list = []

#open every clip
input_dir = os.getcwd() + "/" + input_dir_name
print("---\nFound %i files in '%s' --> Initializing editor.\n---" % (len(os.listdir(input_dir)), input_dir_name))
clip_num = 0
for filename in os.listdir(input_dir):
	clip_num += 1
	
	if (clip is not None):
		del clip
		
	ext = filename[-3:].lower()
	if (ext == "mp3" or ext == "wav"):
		#save audio file for later
		song = AudioFileClip(input_dir + "/" + filename)
		clip_num -= 1
		continue
		
	clip = VideoFileClip(input_dir + "/" + filename, target_resolution=(1080,1920))
	clip_list.append(clip)
	total_time += clip.duration
	
	print("%i: %s (%.1f sec)" % (clip_num, filename, clip.duration))

#concat clips
final_cut = concatenate_videoclips(clip_list)

#audio validation
audio_start = max(audio_start, 0)
if (song is not None):
	audio_end = min([audio_end, song.duration, final_cut.duration])

#add black screens and audio fades to start/end
if (fadein_time > 0):
	clip_list.insert(0, afx.volumex(ColorClip(size=(1920, 1080), color=(0,0,0), duration=fadein_time), 0))
	audio_end += fadein_time
if (fadeout_time > 0):
	clip_list.append(afx.volumex(ColorClip(size=(1920, 1080), color=(0,0,0), duration=fadeout_time), 0))
	audio_end += fadeout_time

#overwrite video audio
if song is not None:
	song = song.subclip(audio_start, audio_end)
	if (fadein_time > 0):
		song = afx.audio_fadein(song, fadein_time)
	if (fadeout_time > 0):
		song = afx.audio_fadeout(song, fadeout_time)
	final_cut = final_cut.set_audio(song)

#free memory
del clip_list
del song

#export video
print("---\nFinal video length: {0:.1f} sec.\n---".format(final_cut.duration))
output_path_full = os.getcwd() + "/%" + output_file
final_cut.write_videofile(output_path_full)