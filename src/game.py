import random
from .voicespeak import speak, sync_speak
import os
import cn2an

tmp_dir = os.path.join(os.getcwd().split("slimePet")[0], "slimePet", "tmp", "tmp.txt")
def guess_game(people="rencai"):
    difficulties = [100, 1000, 10000]
    diffculty = random.choice(difficulties)
    number = random.randint(1, diffculty)
    lower_bound = 1
    upper_bound = diffculty
    attempts = [6, 10, 20][difficulties.index(diffculty)]
    guess = None
    word = "我已经选择了一个{}到{}之间的数字。你有{}次机会来猜测它。"
    with open(tmp_dir, "r") as f:
        old_content = f.read()
    with open(tmp_dir, "w") as f:
        f.write("")
    prev_content = ""
    sync_speak(word.format(lower_bound, upper_bound, attempts), people)
    while attempts > 0:
        with open(tmp_dir, "r") as f:
            content = f.read()
        if content != prev_content:
            prev_content = content
            try:
                guess = int(content)
            except:
                try:
                    guess = cn2an.cn2an(content, "smart")
                except: 
                    print("识别有误，请重新输入")
                    continue
        if guess == None:
            continue
        if guess <= lower_bound or guess >= upper_bound:
            sync_speak("请在{}到{}之间猜测".format(lower_bound, upper_bound), people)
            guess = None
            continue
        if guess == number:
            sync_speak("恭喜你，猜对了！大吉大利，今晚吃鸡！", people)
            with open(tmp_dir, "w") as f:
                f.write(old_content)
            return
        elif guess < number:
            lower_bound = guess
        else:
            upper_bound = guess
        attempts -= 1
        if attempts == 0:
            break
        sync_speak(word.format(lower_bound, upper_bound, attempts), people)
        guess = None
    sync_speak("很遗憾，你没有猜对。正确的数字是{}。".format(number), people)
    with open(tmp_dir, "w") as f:
        f.write(old_content)
            
        
