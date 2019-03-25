from moviepy.editor import *
import os
import random
import sys

#parse args
if (len(sys.argv) != 8):
	print("\nERROR: Expected 'edit.py <src_dir> <dest_filename> <inorder/random> <tempo> <audio_t0/None> <end_caps/None> <hd/4k>'")
	exit()
	
input_dir = os.getcwd() + "/" + sys.argv[1]
output_file = sys.argv[2]
rand = True if sys.argv[3] == "random" else False
tempo = int(sys.argv[4])
audio_start = 0.0 if (sys.argv[5].lower() == "none") else float(sys.argv[5])
end_caps = False if (sys.argv[6].lower() == "none") else True
res = (2160, 3840) if (sys.argv[7] == "4k" or sys.argv[7] == "4K") else (1080, 1920)

#editing setup
total_time = 0
short_clips = []
beat = 60/tempo
clip_lengths = [2*beat, 4*beat, 6*beat, 8*beat]
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
		

#add black screen to start/end of video
if (end_caps):
	(h,w) = res
	black_screen = ColorClip(size=(w,h), color=(0,0,0), duration=4*beat)
	short_clips.insert(0, black_screen)
	short_clips.append(black_screen)

#concatenate all clips
final_cut = concatenate_videoclips(short_clips)
pct_used = 100*final_cut.duration/total_time

#overwrite final_cut audio with song choice if the song is long enough
if (song is not None and song.duration >= final_cut.duration):
	
	#find 2 measures before "audio start" time parameter
	measure = 0
	while (measure*4*60/tempo <= audio_start):
		measure += 2
	music_start = (measure-2)*240/tempo
	
	#extend audio backwards from "start" time until long enough
	while (music_start+final_cut.duration > song.end):
		measure -= 1
		music_start = (measure-1)*240/tempo
	
	#cut song and apply to final_cut
	song = song.subclip(music_start, music_start+final_cut.duration)
	final_cut = final_cut.set_audio(song)

#write final video to output file
print("---\nFinal video length: {0:.1f} sec ({1:.2f}% of original {2:.1f} sec).\n---".format(final_cut.duration, pct_used, total_time))
final_cut.write_videofile(os.getcwd() + "/%" + output_file)
