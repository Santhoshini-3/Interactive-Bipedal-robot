###Voice controlled robot with voice assistant
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
from datetime import date
from gtts import gTTS
from io import BytesIO
from pygame import mixer
import sys
import pigpio
import time

# Initialize pygame mixer
mixer.init()

# Configure Generative AI
genai.configure(api_key="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")
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat()

# Initialize pigpio
pwm = pigpio.pi()
#define servo pin numbers
trunk = 17  # Replace with your first GPIO pin number
right_hip = 27  # Replace with your second GPIO pin number
left_hip = 22  # Replace with your third GPIO pin number
right_ankle = 23  # Replace with your fourth GPIO pin number
left_ankle = 24
right_hand = 5
left_hand = 6
head = 25# GPIO pin for the servo

# Initialize speech recognition and text-to-speech engine
listener = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty('voice', voices[1].id)


# Set mode and frequency for all servos
for pin in [trunk, right_hip, left_hip, right_ankle, left_ankle, right_hand, left_hand, head]:
    pwm.set_mode(pin, pigpio.OUTPUT)
    pwm.set_PWM_frequency(pin, 50)

# Convert angle (0-180) to pulse width in microseconds (500 to 2500 us)
def set_angle(servo_pin, angle):
    """Set the angle of the servo motor."""
    pulse_width = 500 + (angle / 180.0) * 2000
    pwm.set_servo_pulsewidth(servo_pin, pulse_width)

def speak_text(text):
    """Convert text to speech and play it."""
    mp3file = BytesIO()
    tts = gTTS(text, lang="en", tld='us')
    tts.write_to_fp(mp3file)
    mp3file.seek(0)

    try:
        mixer.music.load(mp3file, "mp3")
        mixer.music.play()

        while mixer.music.get_busy():
            pass
    except KeyboardInterrupt:
        mixer.music.stop()
        mp3file.close()

    mp3file.close()

def user_commands():
    """Capture and recognize voice commands."""
    try:
        with sr.Microphone() as source:
            print("Start Speaking!!")
            listener.adjust_for_ambient_noise(source, duration=0.5)
            voice = listener.listen(source, timeout=20, phrase_time_limit=30)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'bujji' in command:
                command = command.replace('bujji', '').strip()
                print(command)
                return command
    except sr.UnknownValueError:
        speak_text("Sorry, I did not understand that.")
    except sr.RequestError:
        speak_text("Sorry, my speech service is down.")
    return ""
##Move forward
def move_forward():
    while(True):
        print("Rotating servo 1 to 135 degrees...")
        set_angle(left_ankle, 135)
        time.sleep(2)
                        
        print("Rotating servo 2 to 120 degrees...")
        set_angle(trunk, 120)
        time.sleep(2)
                        
        print("Rotating servo 3 to 70 degrees...")
        set_angle(left_hip, 70)
        time.sleep(2)
                        
        print("Rotating servo 4 to 70 degrees...")
        set_angle(right_hip, 70)
        time.sleep(2)
                        
        print("Rotating servo 5 to 90 degrees...")
        set_angle(left_ankle, 90)
        time.sleep(2)
                        
        print("Rotating servo 3 to 90 degrees...")
        set_angle(left_hip, 90)
        time.sleep(2)
                        
        print("Rotating servo 4 to 45 degrees...")
        set_angle(right_ankle, 45)
        time.sleep(2)
                      
        print("Rotating servo 1 to 120 degrees...")
        set_angle(trunk, 120)
        time.sleep(2)
                       
        print("Rotating servo 2 to 110 degrees...")
        set_angle(right_hip, 110)
        time.sleep(2)
                        
        print("Rotating servo 3 to 110 degrees...")
        set_angle(left_hip, 110)
        time.sleep(2)
                        
        print("Rotating servo 1 to 90 degrees...")
        set_angle(trunk, 90)
        time.sleep(2)
# Rest position all 90                          
def stop_moving():
    for pin in [trunk, right_hip, left_hip, right_ankle, left_ankle, right_hand, left_hand, head]:
        set_angle(pin, 90)
        time.sleep(2)
# moving head
def turn_head():
    set_angle(head, 0)
    time.sleep(2)
    set_angle(head, 180)
    time.sleep(2)
# moving right hand
def shake_hand():
    set_angle(right_hand, 120)
    time.sleep(2)
    set_angle(right_hand, 600)
    time.sleep(2)   
#hi movement
def wave():
    set_angle(right_hand, 180)
    time.sleep(2)
    set_angle(right_hand, 90)
    time.sleep(2)
def run_bujji():
    """Main function to run the voice assistant."""
    while True:
        command = user_commands()
        if command:
            if 'play' in command:
                song = command.replace('play', '').strip()
                speak_text(f'Playing {song}')
                pywhatkit.playonyt(song)
            elif 'time' in command:
                current_time = datetime.datetime.now().strftime('%I:%M %p')
                speak_text(f'The current time is {current_time}')
            elif 'say hi' in command:
                wave()
                speak_text("Hello, How can I help you?")
            elif 'tell me about yourself' in command:
                speak_text("I am Buujii, an interactive bipedal robot. I have 4 giga bytes of RAM and 16 giga bytes of storage capacity. I use raspberry PI-4 model B as my processor and 8 three point three volts servo motors for locomotion. I use 5 volts 2 amps power supply. I rely google's generative A I model gemini for communicatin.")
            elif 'move forward' in command:
                move_forward()
            elif 'stop moving' in command:
                stop_moving()
            elif 'turn your head' in command:
                turn_head()
            elif 'shake your hands' in command:
                shake_hand()
            elif 'turn off' in command:
                speak_text("Stopping the assistant.")
                for pin in [trunk, right_hip, left_hip, right_ankle, left_ankle]:
                    pwm.set_servo_pulsewidth(pin, 0)
                pwm.stop()
                sys.exit()
            else:
                response = chat.send_message(command, stream=True,
                                             generation_config=genai.types.GenerationConfig(
                                                 max_output_tokens=168))
                for chunk in response:
                    print(chunk.text, end='')
                    speak_text(chunk.text.replace("*", ""))
                print('\n')
        time.sleep(1)

run_bujji()
