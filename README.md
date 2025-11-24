# X-Reply Automation - Alpha

This project automates the process of replying to posts on **X (formerly Twitter)**, helping content creators save time and streamline their engagement workflow. Once set up, the automation will scan your feed (or any section you manually navigate to) and automatically generate replies to visible posts.

<br>

# <u>Pre-requisite</u>

You must open your browser in **debug mode** and manually log into your X account.  
After logging in, navigate to the section where you want the script to reply (e.g., **Home**, **Following**, or any list/feed).  
Once you are on the correct screen, run the script — it will detect posts, reply to each one, and scroll automatically.

<br>

# <u>Important Note</u>

The script <b>cannot</b> navigate to your X account or sections by itself.  
You must:

<b>• Log in</b>  
<b>• Navigate to the correct page</b>  

After that, the script will take over and handle:

<b>• Capturing posts</b>  
<b>• Generating replies</b>  
<b>• Sending replies</b>  
<b>• Scrolling to the next post automatically</b>

You can configure your LLM provider using an `.env` file.

<br>

# <u>Sample .env File</u>

<code>LLM_URL= 
MODEL_NAME=
LLM_KEY=
HOST_ADDRESS=</code>


<br>

# <u>How to Use</u>

1. Start your browser in debug mode.  
   Example for Microsoft Edge on Windows:  
   <code>start msedge.exe --remote-debugging-port=9222 --user-data-dir="C:\edge-debug"</code>  
   (You may use any browser and any port.)

2. Log into your X account.

3. Navigate to the page where the script must interact with posts (e.g., your **feed** or **following** page).

4. Run the script. It supports two modes:  
   - <b>Press F9</b> → Replies to only the currently visible post  
   - <b>Press F10</b> → Automatically replies to every post on your feed

5. The script will begin replying and scrolling.

6. To stop the script, simply close the terminal or press <code>Ctrl + C</code> in VS Code.

<br>

# <u>To-Do</u>

1. Add randomized time intervals between replies to avoid detection as automation by X.  
2. Perform deeper testing across different feed types and browsers.


<br><br>

# <u>Final Notes</u>

This tool is designed to assist content creators while keeping user control at the core.  
Always test responsibly, and ensure you comply with X’s automation rules.

<h4>Remeber, this is a work in progress project.</h4>