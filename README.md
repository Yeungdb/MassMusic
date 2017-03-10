# MassMusic
Author:
  Darien Yeung (@Yeungdb)

When Mass Spec meets Music

Have you ever wondered how the spectra you collect from Mass Spec would sound like? This script will help you convert the spectra to an audio output that you can listen to or use as samples.

You need to use MSConvert from ProteoWizard to convert you Mass Spec raw files to .txt. Then run the code as follows:

```python MassMusic.py -f {FILE}.txt -o {NameOfOutputfile}.wav```

eg./

```python MassMusic.py -f 20170310_MassSpecExpXYZ.txt -o MassSpecExpXYZ.wav```

Have fun with this new tool!
