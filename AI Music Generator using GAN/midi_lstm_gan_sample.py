# File management
import os

# Data preprocessing
import numpy as np
import pretty_midi

# Pytorch
import torch
import torch.nn as nn # nn - Neural Network

model_name = 'midi_lstm_gan_custom_25000epochs'
model_path = f'models/{model_name}.pth'
generated_midi_folder = 'static/music/generated'

seq_len = 50       # Length of the note sequence generated/evaluated
max_files = 50

input_size = 4    # Dimension of the latent noise vector per time step
hidden_size = 64   # Hidden size for LSTM layers
num_layers = 1

#device='cuda' if torch.cuda.is_available() else 'cpu'
device = 'cpu'

# This function reads midi files, you need to provide path to folder where midi files are stored
# for e.g "C:/Users/<username>/Desktop"
def load_midi(midi_dir, max_files=250):
    midi_files = []
    for file in os.listdir(midi_dir):
        if(len(midi_files)>=max_files):
           break
        midi_file = pretty_midi.PrettyMIDI(os.path.join(midi_dir, file))
        midi_files.append(midi_file)

    print(f"{len(midi_files)} MIDI files loaded!")
    return midi_files

# Save midi file, you need to provide midi data, folder where you want to save midi file and name of the file
def save_midi(midi_file, midi_dir="", filename="0001"):
    while True:
        if(os.path.exists(os.path.join(midi_dir, filename+".mid"))):
            try:
                filename = str(int(filename)+1)
                if(len(filename)<4):
                    filename = "0"*(4-len(filename))+filename
            except:
                filename = filename+"1"
        else:
            break
    filename = filename+".mid"

    midi_file.write(os.path.join(midi_dir,filename))
    print(f"Saved as {filename} at {midi_dir}")
    return midi_file

# This function converts raw midi data into a 3d array which is used to train model
# There  are 4 array's: pitch(key number), volume(how hard that key is pressed), start time(time when note is pressed), duration(how long note is played)
def midi_to_data(midi_file, start=0, end=-1):
    midi_data = []
    for instrument in midi_file.instruments:
        pitch = []      # Key number
        velocity = []   # Volume
        step = []       # Start time betweeen previous and current note
        duration = []   # Duration of current note

        sorted_notes = sorted(instrument.notes[start:end], key= lambda x:x.start)

        prev_note = 0
        for note in sorted_notes:
            d = note.end - note.start
            s = note.start - prev_note
            prev_note = note.start

            pitch.append(note.pitch)
            velocity.append(note.velocity)
            step.append(s)
            duration.append(d)

        midi_data.append([pitch, velocity, step, duration])
    return midi_data

# This function is to convert array back to midi format so it can be saved as file
def data_to_midi(midi_data, instrument_num=1, drum=False):
    midi_file = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=instrument_num, is_drum=drum)

    prev_start = 0

    max_keys = 88
    max_velocity = 127
    max_step = 2
    max_duration = 2

    for note in midi_data:
      note[0] = int(note[0]*max_keys)
      note[1] = int(note[1]*max_velocity)

      if(note[0]>max_keys):
        note[0] = max_keys
      elif(note[0]<0):
        note[0] = 0

      if(note[1]>max_velocity):
        note[1] = max_velocity
      elif(note[1]<0):
        note[1] = 0

      step = note[2]*max_step
      duration = note[3]*max_duration
      start = step + prev_start
      end = start + duration
      prev_start = start

      note = pretty_midi.Note(pitch=note[0], velocity=note[1], start=start, end=end)
      instrument.notes.append(note)

    midi_file.instruments.append(instrument)

    return midi_file

def prepare_sequences(midi_data, seq_len=50, start=0, end=-1, max_notes=-1):
  notes = []

  max_keys = 88
  max_velocity = 127
  max_step = 2
  max_duration = 2

  for midi_file in midi_data[start:end]:
    for instrument in midi_file:
      pitches = [i/max_keys for i in instrument[0]]
      velocities = [i/max_velocity for i in instrument[1]]
      steps = [i/max_step for i in instrument[2]]
      durations = [i/max_duration for i in instrument[3]]

      for i in range(len(pitches)):
        # if(max_notes!=-1 and len(notes)>=max_notes):
        #   return generate_sequences(notes=notes, seq_len=seq_len)

        notes.append([pitches[i], velocities[i], steps[i], durations[i]])

  return generate_sequences(notes=notes, seq_len=seq_len)

