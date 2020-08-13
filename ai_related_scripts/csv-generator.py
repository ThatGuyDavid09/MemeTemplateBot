# This creates a csv file assigning each file name to a label
import csv
import os

from os import listdir

master_classes = {
    "0" : "2 buttons to press",
    "1" : "2 calm guys",
    "2" : "2 girls 1 guy",
    "3" : "2 girls yelling at cat",
    "4" : "2 ppl kissing guy in background",
    "5" : "2 strong guys shaking hands",
    "6" : "3 doggos",
    "7" : "3 guys we were bad but now we are good",
    "8" : "3 take it or leave it",
    "9" : "What is this place turtle",
    "10" : "ability to speak no smart",
    "11" : "aging cap",
    "12" : "ah shit here we go again",
    "13" : "ah yes the negotiator",
    "14" : "always has been",
    "15" : "am i a joke to you",
    "16" : "amateurs",
    "17" : "angry guy standing up",
    "18" : "anime girl tposing over someone",
    "19" : "apes together strong",
    "20" : "are we blind deploy the",
    "21" : "are you winning son",
    "22" : "bear looking away",
    "23" : "big doge little doge",
    "24" : "bird spongebob",
    "25" : "bitch how dare you still live",
    "26" : "bonjour",
    "27" : "brain no sleep",
    "28" : "buenos dias fuckboy",
    "29" : "bunch of ppl shaking hands one purple guy",
    "30" : "car turning abruptly",
    "31" : "change my mind guy",
    "32" : "coincidence i think not",
    "33" : "confused but hes got the spirit",
    "34" : "confused screaming",
    "35" : "cool bug facts",
    "36" : "cool future",
    "37" : "coralines dad sad at computer",
    "38" : "could you not be BLANK for 5 minutes",
    "39" : "da fuck they doin over der",
    "40" : "dad and kid in car",
    "41" : "difference between this picture and this picture same picture",
    "42" : "disappointment is immeasurable day is ruined",
    "43" : "dj khaled suffering from success",
    "44" : "do it again",
    "45" : "dog suffocating owner",
    "46" : "dumbest man you are clearly dumber",
    "47" : "ew i stepped in shit",
    "48" : "excuse me what the fuck",
    "49" : "feelings of power bar graph",
    "50" : "finally worthy opponent battle will be legendary",
    "51" : "fine ill do it myself",
    "52" : "first time",
    "53" : "fun fact squidward",
    "54" : "girl and guy in bed",
    "55" : "good question",
    "56" : "grim reaper its time to go",
    "57" : "gun gru",
    "58" : "guy disappearing",
    "59" : "guy pointing at tv",
    "60" : "guy saluting and crying",
    "61" : "guy schooches away on prison bench",
    "62" : "guy smiling and tapping head",
    "63" : "he is the messiah",
    "64" : "hes about to do something stupid",
    "65" : "holy music stops",
    "66" : "i can milk you",
    "67" : "i don't need sleep i need answers",
    "68" : "i fear no man but that thing scares me",
    "69" : "i know him hes me",
    "70" : "i see no god up here other than me",
    "71" : "i see this as an absolute win",
    "72" : "i won at what cost",
    "73" : "if those kids could read",
    "74" : "im going to do a pro gamer move",
    "75" : "increasingly clowny man",
    "76" : "invest",
    "77" : "its all coming together",
    "78" : "its free real estate",
    "79" : "keanu busts down door guy scared",
    "80" : "kid holding fire",
    "81" : "let me in",
    "82" : "lisa presetning somehting",
    "83" : "looks like its off to the rice fields jimbo",
    "84" : "mexican guy laughing (ONLY SAYING MEXICAN FOR CLASSIFICATION PURPOSES)",
    "85" : "modern problems modern solutions",
    "86" : "news person one microphone many microphones",
    "87" : "no haha go brr",
    "88" : "no no hes got a point",
    "89" : "normal coffin fancy coffin",
    "90" : "now all of china knows you are here",
    "91" : "now this is an avengers level threat",
    "92" : "obama giving himself a medal",
    "93" : "oh no anyway",
    "94" : "outstanding move",
    "95" : "panik kalm panik",
    "96" : "panzer of the lake",
    "97" : "patrick this makes sense right",
    "98" : "perfection",
    "99" : "pew die pie and that's a fact",
    "100" : "return of the king",
    "101" : "rice field",
    "102" : "rick peeling back wall",
    "103" : "sad drake happy drake",
    "104" : "satan huge fan",
    "105" : "say the line bart",
    "106" : "shit [CENSORED] that's all you had to say",
    "107" : "so that was a fucking lie",
    "108" : "spider man presenting something",
    "109" : "spider man they love me",
    "110" : "task failed successfully",
    "111" : "the floor is made out of floor",
    "112" : "there is another",
    "113" : "this is beyond science",
    "114" : "thisll cost us 51 years",
    "115" : "visible confusion",
    "116" : "whomst has awakened the ancient one",
    "117" : "you shouldn't be here neither should you"
}

# CSV file format:
# Column labels: file_id, class_name, [class names, 0 for all its not]

# Since the auto generated dictionary is backwards, I have to do this
val_list = list(master_classes.values())

for i in ["Sorted memes"]:
    # I reuse this code a lot
    directory = r"C:\Users\vadim\Videos\Meme stuff\Meme dataset\Sets\{}".format(i)
    folder_paths = [os.path.join(directory, o) for o in os.listdir(directory) if os.path.isdir(os.path.join(directory,o))]
    folders = []
    print(folders)
    for folder_path in folder_paths:
        folder_split = folder_path.split("\\")
        if "Do not use" not in folder_split[-1]:
            folders.append(folder_split[-1])

    # Write the csv file
    with open('{}.csv'.format(i), 'w', newline='') as file:

        print("File opened")
        writer = csv.writer(file)

        headers = ["file_name", "classes"]

        writer.writerow(headers)
        print("First row written")

        for folder in folders:
            search_directory = directory + r"\{dir}".format(dir=folder)
            print("searching " + search_directory)

            for file in listdir(search_directory):
                row = [file]
                row.append(folder)
                # writer.writerow([file[:-4], val_list.index(folder)])
                writer.writerow(row)
                print("Wrote file " + file + " in " + i + ".csv")
