#   -- ASSESSMENT 01 - SPELLCHECKER --
#
# Given that we are only allowed one file, I used several classes in the same file. The Main() class
# exists purely for visual consistency.
# Exiting incorrectly will permanently colour the terminal (until you restart the app and close correctly or restart the
# terminal). This is because I don't turn back the colour after each transformation and it should normally not be possible.
# Correcting this would make strings even less readable than they are right now.


import time
import os
import subprocess
import platform
import copy
from shutil import copyfile
from difflib import SequenceMatcher
from datetime import datetime
import math
import io
import sys


alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
statistics = {
    "totalWords": 0,
    "correctWords": 0,    # no. words spelt correctly
    "incorrectWords": 0,  # no. words spelt incorrectly
    "incorrectWordsList": list(),
    "newWords": 0,        # no. words added to dictionary
    "newWordsList": list(),
    "correctedWords": 0,  # no. word suggestions accepted by the user
    "correctedWordsList": list(),
    "timeAndDate": datetime.now(),
    "timeElapsed": 0,     # time taken spellchecking (excluding user inputs)
    "totalTime": 0        # total execution time for spellchecking
    # this is also not the "total" runtime but since multiple texts can be checked it cannot be the total runtime
}


# this class contains the main functions used in the program and the file-parsing functions
class Main():
    # highest level
    def Main():
        if not Main.DisableBuffer():
            return

        if Main.FileExists("EnglishWords.txt"):
            Main.OrderDictionary()
        else:
            print(f"{colours.LightRed}\nFor this program to work, \"EnglishWords.txt\" must be present in the same folder as the .py file and " +
                  f"contain the dictionary. Additionally, the current working directory must be the directory containing these files." +
                  f"{colours.Default}")
            return

        Main.ClearScreen()
        print(f"{colours.Cyan}Hello!", end=" ")

        repeat = 1
        while repeat:
            error = Main.RunApp()
            if error == -1:
                # this option was added after the PDF rework and I didn't want
                # to redo a lot of stuff just to make it neater
                print(f"{colours.LightGreen}Goodbye!{colours.Default}")
                return
            repeat = Main.GoAgain()
            Main.ClearScreen()

    # body of the app
    def RunApp():
        Main.ResetStatistics()

        print(f"{colours.Cyan}What kind of input would you like to use?\n" +
              f"{colours.Blue}   1. Text input\n" +
              "   2. File input\n" +
              "   0. Quit")
        choice = input(f"{colours.Green}> ")
        while choice == "" or choice[0] not in "tT1fF2qQ0":
            choice = input(
                f"{colours.LightRed}Please input \"text\"/1, \"file\"/2 or \"quit\"/0:\n{colours.Green}> ")
        if choice[0] in "qQ0":
            return -1
        if choice[0] in "tT1":
            print(f"{colours.Cyan}Write text below (press enter to submit):")
            text = input(f"{colours.Green}> ")
            while text == "":
                text = input(
                    f"{colours.LightRed}You need to input some text:\n{colours.Green}> ")
        else:
            print(f"{colours.Cyan}Please enter the path of the file: ")
            path = input(f"{colours.Green}> ")
            while Main.ImportFromFile(path) == -1:
                path = input(f"{colours.LightRed}Could not find a file at the specified path. " +
                             f"Please try again.\n{colours.Green}> ")
            text = Main.ImportFromFile(path)

        # 'interrupts' are time waiting for the user to respond and are deducted from the checking time
        # I also strip the time.sleep() because I need to feel good about my runtimes
        interrupts = list()
        timeStart = time.time()

        text = sc.ProcessText(text, interrupts)
        text = text[:-1]  # has an unnecessary space at the end
        time.sleep(0.5)

        Main.CompileStatistics(timeStart, time.time(), interrupts)
        Main.PresentStatistics()
        time.sleep(0.5)

        saveFilePath = Main.SaveFilePrompt()
        if saveFilePath != -1:
            Main.SaveFile(saveFilePath, text)
            time.sleep(0.5)

        return 1

    # asks if user wants to check more text
    # this is a bit redundant given that the initial menu has the option to quit, but it is explicitly asked for in the pdf
    def GoAgain():
        print(f"{colours.LightMagenta}\nThank you for using this tool. " +
              "Would you like to check more text?")
        answer = input(f"{colours.Green}> ")
        while answer == "" or answer[0] not in ["y", "Y", "n", "N"]:
            answer = input(
                f"{colours.LightRed}I didn't get that. Yes or No?\n{colours.Green}> ")
        # resets the console colours
        print(f"{colours.Default}", end="")

        if answer[0] in ("y", "Y"):
            return True
        return False

    # orders EnglishWords.txt alphabetically
    def OrderDictionary():
        # several thousand words e.g. barnaise are not ordered in the original file
        # sorry for modifying it independent from the input, but an ordered file is
        # browsed much faster
        print(f"{colours.Green}File found!\nLoading...")
        copyfile("EnglishWords.txt", "EnglishWords_temp.txt")
        with open("EnglishWords_temp.txt") as temp:
            with open("EnglishWords.txt", "w") as file:
                for line in sorted(temp):
                    file.write(line)
        os.remove("EnglishWords_temp.txt")

    # sets all statistics to 0 for subsequent checks
    def ResetStatistics():
        statistics["totalWords"] = 0
        statistics["correctWords"] = 0
        statistics["incorrectWords"] = 0
        statistics["newWords"] = 0
        statistics["correctedWords"] = 0
        statistics["timeAndDate"] = datetime.now()
        statistics["timeElapsed"] = 0
        statistics["totalTime"] = 0
        statistics["correctedWordsList"] = list()
        statistics["newWordsList"] = list()

    # some statistics are too complex to be computed while checking and maintain code readability
    def CompileStatistics(timeStart, timeEnd, interrupts):
        statistics["timeElapsed"] = timeEnd - timeStart
        for [x, y] in interrupts:
            statistics["timeElapsed"] -= y - x
        statistics["timeElapsed"] = math.floor(
            statistics["timeElapsed"] * 100) / 100

        statistics["totalTime"] = timeEnd - timeStart
        statistics["totalTime"] = math.floor(
            statistics["totalTime"] * 100) / 100

        months = ["", "Jan", "Feb", "Mar", "Apr", "May",
                  "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        month = months[int(statistics["timeAndDate"].strftime("%m"))]
        dateString = statistics["timeAndDate"].strftime(
            "%d ") + month + statistics["timeAndDate"].strftime(" %Y, %H:%M")
        statistics["timeAndDate"] = dateString

    # outputs the statistics after checking
    def PresentStatistics():
        print(
            f"{colours.Cyan}\n\nI have finished checking the text! Here are some fun facts about this:\n" +
            f"{colours.Blue}Total number of words: {statistics['totalWords']}\n" +
            f"Correctly spelt words: {statistics['correctWords']}\n" +
            f"Incorrectly spelt words: {statistics['incorrectWords']} {statistics['incorrectWordsList']}\n" +
            f"Words I learned from you: {statistics['newWords']} {statistics['newWordsList']}\n" +
            f"Words I helped you correct: {statistics['correctedWords']} {statistics['correctedWordsList']}\n" +
            f"Time it took me to check the text: {statistics['timeElapsed']} s\n" +
            f"Total time elapsed: {statistics['totalTime']} s\n"
        )

    # checks if a certain file exists
    def FileExists(path):
        return os.path.isfile(path)

    # this may be the single most elaborately useless function
    # asks the user if/how they want to save a file
    def SaveFilePrompt():
        print(f"{colours.Cyan}Do you want to save the processed file?")
        answer = input(f"{colours.Green}> ")
        while answer == "" or answer[0] not in "yYnN10":
            answer = input(
                f"{colours.LightRed}I didn't get that. Yes or No?\n{colours.Green}> ")
        if answer[0] in "nN0":
            return - 1

        path = input(
            f"{colours.Cyan}Please enter the name of the file:\n{colours.Green}> ")
        while path == "":
            path = input(
                f"{colours.LightRed}This is not a valid name. Please enter the name of the file:\n{colours.Green}> ")

        while Main.FileExists(path + ".txt"):
            print(
                f"{colours.LightRed}This file already exists and will be overwritten. Proceed? ")
            areYouSure = input(f"{colours.Green}> ")
            while areYouSure == "" or areYouSure[0] not in "yYnN01":
                areYouSure = input(
                    f"{colours.LightRed}I didn't get that. Yes or No?\n{colours.Green}> ")

            if areYouSure[0] in "nN0":
                path = input(
                    f"{colours.Cyan}Please enter a new name for the file:\n> ")
                while path == "":
                    path = input(
                        f"{colours.LightRed}This is not a valid name. Please enter the name of the file:\n{colours.Green}> ")
            else:
                break

        return path + ".txt"

    # saves the file with statistics on top and text below
    def SaveFile(path, text):
        with open(path, "w") as file:
            file.write(
                # this part is intentionally longer so it looks more like a header
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n" +
                "-------------------- STATISTICS ---------------------\n" +
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n" +
                f"This text was checked on: {statistics['timeAndDate']}\n" +
                f"Total number of words: {statistics['totalWords']}\n" +
                f"Correctly spelt words: {statistics['correctWords']}\n" +
                f"Incorrectly spelt words: {statistics['incorrectWords']} {statistics['incorrectWordsList']}\n" +
                f"Words I learned from you: {statistics['newWords']} {statistics['newWordsList']}\n" +
                f"Words I helped you correct: {statistics['correctedWords']} {statistics['correctedWordsList']}\n" +
                f"Time it took me to check the text: {statistics['timeElapsed']} s\n" +
                f"Total time elapsed: {statistics['totalTime']} s\n\n" +
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n" +
                "----------------- CORRECTED TEXT ------------------\n" +
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n" +
                f"\"{text}\"\n\n" +
                "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
            )
        print(f"{colours.LightGreen}File saved!")

    # Could make use of IsFile() but I want it to return the text to be consistend with the text input
    def ImportFromFile(path):
        try:
            file = open(path, "r")
            text = file.read()
        except IOError:
            return -1
        return text

    # Essentially scrolls down right below already existing text in the terminal
    # source: https://stackoverflow.com/questions/2084508/clear-terminal-in-python/18128909#18128909
    def ClearScreen():
        if platform.system() == "Windows":
            subprocess.Popen("cls", shell=True).communicate()
        else:  # Linux and Mac
            print("\033c", end="")

    # Disables the Python Output Buffer to enable a nice flow of outputs
    # source: https://blog.finxter.com/what-is-python-output-buffering-and-how-to-disable-it/#M
    #         ethod_4_Wrapping_sys_stdout_Using_TextIOWrapper_And_Setting_Buffered_Size_=_0
    def DisableBuffer():
        try:
            sys.stdout = io.TextIOWrapper(
                open(sys.stdout.fileno(), 'wb', 0), write_through=True)
            return True
        except TypeError:
            print(f"{colours.LightRed}This cannot work on Python 2{colours.Default}")
            return False


# I decided not to use unicode art/bordered menus because who knows what kind of resolution the
# tester's window has. I opted for this model because it's clean and friendly.
# source: https://godoc.org/github.com/whitedevops/colors
class colours:
    Default = "\033[39m"
    Green = "\033[32m"
    Blue = "\033[34m"
    Cyan = "\033[36m"
    LightRed = "\033[91m"
    LightGreen = "\033[92m"
    LightMagenta = "\033[95m"
    DarkGray = "\033[90m"


# this class contains word-processing functions
class sc:
    # main processing function
    # I don't think that passing 'interrupts' around is the best way to do it, but it's probably worse to declare it global
    def ProcessText(text, interrupts):
        words = text.split()
        newText = ""
        for word in words:
            trimmedWord = ""
            for char in word:
                if char in alphabet:
                    trimmedWord += char
            trimmedWord = trimmedWord.lower()
            if trimmedWord:
                statistics["totalWords"] += 1
                if sc.InDictionary(trimmedWord):
                    statistics["correctWords"] += 1
                    time.sleep(0.1)
                    interrupts.append([0, 0.1])
                    # printing char by char looks more natural
                    print(f"{colours.DarkGray}", end="")
                    for char in trimmedWord:
                        print(char, end="")
                        time.sleep(0.02)
                        interrupts.append([0, 0.02])
                    print(" ", end="")
                    newText += trimmedWord + " "
                else:
                    # highlights the wrong word
                    print(f"{colours.LightRed}", end="")
                    for char in trimmedWord:
                        print(char, end="")
                        time.sleep(0.01)
                        interrupts.append([0, 0.01])
                    print(" ", end="")

                    trimmedWord = sc.CorrectWord(trimmedWord, interrupts)
                    time.sleep(0.1)
                    interrupts.append([0, 0.1])

                    # reprints the whole text for readability
                    # in this case printing char by char would be awful
                    newText += trimmedWord + " "
                    print(f"{colours.DarkGray}" + newText, end="")
                    time.sleep(0.1)
                    interrupts.append([0, 0.1])
        return newText

    # checks if a certain word is found in the dictionary
    def InDictionary(word):
        with open("EnglishWords.txt") as file:
            newWord = file.readline().strip()
            while newWord:
                if word.lower() == newWord:
                    return True
                if (word < newWord):
                    # no point in searching past where the dictionary entry should already be
                    return False
                newWord = file.readline().strip()
        return False

    # makes a choice based on user input as to what to do with a wrong word
    def CorrectWord(word, interrupts):
        print(
            f"{colours.Cyan}\nI have encountered a word I don't recognise(\"%s\"). What should I do with it?" % word)
        print(
            f"{colours.Blue}   1. Ignore\n" +
            "   2. Flag but keep as is\n" +
            "   3. Add to dictionary\n" +
            "   4. Suggest a new word"
        )
        interrupt = time.time()
        choice = input(f"{colours.Green}> ")
        while len(choice) == 0 or choice[0] not in "1234IFASifas":
            choice = input(
                f"{colours.LightRed}Please input a number from 1 to 4:\n{colours.Green}> ")
        interrupts.append([interrupt, time.time()])

        if choice[0] in "1iI":
            # ignore word
            statistics["incorrectWords"] += 1
            statistics["incorrectWordsList"].append(word)
        elif choice[0] in "2fF":
            # flag as incorrect
            statistics["incorrectWords"] += 1
            statistics["incorrectWordsList"].append(word)
            word = "?" + word + "?"
        elif choice[0] in "3aA":
            # add to dictionary
            # creates a temporary duplicate of the dictionary to iterate through
            # and writes the new word in its normal place in a dictionary
            copyfile("EnglishWords.txt", "EnglishWords_temp.txt")
            with open("EnglishWords_temp.txt") as temp:
                with open("EnglishWords.txt", "w") as file:
                    newWord = temp.readline().strip()
                    while newWord < word:
                        file.write(newWord + "\n")
                        newWord = temp.readline().strip()
                    file.write(word.lower())
                    while newWord:
                        file.write("\n" + newWord)
                        newWord = temp.readline().strip()
            os.remove("EnglishWords_temp.txt")
            statistics["correctWords"] += 1
            statistics["newWords"] += 1
            statistics["newWordsList"].append(word)
            print(f"{colours.LightGreen}Added word to dictionary!")
        else:
            # search for a similar word
            newWord = sc.SuggestWord(word)
            print(
                f"{colours.Cyan}I think the word \"{word}\" is similar to \"{newWord}\". Would you like to change it? ")
            interrupt = time.time()
            areYouSure = input(f"{colours.Green}> ")
            while len(areYouSure) == 0 or areYouSure[0] not in "yYnN":
                areYouSure = input(
                    f"{colours.LightRed}I didn't quite get that. Yes or No?\n{colours.Green}> ")
            interrupts.append([interrupt, time.time()])

            if areYouSure[0] in "yY":
                # replaces the word
                statistics["correctWords"] += 1
                statistics["correctedWords"] += 1
                statistics["correctedWordsList"].append(word)
                word = newWord
            else:
                # marks it as wrong
                # this is not very clear in the pdf but Gareth told me to still use ?word?
                statistics["incorrectWords"] += 1
                statistics["incorrectWordsList"].append(word)
                word = "?" + word + "?"
        return word

    # compares word to all words in the dictionary
    # I found the Jaro distance to be faster than the recommended one (and fun to implement) while suggesting the same words
    def SuggestWord(word):
        minDistance = len(word)
        minDistanceWord = word
        with open("EnglishWords.txt", "r") as file:
            newWord = file.readline().strip()
            while newWord:
                distance = StringMatchers.Jaro(word, newWord)
                if minDistance >= distance:
                    if minDistance > distance or (len(word) - len(minDistanceWord) > len(word) - len(newWord)):
                        # with the second condition I try to give priority to words of similar length, assuming the most common error
                        # is mistyping a character. Could use the original word before stripping non-letters but the minor improvement
                        # doesn't warrant keeping the original input and passing a second argument
                        minDistance = distance
                        minDistanceWord = newWord
                newWord = file.readline().strip()
        return minDistanceWord


# I have tried a few methods because I wanted a nice flow of outputs. I aimed to get less than 1s per test.
# Unfortunately, I did not succeed, but I think it's nice to have the algorithms neatly presented anyway. Despite
# the speed I found for some of them, I did not include unreliable algorithms (e.g. the Bag algorithm) and to my
# understanding they are intended for preliminary removal of elements from a list of potential corrections, rather
# than for actually suggesting a word.
#  The time I assigned to each algorithm is the time needed to compare "zymurgyzzz" to the whole dictionary. This
# is a rough average, and testing may yield high variance in time between tests (in fact I haven't been able to
# replicate these results, all of them seem faster now)
# Everything runs much smoother on the host than on the VM, but you already know that ):
# I probably wasted way too much time on this
class StringMatchers:
    # an implementation of the Damerau-Levenshtein distance using the Wagner-Fischer algorithm
    # 5.1s
    def Damerau_Levenshtein(s1, s2):
        s1 = " " + s1
        s2 = " " + s2
        l1 = len(s1)
        l2 = len(s2)
        d = [[0 for i in range(l2)] for j in range(l1)]

        for i in range(l1):
            d[i][0] = i
        for j in range(l2):
            d[0][j] = j
        for i in range(1, l1):
            for j in range(1, l2):
                if s1[i] == s2[j]:
                    cost = 0
                else:
                    cost = 1
                d[i][j] = min(
                    d[i - 1][j] + 1,
                    d[i][j - 1] + 1,
                    d[i - 1][j - 1] + cost,
                )
                if i > 1 and j > 1 and s1[i] == s2[j - 1] and s1[i - 1] == s2[j]:
                    d[i][j] = min(
                        d[i][j],
                        d[i - 2][j - 2] + 1
                    )
        if d[l1 - 1][l2 - 1]:
            return 1.0 / d[l1 - 1][l2 - 1]
        return 0

    # the standard suggested algorithm for this problem
    # 1.4s
    def SequenceMatcherImport(s1, s2):
        return 1 - SequenceMatcher(None, s1, s2).ratio()

    # uses the Jaro distance
    # I did not use Jaro-Winkler because prefixes are not useful for this problem
    # Actually returns 1 - jaro because I want it to be in line with the others
    # 1.1s - I chose this for suggestions
    def Jaro(s1, s2):
        l1 = len(s1)
        l2 = len(s2)

        if l1 == 0 and l2 == 0:
            return 0
        if s1 == s2:
            return 0

        md = math.floor((max(l1, l2) / 2)) - 1
        m1 = [False] * l1
        m2 = [False] * l2
        m = 0
        t = 0

        for i in range(l1):
            xi = max(0, i - md)
            xf = min(l2, i + md + 1)

            for j in range(xi, xf):
                if m2[j]:
                    continue
                if s1[i] != s2[j]:
                    continue
                m1[i] = True
                m2[j] = True
                m += 1
                break

        if m == 0:
            return 1

        k = 0
        for i in range(l1):
            if not m1[i]:
                continue
            while not m2[k]:
                k += 1
            if s1[i] != s2[k]:
                t += 1
            k += 1

        distance = ((m / l1) + (m / l2) + (m - t / 2) / m) / 3
        return 1 - distance


# start running
Main.Main()
