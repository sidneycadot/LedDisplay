#! /usr/bin/env python

from LedDisplay import LedDisplay

import sys, time

def old_stuff(ledz):

    #ledz.deleteAll()

    #if True:
    #    for page in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    #        for line in "12345678":
    #            command = ("<L%s><P%s>" + "<FE><MA><WB><FF>" + "L%sP%s <AA>Font<AB>Font<AC>Font") % (line, page, line, page)
    #            ledz.send(command)

    ledz.send("<TA>00010100009901012359A")

    #ledz.send("<L1><PA>" + "<FA><MA><WA><FK>" + "(L1PA) <CD>Sidney")
    #ledz.send("<L1><PB>" + "<FA><MA><WB><FK>" + "(L1PB) <CA>Cadot")

    ledz.send("<L1><PA>" + "<FA><MA><WA><FK>" + "<CM>             ")
    ledz.send("<L1><PA>" + "<FA><MA><WA><FK>" + "<CL>             ")
    ledz.send("<L1><PA>" + "<FA><MA><WA><FK>" + "<CN>             ")

    # Start effect / end effect

    # Directives in the L command:
    #
    #  The "line" number of the line command is
    #
    #   <CX> where X is one of:
    #     A,B,C     red-on-black
    #     D,E,F     green-on-black
    #     G,H,I,J,K orange-on-black
    #     L         black-on-red
    #     M         black-on-green
    #     N         black-on-orange
    #     O         orange-on-green
    #     P         red-on-green
    #     Q         green-on-red
    #     R         "rasta" or "rainbow" (red/orange/green horizontal bars) on black
    #     S         "sparkly" (random color pattern on black)
    #     TUVWXYZ   red-on-black
    #
    # Default color = ORANGE
    #
    # <KD> date in format DD/MM/YY
    # <KT> time in format hh:mm

    # [L] Line             [1..8]
    # [P] Page             [A..Z]
    # [F] Leading command  [A..S]
    # [M] Speed           ----- song 1: altijd is kortjakje ziek
    # [W] Waiting
    # [F] Effect

    #command = "<L1><PA>" + "<FE><MA><WB><FF>" + "L1PA"
    #ledz.send(command)
    #time.sleep(0.5)

    #command = "<L2><PA>" + "<FE><MA><WB><FF>" + "L2PA"
    #ledz.send(command)
    #time.sleep(0.5)

    #command = "<L3><PA>" + "<FE><MA><WB><FF>" + "L3PA"
    #ledz.send(command)
    #time.sleep(0.5)

    #if False:
    #    ledz.send("<TA>" "0000000000" "9900000000" "UVW")

    #ledz.send("<D*>")
    #time.sleep(0.5)

    #command = "<L1><PA>" + "<FA><MA><WB><FK>" + "PAGINA-A aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    #ledz.send(command)
    #time.sleep(0.5)

    #command = "<L1><PB>" + "<FA><MA><WB><FK>" + "PAGINA-B bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    #ledz.send(command)
    #time.sleep(0.5)

    #command = "<L1><PC>" + "<FA><MA><WB><FK>" + "PAGINA-C cccccccccccccccccccccccccccccccc"
    #ledz.send(command)
    #time.sleep(0.5)

    #for page in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        # page header is 24 bytes (6x 4-byte directives: L,P,F,M,W,F)
        # page content is 239 bytes, max. Formatting characters count as well!
        # color directive:
        #     <CA> red    foreground, black  background (spec says: dim red)
        #     <CB> red    foreground, black  background
        #     <CC> red    foreground, black  background (spec says: bright red)
        #     <CD> green  foreground, black  background (spec says: dim green)
        #     <CE> green  foreground, black  background
        #     <CF> green  foreground, black  background (spec says: bright green)
        #     <CG> orange foreground, black  background (spec says: dim orange)
        #     <CH> orange foreground, black  background
        #     <CI> orange foreground, black  background (spec says: bright orange)
        #     <CJ> orange foreground, black  background (spec says: yellow)
        #     <CK> orange foreground, black  background (spec says: lime)
        #     <CL> black  foreground, red    background
        #     <CM> black  foreground, green  background
        #     <CN> black  foreground, orange background
        #     <CO> orange foreground. green  background
        #     <CP> red    foreground, green  background (spec says: dim green)
        #     <CQ> green  foreground, red    background (spec says: dim red)

        #     <CR> "rasta:" 2 lines red, three lines orange, 2 lines green
        #     <CS> "sparkly": active bits are randomly set to red/orange/green.

        #     <CT>, <CU>, <CV>, <CW>, <CX>, <CY>, <CZ>: red (out-of-spec)

        #     <AA> font size 5x7 (Normal)
        #     <AB> font size 6x7 (Bold)
        #     <AC> font size 4x7 (Narrow)
        #     <AD> font size 7x13 (Top half)
        #     <AE> font size 7x13 (Bottom half)
        #     <AF> font size 6x8 (Top part)
        #     <AG> Not interpreted as directives...

        #letter = chr(ord(page) + 0)
        #command = "<L1><P%s>" % page + "<FA><MA><WB><FK>" + "<AC>%s" % ((letter * 5 + " ") * 3)

    #command = "<L1><PA>" "<FI><MQ><WA><FK>" + "<AB><CS><N05>PARTY TIME"
    #ledz.send(command)

    #command = "<L1><PB>" "<FA><MA><WA><FK>" + "<AB><CS><N05>PARTY TIME"
    #ledz.send(command)

    #command = "<L1><PC>" "<FA><MQ><WA><FI>" + "<AB><CS><N05>PARTY TIME"
    #ledz.send(command)

    #command = "<L1><PD>" "<FE><MQ><WA><FK>" + "<AA><CR>Welkom bij Sidney en Petra voor het vieren van de <CB><U69><CE><U69><CH>n<CB>e<CE>n<CH>d<CB>e<CE>r<CH>t<CB>i<CE>g<CH>s<CB>t<CE>e<CR> verjaardag van Petra !!!             "
    #ledz.send(command)

    #for schedule in "ABCDE":
    #    if schedule == "A":
    #        command = "<T%s>" % schedule + "0000000000" + "9800000000" + "ABBBBBBBBBBBBBBBBBBBBBBBBBBBBBCD"
    #        ledz.send(command)
    #    else:
    #        command = "<T%s>" % schedule + "9900000000" + "9900000000" + "DEF"
    #        ledz.send(command)

    #command = "<L1><PA>" + "<FA><MA><WA><FK>" + ""
    #ledz.send(command)

    #command = "<L1><PB>" + "<FA><MA><WA><FK>" + "<CA>Time: <CD><KT>"
    #ledz.send(command)

    #command = "<L1><PC>" + "<FA><MA><WA><FK>" + "<CA>Date: <CD><KD>"
    #ledz.send(command)

    #ledz.send("<DL1PA>")

    #for i in range(1, 1 + 8):
    #    ledz.send("<L%d><PB><FK><MA><WC><FK>This is line # %d" % (1, i))
    #    time.sleep(1)

    #for gp in "ABCDEFGHIJKLMNOP":
    #    for gb in [1,2,3,4,5,6,7,8]:
    #        bits = "".join(["%02X" % random.randrange(256) for i in range(64)])
    #        command = "<G%s%d>" % (gp, gb) + bits
    #        ledz.send(command)

    #for i in range(0, 10000, 8):
    #    bits = "%0128X" % (1 << i)
    #    command = "<GA1>" + bits
    #    print i, bits, command
    #    ledz.send(command)
    #    time.sleep(0.8)

        #ledz.deleteAll()

    #if True:
    #    for page in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    #        for line in "12345678":
    #            command = ("<L%s><P%s>" + "<FE><MA><WB><FF>" + "L%sP%s <AA>Font<AB>Font<AC>Font") % (line, page, line, page)
    #            ledz.send(command)

    ledz.send("<TA>00010100009901012359A")

    #ledz.send("<L1><PA>" + "<FA><MA><WA><FK>" + "(L1PA) <CD>Sidney")
    #ledz.send("<L1><PB>" + "<FA><MA><WB><FK>" + "(L1PB) <CA>Cadot")

    ledz.send("<L1><PA>" + "<FA><MA><WA><FK>" + "<CM>             ")
    ledz.send("<L1><PA>" + "<FA><MA><WA><FK>" + "<CL>             ")
    ledz.send("<L1><PA>" + "<FA><MA><WA><FK>" + "<CN>             ")

    # Start effect / end effect

    # Directives in the L command:
    #
    #  The "line" number of the line command is
    #
    #   <CX> where X is one of:
    #     A,B,C     red-on-black
    #     D,E,F     green-on-black
    #     G,H,I,J,K orange-on-black
    #     L         black-on-red
    #     M         black-on-green
    #     N         black-on-orange
    #     O         orange-on-green
    #     P         red-on-green
    #     Q         green-on-red
    #     R         "rasta" or "rainbow" (red/orange/green horizontal bars) on black
    #     S         "sparkly" (random color pattern on black)
    #     TUVWXYZ   red-on-black
    #
    # Default color = ORANGE
    #
    # <KD> date in format DD/MM/YY
    # <KT> time in format hh:mm

    # [L] Line             [1..8]
    # [P] Page             [A..Z]
    # [F] Leading command  [A..S]
    # [M] Speed           ----- song 1: altijd is kortjakje ziek
    # [W] Waiting
    # [F] Effect

    #command = "<L1><PA>" + "<FE><MA><WB><FF>" + "L1PA"
    #ledz.send(command)
    #time.sleep(0.5)

    #command = "<L2><PA>" + "<FE><MA><WB><FF>" + "L2PA"
    #ledz.send(command)
    #time.sleep(0.5)

    #command = "<L3><PA>" + "<FE><MA><WB><FF>" + "L3PA"
    #ledz.send(command)
    #time.sleep(0.5)

    #if False:
    #    ledz.send("<TA>" "0000000000" "9900000000" "UVW")

    #ledz.send("<D*>")
    #time.sleep(0.5)

    #command = "<L1><PA>" + "<FA><MA><WB><FK>" + "PAGINA-A aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    #ledz.send(command)
    #time.sleep(0.5)

    #command = "<L1><PB>" + "<FA><MA><WB><FK>" + "PAGINA-B bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    #ledz.send(command)
    #time.sleep(0.5)

    #command = "<L1><PC>" + "<FA><MA><WB><FK>" + "PAGINA-C cccccccccccccccccccccccccccccccc"
    #ledz.send(command)
    #time.sleep(0.5)

    #for page in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        # page header is 24 bytes (6x 4-byte directives: L,P,F,M,W,F)
        # page content is 239 bytes, max. Formatting characters count as well!
        # color directive:
        #     <CA> red    foreground, black  background (spec says: dim red)
        #     <CB> red    foreground, black  background
        #     <CC> red    foreground, black  background (spec says: bright red)
        #     <CD> green  foreground, black  background (spec says: dim green)
        #     <CE> green  foreground, black  background
        #     <CF> green  foreground, black  background (spec says: bright green)
        #     <CG> orange foreground, black  background (spec says: dim orange)
        #     <CH> orange foreground, black  background
        #     <CI> orange foreground, black  background (spec says: bright orange)
        #     <CJ> orange foreground, black  background (spec says: yellow)
        #     <CK> orange foreground, black  background (spec says: lime)
        #     <CL> black  foreground, red    background
        #     <CM> black  foreground, green  background
        #     <CN> black  foreground, orange background
        #     <CO> orange foreground. green  background
        #     <CP> red    foreground, green  background (spec says: dim green)
        #     <CQ> green  foreground, red    background (spec says: dim red)

        #     <CR> "rasta:" 2 lines red, three lines orange, 2 lines green
        #     <CS> "sparkly": active bits are randomly set to red/orange/green.

        #     <CT>, <CU>, <CV>, <CW>, <CX>, <CY>, <CZ>: red (out-of-spec)

        #     <AA> font size 5x7 (Normal)
        #     <AB> font size 6x7 (Bold)
        #     <AC> font size 4x7 (Narrow)
        #     <AD> font size 7x13 (Top half)
        #     <AE> font size 7x13 (Bottom half)
        #     <AF> font size 6x8 (Top part)
        #     <AG> Not interpreted as directives...

        #letter = chr(ord(page) + 0)
        #command = "<L1><P%s>" % page + "<FA><MA><WB><FK>" + "<AC>%s" % ((letter * 5 + " ") * 3)

    #command = "<L1><PA>" "<FI><MQ><WA><FK>" + "<AB><CS><N05>PARTY TIME"
    #ledz.send(command)

    #command = "<L1><PB>" "<FA><MA><WA><FK>" + "<AB><CS><N05>PARTY TIME"
    #ledz.send(command)

    #command = "<L1><PC>" "<FA><MQ><WA><FI>" + "<AB><CS><N05>PARTY TIME"
    #ledz.send(command)

    #command = "<L1><PD>" "<FE><MQ><WA><FK>" + "<AA><CR>Welkom bij Sidney en Petra voor het vieren van de <CB><U69><CE><U69><CH>n<CB>e<CE>n<CH>d<CB>e<CE>r<CH>t<CB>i<CE>g<CH>s<CB>t<CE>e<CR> verjaardag van Petra !!!             "
    #ledz.send(command)

    #for schedule in "ABCDE":
    #    if schedule == "A":
    #        command = "<T%s>" % schedule + "0000000000" + "9800000000" + "ABBBBBBBBBBBBBBBBBBBBBBBBBBBBBCD"
    #        ledz.send(command)
    #    else:
    #        command = "<T%s>" % schedule + "9900000000" + "9900000000" + "DEF"
    #        ledz.send(command)

    #command = "<L1><PA>" + "<FA><MA><WA><FK>" + ""
    #ledz.send(command)

    #command = "<L1><PB>" + "<FA><MA><WA><FK>" + "<CA>Time: <CD><KT>"
    #ledz.send(command)

    #command = "<L1><PC>" + "<FA><MA><WA><FK>" + "<CA>Date: <CD><KD>"
    #ledz.send(command)

    #ledz.send("<DL1PA>")

    #for i in range(1, 1 + 8):
    #    ledz.send("<L%d><PB><FK><MA><WC><FK>This is line # %d" % (1, i))
    #    time.sleep(1)

    #for gp in "ABCDEFGHIJKLMNOP":
    #    for gb in [1,2,3,4,5,6,7,8]:
    #        bits = "".join(["%02X" % random.randrange(256) for i in range(64)])
    #        command = "<G%s%d>" % (gp, gb) + bits
    #        ledz.send(command)

    #for i in range(0, 10000, 8):
    #    bits = "%0128X" % (1 << i)
    #    command = "<GA1>" + bits
    #    print i, bits, command
    #    ledz.send(command)
    #    time.sleep(0.8)

