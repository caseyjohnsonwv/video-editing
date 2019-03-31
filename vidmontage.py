from moviepy.editor import *
import os
import random
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
if (len(sys.argv) != 8):
	print("\nERROR: Expected 'vidmontage.py <src_dir> <dest_file> <tempo?> <audio_t0?> <speedup?> <end_caps?> <random?>'")
	exit()

rejs = ['no', 'none', 'n', 'f', 'false']
input_dir_short = sys.argv[1]
output_file = sys.argv[2]
tempo = int(parse_arg(sys.argv[3], rejections=rejs, default=120))
audio_start = float(parse_arg(sys.argv[4], rejections=rejs, default=0.0))
speedup = float(parse_arg(sys.argv[5], rejections=rejs, default=1.0))
end_caps = False if not parse_arg(sys.argv[6], rejections=rejs, default=False) else True
rand = False if not parse_arg(sys.argv[7], rejections=rejs, default=False) else True


#editing setup
beat = 60/tempo
twobeats = 2*beat
fourbeats = 4*beat
sixbeats = 6*beat
eightbeats = 8*beat
clip_lengths = [twobeats, fourbeats, sixbeats, eightbeats]
num_cls = len(clip_lengths)
total_time = 0
short_clips = []
song = None
final_cut = None
clip = None


#edit loop
input_dir = os.getcwd() + "/" + sys.argv[1]
print("---\nFound %i files in '%s' --> Initializing editor.\n---" % (len(os.listdir(input_dir)), input_dir_short))
clip_num = 0
for filename in os.listdir(input_dir):
	input_path_full = input_dir + "/" + filename
	ext = filename[-3:].lower()
	
	if (ext == "mp3" or ext == "wav"):
		#save audio file for later
		song = AudioFileClip(input_path_full)
	
	elif (ext == "mp4" or ext == "avi"):
		clip_num += 1
		
		if (clip is not None):
			del clip
		
		#open new clip
		clip = VideoFileClip(input_path_full, target_resolution=(1080,1920), audio=False, fps_source='fps')
		orig_time = clip.duration
		total_time += orig_time
		
		#apply speedup to clip
		if (speedup > 1):
			clip = clip.fx(vfx.speedx, factor=speedup)
			
		#throw away clips that are too short to use
		if (clip.duration < clip_lengths[0]):
			print("%i: %s (%.1f sec --> 0.0 sec) --> Clip too short!" % (clip_num, filename, orig_time))
			clip.close()
			continue
		
		#choose a random clip length
		while True:
			idx = random.randint(0,num_cls)-1
			if clip_lengths[idx] < clip.duration:
				break
		
		#choose a random starting point, then cut the clip
		clip_time = clip_lengths[idx]
		clip_start = random.random()*(clip.duration-clip_time)
		clip = clip.subclip(clip_start, clip_start+clip_time)
		
		#save clip
		if (not rand or clip_num == 1):
			short_clips.append(clip)
		else:
			short_clips.insert(random.randint(0, clip_num), clip)
		
		#print some clip info
		print("%i: %s (%.1f sec --> %.1f sec)" % (clip_num, filename, orig_time, clip_time))
		

#add black screen to start/end of video
if (end_caps):
	short_clips.insert(0, ColorClip(size=(1920, 1080), color=(0,0,0), duration=eightbeats))
	short_clips.append(ColorClip(size=(1920, 1080), color=(0,0,0), duration=eightbeats))

	
#make final cut from all clips
final_cut = concatenate_videoclips(short_clips)
pct_used = final_cut.duration/total_time*100


#overwrite final_cut audio with song choice if the song is long enough
if (not (song is None or song.duration < final_cut.duration)):
	
	#find the measure before the user's audio_t0; will stop at latest allowable start time
	measure = 0
	music_start = 0
	while (not (music_start > audio_start or music_start + final_cut.duration > song.end)):
		measure += 2
		music_start = measure*fourbeats
		
	#cut song and apply fade-in/fade-out
	song = song.subclip(music_start, music_start+final_cut.duration)
	if (end_caps):
		song = afx.audio_fadein(song, eightbeats)
		song = afx.audio_fadeout(song, eightbeats)
	
	#apply song to final_cut
	final_cut = final_cut.set_audio(song)

	
#deallocate unneeded variables to prevent memory swapping
del clip_lengths
del short_clips
del song


#write final video to output file
print("---\nFinal video length: {0:.1f} sec ({1:.2f}% of original {2:.1f} sec).\n---".format(final_cut.duration, pct_used, total_time))
output_path_full = os.getcwd() + "/%" + output_file
final_cut.write_videofile(output_path_full)