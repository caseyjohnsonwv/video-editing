from moviepy.editor import *
import os
import random
import sys

#parse args
if (len(sys.argv) != 7):
	print("\nERROR: Expected 'edit.py <src_dir> <dest_filename> <inorder/random> <tempo> <hd/uhd> <nosound?>'")
	exit()
	
input_dir = os.getcwd() + "/" + sys.argv[1]
output_file = sys.argv[2]
rand = True if sys.argv[3] == "random" else False
tempo = int(sys.argv[4])
res = (2160, 3840) if (sys.argv[5] == "uhd") else (1080, 1920)
sound = False if (sys.argv[6] == "nosound") else True

#editing setup
total_time = 0.0
short_clips = []
clip_lengths = [120/tempo, 240/tempo, 360/tempo]

#edit loop
print("---\nFound %i clips --> Initializing editor.\n---" % (len(os.listdir(input_dir))))
for filename in os.listdir(input_dir):

	#open new clip
	input_path_full = input_dir + "/" + filename	
	clip = VideoFileClip(input_path_full, target_resolution=res, audio=sound)
	orig_time = clip.duration
	total_time += orig_time
		
	#throw away useless clips
	if (orig_time < clip_lengths[0]):
		continue
	
	#choose a random clip length
	clip_time = clip_lengths[random.randint(0,len(clip_lengths))-1]
	while (clip_time > orig_time):
		clip_time = clip_lengths[random.randint(0,len(clip_lengths))-1]
		
	#choose a random starting point, then cut the clip
	clip_start = random.random()*(orig_time-clip_time)
	clip = clip.subclip(clip_start, clip_start+clip_time)
	
	#save clip
	if (len(short_clips) > 0 and rand):
		short_clips.insert(random.randint(0, len(short_clips)-1), clip)
	else:
		short_clips.append(clip)
	
	#print some clip info
	print("%s (%.1f sec --> %.1f sec)" % (filename, orig_time, clip_time))
	
#concatenate all clips
final_cut = concatenate_videoclips(short_clips)
pct_cut = (1-final_cut.duration/total_time)*100
print("---\nFinal video length: {0:.1f} sec ({1:.2f}% removed)\n---".format(final_cut.duration, pct_cut))

#write final video to output file
final_cut.write_videofile(os.getcwd() + "/%OUTPUTS/" + output_file)