def temp_rv(ledz):

    last_command = ""

    print "LOOP"

    while True:
        line = raw_input()
        print ">>", line
        (timestamp, rv, temp) = line.split()
        rv = float(rv)
        temp = float(temp)

        command = "<L1><PA><FA><MA><WA><FK><AC><CD>%5.1f %% %5.1f <U3A>C" % (rv, temp)

        if command != last_command:
            ledz.send(command)
            last_command = command

def main():

    device = "/dev/ttyUSB5"

    for arg in sys.argv[1:]:
        if arg.startswith("--device="):
            device = arg[9:]

    ledz = LedDisplay(device, noisy = True)

    #  0   1  16  17  32  33  48  49
    #  2   3  18  19  34  35  50  51
    #  4   5  20  21  36  37  52  53
    #  6   7  22  23  38  39  54  55
    #  8   9  24  25  40  41  56  57
    # 10  11  26  27  42  43  58  59
    # 12  13  28  29  44  45  60  61
    # --  --  --  --  --  --  --  --

    # 00110101 '5': zwart oranje groen groen
    # 01010101 'U': groen  groen groen groen
    # 01001010 'J': groen  zwart rood  rood

    ledz.setGraphicsBlock("A", 1, "RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR" + "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG" + 5 * "OOOOOOOOBBBBBBGGBBBBBBBBOOOOOOOO")

    ledz.setSchedule("A", "A")
    ledz.send("<L1><PA><FP><MA><WC><FK>[A] (<GA1>)")

    ledz.close()

    del ledz

if __name__ == "__main__":
    main()
