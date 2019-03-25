from moviepy.editor import *
import os
import random
import sys

"""
COMMAND LINE ARGS

0: edit.py
1: source directory, relative to current working directory
2: destination file name (including filetype extension); file is placed in current working directory
3: inorder concatenates clips in lexicographical order by name; random is random
4: tempo of the video or music it will be set to (bpm)
5: output resolution; hd is 1080x1920, 4k is 2160x3840; affects export rate
6: nosound disables output video's sound; anything else enables it
"""

#parse args
if (len(sys.argv) != 7):
	print("\nERROR: Expected 'edit.py <src_dir> <dest_filename> <inorder/random> <tempo> <audio_t0/None> <hd/4k>'")
	exit()
	
input_dir = os.getcwd() + "/" + sys.argv[1]
output_file = sys.argv[2]
rand = True if sys.argv[3] == "random" else False
tempo = int(sys.argv[4])
audio_start = None if (sys.argv[5].lower() == "none") else float(sys.argv[5])
res = (2160, 3840) if (sys.argv[6] == "4k" or sys.argv[6] == "4K") else (1080, 1920)

#editing setup
total_time = 0
short_clips = []
clip_lengths = [120/tempo, 240/tempo, 360/tempo, 480/tempo]
song = None

#edit loop
print("---\nFound %i files --> Initializing editor.\n---" % (len(os.listdir(input_dir))))
clip_num = 0
for filename in os.listdir(input_dir):
	input_path_full = input_dir + "/" + filename
	ext = filename[-3:].lower()
	
	if (ext == "mp3" or ext == "wav"):
		song = AudioFileClip(input_path_full)
	
	else:
		#open new clip
		clip = VideoFileClip(input_path_full, target_resolution=res)
		orig_time = clip.duration
		total_time += orig_time
			
		#throw away clips that are too short to use
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
		if (rand and len(short_clips) > 0):
			index = random.randint(0, len(short_clips))
			if (index == len(short_clips)):
				short_clips.append(clip)
			else:
				short_clips.insert(index, clip)
		else:
			short_clips.append(clip)
		
		#print some clip info
		clip_num += 1
		print("%i: %s (%.1f sec --> %.1f sec)" % (clip_num, filename, orig_time, clip_time))
		

#concatenate all clips
final_cut = concatenate_videoclips(short_clips)
pct_cut = (1-final_cut.duration/total_time)*100

#overwrite final_cut audio with song choice if the song is long enough
if (song is not None and song.duration >= final_cut.duration):
	
	#find measure before "audio start" time parameter
	measure = 0
	while (measure*240/tempo <= audio_start):
		measure += 1
	music_start = (measure-1)*240/tempo
	
	#extend audio backwards from "start" time until long enough
	while (music_start+final_cut.duration > song.end):
		measure -= 1
		music_start = (measure-1)*240/tempo
	
	#cut song and apply to final_cut
	song = song.subclip(music_start, music_start+final_cut.duration)
	final_cut = final_cut.set_audio(song)

#write final video to output file
print("---\nFinal video length: {0:.1f} sec ({1:.2f}% removed from original footage).\n---".format(final_cut.duration, pct_cut))
final_cut.write_videofile(os.getcwd() + "/" + output_file)
