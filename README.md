# Bach-Style Music Generator

This project implements a Markov Chain-based music generation system that learns from Bach's compositions and generates new pieces in his style. The system can render the generated pieces using different musical instruments, providing various interpretations of the same musical content.

## Methodology

### 1. Data Processing and Model Architecture

#### 1.1 Data Organization
- The system uses a collection of Bach's MIDI files located in `data/Human/`
- Files are randomly split into training (90%) and testing (10%) sets
- Each MIDI file is processed to extract musical notes and chords

#### 1.2 Musical Representation
- Notes are represented as pitch strings (e.g., "C4", "G5")
- Chords are represented as dot-separated pitch sequences
- The system maintains the temporal sequence of musical events

#### 1.3 Markov Chain Model
- **Sequence Length**: Uses a 4-note context window for predictions
- **State Space**: Each state represents a sequence of 4 consecutive notes/chords
- **Transition Probabilities**: Calculated based on frequency of note sequences in training data
- **Deterministic Generation**: Uses fixed random seeds for reproducible results

### 2. Generation Process

#### 2.1 Model Training
1. Extract notes and chords from MIDI files
2. Build sequences of length 4 (sequence_length)
3. Calculate transition probabilities between states
4. Store the model as a dictionary of state transitions

#### 2.2 Music Generation
1. Start with a deterministically chosen initial sequence
2. Iteratively generate new notes based on transition probabilities
3. Use the last 4 notes as context for the next prediction
4. Generate a fixed-length sequence (default: 200 notes)

#### 2.3 Instrument Rendering
The system supports multiple instrument voices:
- Harpsichord (historically authentic, Program 6)
- Piano (modern interpretation, Program 0)
- Pipe Organ (historically authentic, Program 19)
- String Ensemble (orchestral adaptation, Program 48)
- Violin (Program 40)
- Cello (Program 42)

### 3. Technical Implementation

#### 3.1 Key Components
- **music21**: Handles MIDI file parsing and music theory operations
- **FluidSynth**: Renders MIDI files with different instruments
- **numpy**: Handles probability calculations and random selection
- **joblib**: Provides model persistence capabilities

#### 3.2 File Organization
- Generated pieces are saved in the `generated_pieces/` directory
- Each piece is saved in both MIDI and WAV formats
- Files are named according to their instrument (e.g., `generated_bach_piano.mid`)

### 4. Usage

#### 4.1 Training
```python
generator = BachStyleGenerator(
    data_dir="data/Human",
    soundfont_path="data/FluidR3_GM.sf2",
    seed=FIXED_SEED
)
generator.load_and_split_data()
generator.build_markov_chain()
generator.save_model("bach_model.joblib")
```

#### 4.2 Generation
```python
generator.load_model("bach_model.joblib")
sequence = generator.generate_sequence(length=200, seed=FIXED_SEED)
```

#### 4.3 Rendering
```python
generator.create_midi(sequence, "output.mid", instrument_program)
generator.render_to_audio("output.mid", "output.wav")
```

### 5. Limitations and Future Work

1. **Model Limitations**
   - Fixed context window of 4 notes
   - No explicit handling of musical structure or form
   - Limited to single-voice generation

2. **Potential Improvements**
   - Implement variable-length contexts
   - Add support for multiple voices
   - Incorporate musical theory constraints
   - Add rhythm and dynamics modeling

## Dependencies

- Python 3.x
- music21
- FluidSynth
- numpy
- joblib
- pygame (for playback)

## References

- Bach's MIDI collection
- music21 documentation
- FluidSynth documentation
