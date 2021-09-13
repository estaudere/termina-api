# Welcome to Termina.

This is the backend for CAI @ Termina, an AI that analyzes your recent Spotify history to judge your character in a cyberpunk world. Go 
[here](https://cai.edwinrheindt.repl.co/) to find out if you're a hacker, medic, gearhead, or any of a dozen characters.

This project won Most Creative Hack at Uncommon Hacks in April 2021. [Here's](https://devpost.com/software/cai-an-artificial-intelligence) our Devpost
submission. I worked entirely on the backend of this project — including the Random Forest model that assigns the character and the K-means Classifier 
model that digested a dataset of almost 500k songs to divide them into 12 archetypes. I also turned these models into an API (using Python's Flask library)
to be called from the React frontend.
