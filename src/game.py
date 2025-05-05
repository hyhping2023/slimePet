import random
from .voicespeak import speak, async_speak
import os
import cn2an

tmp_dir = os.path.join(os.getcwd().split("slimePet")[0], "slimePet", "tmp", "tmp.txt")
def guess_game():
    difficulties = [100, 1000, 10000]
    diffculty = random.choice(difficulties)
    number = random.randint(1, diffculty)
    lower_bound = 5
    upper_bound = diffculty
    attempts = 3
    guess = None
    word = "我已经选择了一个{}到{}之间的数字。你有{}次机会来猜测它。"
    with open(tmp_dir, "r") as f:
        old_content = f.read()
    with open(tmp_dir, "w") as f:
        f.write("")
    prev_content = ""
    async_speak(word.format(lower_bound, upper_bound, attempts))
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
            async_speak("请在{}到{}之间猜测".format(lower_bound, upper_bound))
            continue
        if guess == number:
            async_speak("恭喜你，猜对了！大吉大利，今晚吃鸡！")
            with open(tmp_dir, "w") as f:
                f.write(old_content)
            return
        elif guess < number:
            lower_bound = guess
        else:
            upper_bound = guess
        attempts -= 1
        async_speak(word.format(lower_bound, upper_bound, attempts))
        guess = None
    async_speak("很遗憾，你没有猜对。正确的数字是{}。".format(number))
    with open(tmp_dir, "w") as f:
        f.write(old_content)
            
        
