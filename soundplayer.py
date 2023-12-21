from random import choice
import winsound


effect_list = ["effects//1.wav", "effects//2.wav", "effects//3.wav", "effects//4.wav", "effects//5.wav",
               "effects//7.wav", "effects//8.wav", "effects//9.wav"]

winsound.PlaySound(choice(effect_list), winsound.SND_FILENAME)
