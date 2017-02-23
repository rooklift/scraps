# This prints the Catholic sequence of prayers known as The Rosary (plus a couple
# of surrounding prayers that are not strictly part of it, I think). Anyway it's
# designed to more or less match the text of this video:
# https://www.youtube.com/watch?v=1L-Op-3DUPw

import datetime, re, time

WIDTH = 72

MEMORARE = '''Remember, O most gracious Virgin Mary, that never was it known that anyone who fled to your protection, implored your help, or sought your intercession was left unaided. Inspired with this confidence, I fly unto you, O Virgin of virgins, my Mother; to you do I come; before you I stand, sinful and sorrowful. O Mother of the Word Incarnate, despise not my petitions, but in your mercy hear and answer me. Amen.'''
SIGN_OF_THE_CROSS = '''In the name of the Father, and of the Son, and of the Holy Spirit, Amen.'''
APOSTLES_CREED = '''I believe in God, the Father Almighty, Creator of Heaven and earth; I believe in Jesus Christ, His only Son, Our Lord. He was conceived by the power of the Holy Spirit, and born of the Virgin Mary. He suffered under Pontius Pilate, was crucified, died, and was buried. He descended to the dead; on the third day He rose again. He ascended into Heaven and is seated at the right hand of the Father; He will come again to judge the living and the dead. I believe in the Holy Spirit, the Holy Catholic Church, the Communion of Saints, the forgiveness of sins, the resurrection of the body, and the life everlasting. Amen.'''
OUR_FATHER = '''Our Father, Who art in Heaven; hallowed be Thy name; Thy kingdom come; Thy will be done on earth as it is in Heaven. Give us this day our daily bread; and forgive us our trespasses, as we forgive those who trespass against us; and lead us not into temptation, but deliver us from evil. Amen.'''
HAIL_MARY = '''Hail Mary, full of grace, the Lord is with you. Blessed are you among women, and blessed is the fruit of your womb, Jesus. Holy Mary, Mother of God, pray for us sinners, now and at the hour of our death. Amen.'''
GLORY_BE = '''Glory be to the Father, and to the Son, and to the Holy Spirit, as it was in the beginning, is now, and ever shall be, world without end. Amen.'''
O_MY_JESUS = '''O my Jesus, forgive us our sins, save us from the fires of hell; lead all souls to Heaven, especially those most in need of your Mercy.'''
HAIL_HOLY_QUEEN = '''Hail, Holy Queen, Mother of Mercy, our life, our sweetness, and our hope. To you do we cry, poor banished children of Eve. To you do we send up our sighs, mourning and weeping in this valley of tears. Turn then, most gracious advocate, your eyes of mercy towards us, and after this our exile show unto us the blessed fruit of your womb, Jesus. O clement, O loving, O sweet Virgin Mary! Pray for us, O holy Mother of God, that we may be made worthy of the promises of Christ.'''
LET_US_PRAY = '''Let us pray: O God, whose only begotten Son, by His life, death and resurrection, has purchased for us the rewards of eternal life; grant, we beseech you, that while meditating on these mysteries of the Most Holy Rosary of the Blessed Virgin Mary, we may imitate what they contain and obtain what they promise, through Christ our Lord. Amen.'''
FIN = '''May the Divine assistance remain always with us. And may all the souls of the faithful departed, through the mercy of God, rest in peace. Amen.'''

joyful_mysteries = [
    "The Annunciation",
    "The Visitation",
    "The Holy Nativity",
    "The Presentation and The Purification",
    "The Finding in the Temple"
]

sorrowful_mysteries = [
    "The Agony in the Garden",
    "The Scourging at the Pillar",
    "The Crowning with Thorns",
    "The Carrying of the Cross",
    "The Crucifixion and Death of Our Lord"
]

glorious_mysteries = [
    "The Resurrection",
    "The Ascension",
    "The Descent of the Holy Spirit",
    "The Assumption",
    "The Coronation"
]

