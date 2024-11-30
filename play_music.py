import pygame
import time
import sys
from pathlib import Path
from midi2audio import FluidSynth

def convert_to_wav(midi_file, output_wav, soundfont):
    try:
        # Initialize FluidSynth with the specified soundfont
        fs = FluidSynth(sound_font=soundfont)
        # Convert MIDI to WAV
        fs.midi_to_audio(midi_file, output_wav)
        print(f"Successfully converted MIDI to WAV: {output_wav}")
    except Exception as e:
        print(f"Error converting MIDI to WAV: {e}")

def play_midi(midi_file):
    try:
        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.init()
        
        # Load and play the MIDI file
        pygame.mixer.music.load(midi_file)
        pygame.mixer.music.play()
        
        # Wait for the music to play
        while pygame.mixer.music.get_busy():
            time.sleep(1)
            
    except KeyboardInterrupt:
        # Handle user interrupt (Ctrl+C)
        pygame.mixer.music.stop()
        pygame.quit()
        print("\nPlayback stopped by user")
    except Exception as e:
        print(f"Error playing MIDI file: {e}")
        pygame.quit()
    finally:
        pygame.quit()

if __name__ == "__main__":
    midi_file = "data/Human/brand43s.mid"
    wav_file = "bach.wav"
    soundfont = "data/FluidR3_GM.sf2"
    
    if not Path(midi_file).exists():
        print(f"Error: MIDI file '{midi_file}' not found")
        sys.exit(1)
    
    if not Path(soundfont).exists():
        print(f"Error: Soundfont file '{soundfont}' not found")
        sys.exit(1)
        
    # Convert to WAV
    print(f"Converting {midi_file} to WAV format using soundfont: {soundfont}")
    convert_to_wav(midi_file, wav_file, soundfont)
        
    # Play the original MIDI file
    print(f"\nPlaying original MIDI: {midi_file}")
    play_midi(midi_file)