def generate_sequences(notes, seq_len):
  sequencesx=[]; sequencesy=[]

  notes_len = len(notes) - (len(notes)%seq_len)
  for i in range(0, notes_len, seq_len):
    sequencesx.append(notes[i:(i+seq_len)])
    sequencesy.append(notes[(i+seq_len)])

  return np.array(sequencesx), np.array(sequencesy)

# this is just some conversion of data or say some extra preprocessing before feeding to the network
def prepare_data(midi_data, seq_len=50, start=0, end=-1):
  x = []; y = []
  notex = []; notey = []

  max_keys = 88
  max_velocity = 127
  max_step = 2
  max_duration = 2

  for midi_file in midi_data[start:end]:
    instrumentx = []; instrumenty = []
    for instrument in midi_file:
      pitches = [i/max_keys for i in instrument[0]]
      velocities = [i/max_velocity for i in instrument[1]]
      steps = [i/max_step for i in instrument[2]]
      durations = [i/max_duration for i in instrument[3]]

      #notex = []; notey = []

      for i in range(len(pitches)-seq_len):
        pitchx = pitches[i:(i+seq_len)]
        velocityx = velocities[i:(i+seq_len)]
        stepx = steps[i:(i+seq_len)]
        durationx = durations[i:(i+seq_len)]

        pitchy = pitches[i+seq_len]
        velocityy = velocities[i+seq_len]
        stepy = steps[i+seq_len]
        durationy = durations[i+seq_len]

        sub_seqx = []
        for j in range(len(pitchx)):
          sub_seqx.append([pitchx[j], velocityx[j], stepx[j], durationx[j]])

        notex.append(sub_seqx)
        notey.append([pitchy, velocityy, stepy, durationy])

      #instrumentx.append(notex); instrumenty.append(notey)

    #x.append(instrumentx); y.append(instrumenty)
  # ShapeX: [len_notes, seq_len, 4]
  # shapeY: [len_notes, 4]
  x = notex; y = notey
  return np.array(x), np.array(y)

class lstmGenerator(nn.Module):
    def __init__(self, input_size, hidden_size, seq_len, num_layers=2):
        """
        Args:
            input_size (int): Dimension of the input noise vector per time step.
            hidden_size (int): Hidden state dimension of the LSTM.
            seq_len (int): Length of the note sequence to generate.
            num_layers (int): Number of LSTM layers.
        """
        super().__init__()
        self.seq_len = seq_len
        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True)
        # Fully connected layer maps LSTM outputs to 4 note features.
        self.fc1 = nn.Linear(hidden_size, 64)
        self.fc2 = nn.Linear(64, input_size)

    def forward(self, x):
        """
        Args:
            x: Input noise tensor of shape (batch_size, seq_len, input_size)
        Returns:
            out: Generated note sequence of shape (batch_size, seq_len, 4)
        """
        # LSTM processing
        lstm_out, _ = self.lstm(x)  # Shape: (batch_size, seq_len, hidden_size)
        # Map each time step's hidden state to note features
        out = self.fc1(lstm_out)     # Shape: (batch_size, seq_len, 4)

        out = torch.relu(out)

        out = self.fc2(out)

        return out

if(__name__=="main"):
  # Instantiate the generator
  generator = lstmGenerator(input_size=input_size, hidden_size=hidden_size, seq_len=seq_len, num_layers=num_layers)
  generator.load_state_dict(torch.load(model_path, weights_only=True))
  print(generator)

  generator.to(device=device)

  generator.eval()  # Set to evaluation mode.

  # Create a random noise tensor (for one melody sequence)
  generate_batch_size = 1
  generate_seq_len = 500 #seq_len
  noise = torch.randn(generate_batch_size, generate_seq_len, input_size).to(device=device)

  # Generate the note sequence (shape: [batch_size, seq_len, 4])
  with torch.no_grad():
      generated_notes = generator(noise)

  print(generated_notes.shape)

  # Remove the batch dimension (resulting shape: [seq_len, 4])
  generated_notes = generated_notes.squeeze(0)
  print(generated_notes.shape)

  # bring data to cpu
  generated_notes.to(device="cpu")

  # .detach() to remove something and .tolist() converts it to python array
  generated = generated_notes.detach().tolist()

  # convert data to midi file and save it
  generated_midi = data_to_midi(generated, instrument_num=1, drum=False)
  save_midi(generated_midi, generated_midi_folder)