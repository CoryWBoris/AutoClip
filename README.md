# AutoClip

![Stability Badge](https://img.shields.io/badge/-stable-blue)  
By: Cory Boris  
© 2024 MIT License
A Control Surface for Automatically Changing Clips' Names Based on the Name of their Parent Track In Ableton Live 11+ WITHOUT PLUGINS ;)

\*\*for Mac or Windows\*\*

### 5 Steps to setup. -note-, this assumes you are using the default user library folder. If you have moved this folder externally or otherwise, make a Remote Scripts folder inside of whatever user library folder you have pointed Ableton to, and start from step 2:
1. Mac users:  
   Go to `/Users/your_username/Music/Ableton/User Library`  
   Windows users:  
   Go to `\Users\your_username\Documents\Ableton\User Library`
2. Create a folder 'Remote Scripts' if it's not already created.
3. Create a folder titled 'AutoClip' inside the 'Remote Scripts' folder.
4. Download **both** .py files, "AutoClip.py" and "\_\_init\_\_.py", and place them in the 'Remote Scripts/AutoClip' folder.
5. Restart or open Ableton Live
6. In Ableton, select 'AutoClip' in the "Link|Tempo|Midi" tab, and make sure the input and output are set to 'None'.

**Note**: You can add the 2 mentioned files from here to their respective folders as shown by my tutorial while Ableton is open or quit, but if Ableton is open, then you *will* have to restart Ableton for the selected control surface to go into effect. The reason being is that Ableton compiles python and loads python code into memory when Ableton starts, but not after it loads up. This means for you using the software that in order to update this script if and when it is updated, then you will have to restart Ableton to use the updated software.

## Instructions for use:
In Arrangement View: Rename a Midi or Audio Track and then the names of every clip are **magically** changed to the name of their individual tracks + the number the clip is in order from left to right. Order is always maintained.  
In Session View: Rename a Midi or Audio Track and then the clips you drag to these tracks or the clips already existing will be renamed the name of the track + the number of the clip from top to bottom.  
The number in a renamed clip's name in Session view is not based on the next adjacent clip but rather the next adjacent clip slot whether or not there is a clip. I thought this made more sense for session view.  
Anytime you drop a clip in a track, it will automatically be renamed to match the above rules.  
Lastly, when this control surface is enabled, you won't be able to name clips manually, as their names will always be reset whenever you drag a single clip.

## Open Issues:
None so far, but please let me know if there are any by all means!

## Future Updates:
I was thinking it would be cool to use the name of the track to determine if clips will be renamed or not based on a code word.  
For now, every clip is named at once when loading the control surface, I can understand if this is too 'all or nothing' for your personal tastes, but I figured you always have the option to just not use the control surface.  

## Other Programs:
<a href="https://coryboris.gumroad.com/l/TrueAutoColor">TrueAutoColor</a>  
A custom color layout maker for Ableton Live 11+ for changing track and clip colors based on name

### Coffees Welcome!
- Paypal: tromboris@gmail.com
- Venmo: @Cory-Boris
- Ethereum Address: `0x3f6af994201c17eF1E86ff057AB2a2F6CB0D1f6a`

Thank you! 🔥🥰✌🏻🙏🏻