ordinals = ["1st", "2nd", "3rd", "4th", "5th"]

timings = '''
     0:10  0:50  0:57  1:46  2:17  2:35  2:54  3:13  3:26  3:39  3:53
     4:17  4:32  4:46  5:01  5:16  5:30  5:44  5:59  6:14  6:29
     6:44  6:57  7:10  7:24
     7:48  8:03  8:17  8:33  8:49  9:04  9:19  9:34  9:50 10:05
    10:21 10:34 10:47 11:03
    11:27 11:41 11:56 12:10 12:25 12:39 12:54 13:09 13:24 13:38
    13:54 14:06 14:19 14:37
    15:01 15:16 15:30 15:46 16:02 16:17 16:32 16:48 17:03 17:18
    17:34 17:47 18:00 18:18
    18:41 18:56 19:11 19:25 19:40 19:54 20:09 20:24 20:39 20:53
    21:08 21:21 21:34 22:14 22:41
    '''

class Prayer():
    def __init__(self, s, pre = None):
        self.s = s
        self.pre = pre

    def printout(self):
        if self.pre:
            print(" " + self.pre)
            print()
        output = " "
        tokens = self.s.split()
        w = 1
        for i, token in enumerate(tokens):
            if w + len(token) > WIDTH:
                output += "\n " + token
                w = 1 + len(token)
            else:
                output += token
                w += len(token)
            if i < len(tokens) - 1:     # Add space iff this isn't final token.
                if w + 1 > WIDTH:
                    output += "\n "
                    w = 1
                else:
                    output += " "
                    w += 1
        print(output)
        print()

class Announce(Prayer):
    def __init__(self, i):
        weekday = datetime.datetime.today().weekday()
        if weekday in [0, 3]:
            mystery = joyful_mysteries[i]
            adjective = "Joyful"
        elif weekday in [1, 4]:
            mystery = sorrowful_mysteries[i]
            adjective = "Sorrowful"
        else:
            mystery = glorious_mysteries[i]
            adjective = "Glorious"

        self.s  = "    Come Holy Spirit, and be with us as we meditate on:\n"
        self.s += "       The {} {} Mystery: {}".format(ordinals[i], adjective, mystery)

    def printout(self):
        print(self.s)
        print()

class Timer():
    def __init__(self, raw_times):
        self.start = time.time()
        self.times = []
        self.i = 0
        raw_times = raw_times.split()
        for s in raw_times:
            mins, secs = re.search(r"(\d+):(\d+)", s).group(1,2)
            self.times.append(int(mins) * 60 + int(secs))

    def wait(self):
        time_elapsed = time.time() - self.start
        try:
            time_to_wait = self.times[self.i] - time_elapsed
        except IndexError:
            return
        time.sleep(time_to_wait)
        self.i += 1

def main():

    sequence = []

    sequence.append(Prayer(MEMORARE))
    sequence.append(Prayer(SIGN_OF_THE_CROSS))
    sequence.append(Prayer(APOSTLES_CREED))
    sequence.append(Prayer(OUR_FATHER))
    for n in range(3):
        sequence.append(Prayer(HAIL_MARY))
    sequence.append(Prayer(GLORY_BE))
    sequence.append(Prayer(O_MY_JESUS))

    for n in range(5):
        sequence.append(Announce(n))
        sequence.append(Prayer(OUR_FATHER))
        for i in range(10):
            sequence.append(Prayer(HAIL_MARY, "({})".format(i + 1)))    # De-zeroth
        sequence.append(Prayer(GLORY_BE))
        sequence.append(Prayer(O_MY_JESUS))

    sequence.append(Prayer(HAIL_HOLY_QUEEN))
    sequence.append(Prayer(LET_US_PRAY))
    sequence.append(Prayer(FIN))

    # -------------------------------------

    timer = Timer(timings)

    print()
    for prayer in sequence:
        timer.wait()
        prayer.printout()
    input()


if __name__ == "__main__":
    main()
