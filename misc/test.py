
import waveTools
inputString = "hello world"
indexfilepath = r"c:\tmp\skimpyGimpy\waveIndex.zip"
audioString = waveTools.WaveAudioSpelling(inputString, indexfilepath)
outputFile = file("waveOutput.wav", "wb")
outputFile.write(audioString)