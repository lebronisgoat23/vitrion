import mediapipe as mp
print(f"MediaPipe path: {mp.__path__}")
try:
    print(f"Solutions: {mp.solutions}")
except AttributeError:
    print("mp.solutions missing")
    print(f"Dir mp: {dir(mp)}")
