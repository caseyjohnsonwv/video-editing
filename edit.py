from moviepy.editor import *
import os
import random
import sys

#parse args
if (len(sys.argv) != 9):
	print("\nERROR: Expected 'edit.py <src_dir> <dest_file> <random?> <tempo?> <audio_t0?> <speedup?> <end_caps?> <4k?>'")
	exit()
	
input_dir_short = sys.argv[1]
output_file = sys.argv[2]
rand = True if sys.argv[3].lower() == "random" or sys.argv[3].lower() == "true" or sys.argv[3].lower() == "yes" else False
tempo = 120 if sys.argv[4].lower() == "none" else int(sys.argv[4])
audio_start = 0.0 if (sys.argv[5].lower() == "none") else float(sys.argv[5])
speedup = None if (sys.argv[6].lower() == "none" or sys.argv[6].lower() == "false" or sys.argv[6].lower() == "no" or float(sys.argv[6]) <= 1) else float(sys.argv[6])
end_caps = False if (sys.argv[7].lower() == "none" or sys.argv[7].lower() == "false" or sys.argv[7].lower() == "no") else True
res = (2160, 3840) if (sys.argv[8].lower() == "4k" or sys.argv[8].lower() == "yes") else (1080, 1920)

#editing setup
total_time = 0
short_clips = []
beat = 60/tempo
twobeats = 2*beat
fourbeats = 4*beat
sixbeats = 6*beat
eightbeats = 8*beat
clip_lengths = [twobeats, fourbeats, sixbeats, eightbeats]
song = None

#markov chain setup (rows can have different sums, this is handled by the number generator)
last_cl_index = -1
markov = [
[2, 3, 2, 0],
[2, 4, 1, 1],
[2, 4, 1, 1],
[2, 5, 3, 0]
]

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
	
	else:
		#open new clip
		clip = VideoFileClip(input_path_full, target_resolution=res)
		orig_time = clip.duration
		total_time += orig_time
		
		#apply speedup to clip
		if (speedup is not None):
			clip = clip.fx(vfx.speedx, factor=speedup)
			
		#throw away clips that are too short to use
		if (clip.duration < clip_lengths[0]):
			clip_num += 1
			print("%i: %s (%.1f sec --> 0.0 sec) ... (Clip could not be used)" % (clip_num, filename, orig_time))
			continue
		
		#choose a random clip length
		new_cl_index = -1
		if (last_cl_index == -1):
			#first clip length is totally random
			new_cl_index = random.randint(0,len(clip_lengths))-1
			while (clip_lengths[new_cl_index] > clip.duration):
				new_cl_index = random.randint(0,len(clip_lengths))-1
				
		else:
			#subsequent clip lengths are chosen by markov chains
			chain = markov[last_cl_index]
			while(new_cl_index == -1 or clip_lengths[new_cl_index] > clip.duration):
				
				#on repeated calcuations, ignore clip lengths that are too long
				if (new_cl_index != -1):
					chain = chain[0:new_cl_index-1]
					
				rand_num = random.randint(sum(chain))
				psum = 0
				i = 0
				while (psum < rand_num):
					psum += chain[i]
					i += 1
				new_cl_index = i
			
		#choose a random starting point, then cut the clip
		clip_time = clip_lengths[new_cl_index]
		clip_start = random.random()*(clip.duration-clip_time)
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
	first_blackscreen = ColorClip(size=(w,h), color=(0,0,0), duration=fourbeats)
	last_blackscreen = ColorClip(size=(w,h), color=(0,0,0), duration=eightbeats)
	short_clips.insert(0, first_blackscreen)
	short_clips.append(last_blackscreen)


#concatenate all clips
final_cut = concatenate_videoclips(short_clips)
pct_used = final_cut.duration/total_time*100

#overwrite final_cut audio with song choice if the song is long enough
if (song is not None and song.duration >= final_cut.duration):
	
	#find the measure before the user's audio_t0; will stop at latest allowable start time
	measure = 0
	music_start = 0
	while (music_start <= audio_start and music_start + final_cut.duration <= song.end):
		measure += 1
		music_start = measure*fourbeats
		
	#cut song and apply fade-in/fade-out
	song = song.subclip(music_start, music_start+final_cut.duration)
	if (end_caps):
		song = afx.audio_fadein(song, fourbeats)
		song = afx.audio_fadeout(song, eightbeats)
	
	#apply song to final_cut
	final_cut = final_cut.set_audio(song)
	

#write final video to output file
print("---\nFinal video length: {0:.1f} sec ({1:.2f}% of original {2:.1f} sec).\n---".format(final_cut.duration, pct_used, total_time))
final_cut.write_videofile(os.getcwd() + "/%" + output_file)
