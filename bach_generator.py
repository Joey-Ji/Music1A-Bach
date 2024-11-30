import os
import random
import numpy as np
from music21 import converter, instrument, note, chord, stream, pitch
from midi2audio import FluidSynth
from pathlib import Path
import joblib

class BachStyleGenerator:
    def __init__(self, data_dir, soundfont_path, seed=42):
        self.data_dir = data_dir
        self.soundfont_path = soundfont_path
        self.sequence_length = 4  # Number of notes to use as context
        self.model = {}
        self.all_files = []
        self.train_files = []
        self.test_files = []
        self.seed = seed
        
    def load_and_split_data(self, train_ratio=0.9):
        """Load MIDI files and split into train/test sets"""
        self.all_files = [f for f in os.listdir(self.data_dir) if f.endswith('.mid')]
        random.shuffle(self.all_files)
        split_idx = int(len(self.all_files) * train_ratio)
        self.train_files = self.all_files[:split_idx]
        self.test_files = self.all_files[split_idx:]
        print(f"Training files: {len(self.train_files)}")
        print(f"Testing files: {len(self.test_files)}")

    def extract_notes(self, midi_file):
        """Extract notes and chords from a MIDI file"""
        notes = []
        try:
            midi = converter.parse(os.path.join(self.data_dir, midi_file))
            parts = instrument.partitionByInstrument(midi)
            
            if parts:  # file has instrument parts
                notes_to_parse = parts.parts[0].recurse()
            else:  # file has notes in a flat structure
                notes_to_parse = midi.flat.notes
            
            for element in notes_to_parse:
                if isinstance(element, note.Note):
                    notes.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    notes.append('.'.join(str(n) for n in element.normalOrder))
        except Exception as e:
            print(f"Error processing {midi_file}: {str(e)}")
        return notes

    def build_markov_chain(self):
        """Build a Markov chain model from the training data"""
        all_notes = []
        for file in self.train_files:
            notes = self.extract_notes(file)
            all_notes.extend(notes)
        
        for i in range(len(all_notes) - self.sequence_length):
            sequence = tuple(all_notes[i:i + self.sequence_length])
            next_note = all_notes[i + self.sequence_length]
            
            if sequence in self.model:
                if next_note in self.model[sequence]:
                    self.model[sequence][next_note] += 1
                else:
                    self.model[sequence][next_note] = 1
            else:
                self.model[sequence] = {next_note: 1}
        
        # Convert counts to probabilities
        for sequence in self.model:
            total = sum(self.model[sequence].values())
            for note in self.model[sequence]:
                self.model[sequence][note] = self.model[sequence][note] / total

    def generate_sequence(self, length=100, seed=None):
        """Generate a new sequence of notes"""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
            
        # Start with a random sequence from the model
        all_sequences = list(self.model.keys())
        all_sequences.sort()  # Sort to ensure consistent selection with same seed
        current = all_sequences[0]  # Always start with the same sequence
        output = list(current)
        
        for _ in range(length):
            if current in self.model:
                next_notes = list(self.model[current].keys())
                next_probabilities = list(self.model[current].values())
                next_notes.sort()  # Sort to ensure consistent selection with same seed
                next_note = np.random.choice(next_notes, p=next_probabilities)
                output.append(next_note)
                current = tuple(output[-self.sequence_length:])
            else:
                # If sequence not in model, start a new sequence
                current = all_sequences[0]
                output.extend(current)
        
        return output

    def create_midi(self, note_sequence, output_file, instrument_program=0):
        """Create a MIDI file from a sequence of notes"""
        output_stream = stream.Stream()
        
        # Create and configure the instrument
        if instrument_program == 6:  # Harpsichord
            inst = instrument.Harpsichord()
        elif instrument_program == 19:  # Church Organ
            inst = instrument.PipeOrgan()
        elif instrument_program == 48:  # String Ensemble
            inst = instrument.StringInstrument()
            inst.midiProgram = 48
        elif instrument_program == 40:  # Violin
            inst = instrument.Violin()
        elif instrument_program == 42:  # Cello
            inst = instrument.Violoncello()
        else:  # Piano (default)
            inst = instrument.Piano()
        
        # Ensure the instrument program is set
        inst.midiProgram = instrument_program
        output_stream.append(inst)
        
        # Create a part for the instrument
        part = stream.Part()
        part.append(inst)
        
        for pattern in note_sequence:
            if '.' in pattern:  # Chord
                notes = pattern.split('.')
                chord_notes = []
                for current_note in notes:
                    if current_note.isdigit():
                        p = pitch.Pitch()
                        p.midi = int(current_note)
                        n = note.Note(p)
                    else:
                        n = note.Note(current_note)
                    chord_notes.append(n)
                new_chord = chord.Chord(chord_notes)
                new_chord.quarterLength = 0.5
                part.append(new_chord)
            else:  # Note
                if pattern.isdigit():
                    p = pitch.Pitch()
                    p.midi = int(pattern)
                    new_note = note.Note(p)
                else:
                    new_note = note.Note(pattern)
                new_note.quarterLength = 0.5
                part.append(new_note)
        
        # Add the part to the stream
        output_stream.append(part)
        
        # Write to MIDI file
        output_stream.write('midi', fp=output_file)

    def render_to_audio(self, midi_file, output_wav):
        """Convert MIDI to WAV using FluidSynth"""
        fs = FluidSynth(sound_font=self.soundfont_path)
        fs.midi_to_audio(midi_file, output_wav)

    def save_model(self, filename):
        """Save the trained model"""
        joblib.dump(self.model, filename)

    def load_model(self, filename):
        """Load a trained model"""
        self.model = joblib.load(filename)

# Dictionary of instruments and their program numbers
INSTRUMENTS = {
    'harpsichord': 6,      # Harpsichord
    'piano': 0,            # Acoustic Grand Piano
    'pipe_organ': 19,      # Church Organ
    'string_ensemble': 48, # String Ensemble 1
    'violin': 40,          # Violin
    'cello': 42           # Cello
}

if __name__ == "__main__":
    # Set a fixed seed for reproducibility
    FIXED_SEED = 5
    
    # Create output directory
    output_dir = "generated_pieces"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the generator with the seed
    generator = BachStyleGenerator(
        data_dir="data/Human",
        soundfont_path="data/FluidR3_GM.sf2",
        seed=FIXED_SEED
    )
    
    # Load the trained model
    generator.load_model("bach_model.joblib")
    
    # Generate the base sequence once
    print("\nGenerating base sequence...")
    base_sequence = generator.generate_sequence(length=200, seed=FIXED_SEED)
    
    # Generate pieces with different instruments using the same sequence
    print("\nCreating pieces with different instruments...")
    for instrument_name, program_number in INSTRUMENTS.items():
        print(f"\nGenerating piece with {instrument_name}...")
        
        # Create MIDI file using the same sequence
        midi_filename = os.path.join(output_dir, f"generated_bach_{instrument_name}.mid")
        wav_filename = os.path.join(output_dir, f"generated_bach_{instrument_name}.wav")
        
        generator.create_midi(base_sequence, midi_filename, program_number)
        generator.render_to_audio(midi_filename, wav_filename)
        
        print(f"Created {midi_filename} and {wav_filename}")
    
    print(f"\nDone! All files have been saved in the '{output_dir}' directory.")
