'''
Client
'''
import socket
import numpy as np
import pygame as game
import random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

game.init()
game.display.set_caption('Chess Game')
programIcon = game.image.load('images/icon.png')
game.display.set_icon(programIcon)

WIDTH = HEIGHT = 800
square_size = HEIGHT // 8
CHESSMAN = {}
screen = game.display.set_mode((800, 800))

class Socket:
    def __init__(self):
        self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, ip, port):
        try:
            self.soc.connect((ip, port))
        except:
            print("Error Connection")

    def sendall(self, msg, byte=False):
        if not byte:
            try:
                msg += "\r\n\r\n"
                self.soc.sendall(msg.encode('utf-8'))
            except socket.error as e:
                print(e)
        else:
            try:
                msg += b"\r\n\r\n"
                self.soc.sendall(msg)
            except socket.error as e:
                print(e)

    def recv(self):
        data_recv = b""
        while b"\r\n\r\n" not in data_recv:
            data_recv += self.soc.recv(1)
        temp_recv = str(data_recv.decode("utf-8"))
        temp_recv = temp_recv[:-4]
        return temp_recv

    def recv_2(self):
        data = b""
        while not b'\r\n\r\n' in data:
            data += self.soc.recv(1)
        return data

def loadImages():
    CHESSMAN[11] = game.transform.scale(game.image.load("images/bKing.png"), (square_size, square_size))
    CHESSMAN[12] = game.transform.scale(game.image.load("images/bQueen.png"), (square_size, square_size))
    CHESSMAN[13] = game.transform.scale(game.image.load("images/bBishop.png"), (square_size, square_size))
    CHESSMAN[14] = game.transform.scale(game.image.load("images/bKnight.png"), (square_size, square_size))
    CHESSMAN[15] = game.transform.scale(game.image.load("images/bRook.png"), (square_size, square_size))
    CHESSMAN[16] = game.transform.scale(game.image.load("images/bPawn.png"), (square_size, square_size))
    CHESSMAN[21] = game.transform.scale(game.image.load("images/wKing.png"), (square_size, square_size))
    CHESSMAN[22] = game.transform.scale(game.image.load("images/wQueen.png"), (square_size, square_size))
    CHESSMAN[23] = game.transform.scale(game.image.load("images/wBishop.png"), (square_size, square_size))
    CHESSMAN[24] = game.transform.scale(game.image.load("images/wKnight.png"), (square_size, square_size))
    CHESSMAN[25] = game.transform.scale(game.image.load("images/wRook.png"), (square_size, square_size))
    CHESSMAN[26] = game.transform.scale(game.image.load("images/wPawn.png"), (square_size, square_size))

def drawBoard(screen, soc, board, selectSq1, player, check, encryptor, decryptor, idsession):
    Sq1 = game.transform.scale(game.image.load("images/Sq1.png"), (square_size, square_size))
    Sq2 = game.transform.scale(game.image.load("images/Sq2.png"), (square_size, square_size))

    if not player:
        board = np.flip(board)

    for x in range(8):
        for y in range(8):
            if (x + y) % 2 == 0:
                screen.blit(Sq1, (x * square_size, y * square_size))
            else:
                screen.blit(Sq2, (x * square_size, y * square_size))

    if selectSq1 != ():
        row, column = selectSq1

        dot_icon = game.transform.scale(game.image.load("images/dot.png"), (square_size, square_size))
        dot_icon.set_alpha(200)
        if player:
            game.draw.rect(screen, "green", game.Rect(column * square_size, row * square_size, square_size, square_size), 3)
        else:
            game.draw.rect(screen, "green", game.Rect((7 - column) * square_size, (7 - row) * square_size, square_size, square_size), 3)

        temp = "PROTOCOL01P\r\n" + idsession + "\r\n" + "VALIDMOVES\r\n" + str(row) + "\r\n" + str(column)
        encrypted = encryptor.encrypt(temp.encode("utf-8"))
        soc.sendall(encrypted, True)

        data = soc.recv_2()
        data = decryptor.decrypt(data[:-4])

        prot = data.split(b"\r\n")[0]
        if prot == b"PROTOCOL01P":
            pass
        else:
            temp = "ERROR\r\n499"
            encrypted = encryptor.encrypt(temp.encode("utf-8"))
            soc.sendall(encrypted, True)
            soc.soc.close()
            window(499)
        if b"VALIDMOVES" in data:
            validMoves_len = int(data.split(b"\r\n")[2])
        elif b"ERROR" in data:
            nrerror = data.split(b"\r\n")[0]
            print(nrerror)
            soc.soc.close()
            window(401)
            return
        y = 0
        for x in range(validMoves_len):
            vm_row = int(data.split(b"\r\n")[3 + x + y])
            y = y + 1
            vm_col = int(data.split(b"\r\n")[3 + x + y])
            if player:
                screen.blit(dot_icon, (vm_col * square_size, vm_row * square_size))
            else:
                screen.blit(dot_icon, ((7 - vm_col) * square_size, (7 - vm_row) * square_size))

    if check == 1:
        temp = "PROTOCOL01P\r\n" + idsession + "\r\n" + "KINGPOS\r\n" + str(player)
        encrypted = encryptor.encrypt(temp.encode("utf-8"))
        soc.sendall(encrypted, True)

        kingposx = 0
        kingposy = 0

        data = soc.recv_2()
        data = decryptor.decrypt(data[:-4])

        prot = data.split(b"\r\n")[0]
        if prot == b"PROTOCOL01P":
            pass
        else:
            temp = "ERROR\r\n599"
            encrypted = encryptor.encrypt(temp.encode("utf-8"))
            soc.sendall(encrypted, True)
            soc.soc.close()
            window(599)
        if b"KINGPOS" in data:
            kingposx = int(data.split(b"\r\n")[2])
            kingposy = int(data.split(b"\r\n")[3])
        elif b"ERROR" in data:
            nrerror = data.split(b"\r\n")[0]
            print(nrerror)
            soc.soc.close()
            window(401)
            return
        game.draw.rect(screen, "red", game.Rect(kingposy * square_size, kingposx * square_size, square_size, square_size), 3)

    for x in range(8):
        for y in range(8):
            square = board[x][y]
            if square != 00:
                screen.blit(CHESSMAN[square], game.Rect(y * square_size, x * square_size, square_size, square_size))

def drawMove(screen, soc, board, clock, player, encryptor, decryptor, idsession):
    temp = "PROTOCOL01P\r\n" + idsession + "\r\n" +"DRAWMOVE"
    encrypted = encryptor.encrypt(temp.encode("utf-8"))
    soc.sendall(encrypted, True)

    data = soc.recv_2()
    data = decryptor.decrypt(data[:-4])

    prot = data.split(b"\r\n")[0]
    if prot == b"PROTOCOL01P":
        pass
    else:
        temp = "ERROR\r\n499"
        encrypted = encryptor.encrypt(temp.encode("utf-8"))
        soc.sendall(encrypted, True)
        soc.soc.close()
        window(499)
    if b"DRAWMOVE" in data:
        # print(data)
        sRow = int(data.split(b"\r\n")[2])
        sCol = int(data.split(b"\r\n")[3])
        eRow = int(data.split(b"\r\n")[4])
        eCol = int(data.split(b"\r\n")[5])
    elif b"ERROR" in data:
        nrerror = data.split(b"\r\n")[0]
        print(nrerror)
        soc.soc.close()
        window(401)
        return

    if not player:
        board = np.flip(board)

    if not player:
        sRow = 7 - sRow
        sCol = 7 - sCol
        eRow = 7 - eRow
        eCol = 7 - eCol

    dRow = eRow - sRow
    dColumn = eCol - sCol

    fps = 10
    frameCount = (abs(dRow) + abs(dColumn)) * fps
    for f in range(frameCount + 1):
        row, column = (sRow + dRow * f / frameCount, sCol + dColumn * f / frameCount)

        Sq1 = game.transform.scale(game.image.load("images/Sq1.png"), (square_size, square_size))
        Sq2 = game.transform.scale(game.image.load("images/Sq2.png"), (square_size, square_size))

        for x in range(8):
            for y in range(8):
                if (x + y) % 2 == 0:
                    screen.blit(Sq1, (x * square_size, y * square_size))
                else:
                    screen.blit(Sq2, (x * square_size, y * square_size))
        for x in range(8):
            for y in range(8):
                square = board[x][y]
                if square != 00:
                    screen.blit(CHESSMAN[square], game.Rect(y * square_size, x * square_size, square_size, square_size))

        if (eRow + eCol) % 2 == 0:
            endSquare = game.Rect(eCol * square_size, eRow * square_size, square_size, square_size)
            screen.blit(Sq1, endSquare)
        else:
            endSquare = game.Rect(eCol * square_size, eRow * square_size, square_size, square_size)
            screen.blit(Sq2, endSquare)

        if player:
            temp_Mv = board[sRow][sCol]
            temp_Cp = board[eRow][eCol]
        else:
            temp_Mv = board[sRow][sCol]
            temp_Cp = board[eRow][eCol]

        if temp_Cp != 00:
            screen.blit(CHESSMAN[temp_Cp], endSquare)
        screen.blit(CHESSMAN[temp_Mv], game.Rect(column * square_size, row * square_size, square_size, square_size))
        game.display.flip()
        clock.tick(60)

def main():
    pub_key_serv_str = ""
    prv_key_clnt = RSA.generate(2048)
    pub_key_clnt = prv_key_clnt.public_key()
    pub_key_clnt_str = pub_key_clnt.export_key("PEM")

    loadImages()
    run = True

    click = 0
    selectSq1 = ()
    selectSq2 = ()

    clock = game.time.Clock()

    soc = Socket()
    soc.connect("localhost", 1791)

    nr_seq = random.randint(1000, 9999)
    data = "HELLO\r\n" + str(nr_seq)
    soc.sendall(data)

    recv_data = soc.recv_2()
    if b"HELLO" in recv_data:
        nr_seq_back = int(recv_data.split(b"\r\n")[1])
        if (nr_seq + 1) != nr_seq_back:
            soc.sendall("ERROR\r\n402")
            soc.soc.close()
            window(402)

    nr_seq = nr_seq_back + 1
    data = "WAITFORPORT\r\n" + str(nr_seq)
    soc.sendall(data)

    recv_data = soc.recv_2()
    if b"PORT" in recv_data:
        port = int(recv_data.split(b"\r\n")[1])
        nr_seq_back = int(recv_data.split(b"\r\n")[2])
        if (nr_seq + 1) != nr_seq_back:
            soc.sendall("ERROR\r\n402")
            soc.soc.close()
            window(402)
    elif b"ERROR" in recv_data:
        nrerror = recv_data.split(b"\r\n")[0]
        print(nrerror)
        soc.soc.close()
        window(int(nrerror))

    nr_seq = nr_seq_back + 1
    data = "READYPORT\r\n" + str(nr_seq)
    soc.sendall(data)

    print("Port:", port)

    soc_new = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soc_new.connect(('localhost', port))

        data = b""
        while b"\r\n\r\n" not in data:
            data += soc_new.recv(1)

        y = str(data.decode('utf-8'))
        y = y[:-4]
        pub_key_serv_str = y

        soc_new.close()
    except socket.error:
        soc_new.close()
        soc.sendall("ERROR\r\n403")
        window(403)

    decryptor = PKCS1_OAEP.new(prv_key_clnt)
    pub_key_serv = RSA.import_key(pub_key_serv_str)
    encryptor = PKCS1_OAEP.new(pub_key_serv)

    soc.sendall(pub_key_clnt_str, True)

    data = soc.recv_2()
    data = decryptor.decrypt(data[:-4])
    if b"PLAYERDET" in data:
        player_num = int(data.split(b"\r\n")[1])
        gameid = int(data.split(b"\r\n")[2])
        nr_seq_back = int(data.split(b"\r\n")[3])
        if (nr_seq + 1) != nr_seq_back:
            print("ERROR402")
            soc.sendall("ERROR\r\n402")
            soc.soc.close()
            window(402)
    elif b"ERROR" in recv_data:
        nrerror = recv_data.split(b"\r\n")[0]
        soc.soc.close()
        window(nrerror)
    idsession = str(gameid * 10 + player_num)

    nr_seq = nr_seq_back + 1
    msg = "GAME\r\n" + idsession + "\r\n" + str(nr_seq) + "\r\n\r\n"
    encrypted = encryptor.encrypt(msg.encode("utf-8"))
    soc.sendall(encrypted, True)

    print("idsession", idsession)

    while run:
        clock.tick(120)
        try:
            temp = "PROTOCOL01P\r\n" + idsession + "\r\n" + "INFO"
            encrypted = encryptor.encrypt(temp.encode("utf-8"))
            soc.sendall(encrypted, True)

            data = soc.recv_2()
            data = decryptor.decrypt(data[:-4])

            prot = data.split(b"\r\n")[0]

            if prot == b"PROTOCOL01P":
                pass
            else:
                temp = "ERROR\r\n499"
                encrypted = encryptor.encrypt(temp.encode("utf-8"))
                soc.sendall(encrypted, True)
                soc.soc.close()
                window(499)
            if b"INFO" in data:
                ready = data.split(b"\r\n")[2]  # if ready to play
            elif b"ERROR" in data:
                nrerror = data.split(b"\r\n")[0]
                print(nrerror)
                soc.soc.close()
                window(401)
                break
        except:
            run = False
            print("Couldn't get game")
            break

        if ready == b"no":
            screen.fill(game.Color("red"))
            font = game.font.SysFont("Arial", 64, False, False)
            txtOb = font.render("Waiting...!", 1, game.Color('Black'))
            txtLoc = game.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - txtOb.get_width() / 2, HEIGHT / 2 - txtOb.get_height() / 2)
            screen.blit(txtOb, txtLoc)
            game.display.update()

            for x in game.event.get():
                if x.type == game.QUIT:
                    temp = encryptor.encrypt("END\r\n1".encode("utf-8"))
                    soc.sendall(temp, True)
                    game.quit()
                    run = False
        elif ready == b"end":
            end_temp = int(data.split(b"\r\n")[3])
            if end_temp == 1:
                window(1)
                break
            elif end_temp == 0:
                window(0)
                break
        else:
            board_temp = data.split(b"\r\n")[3]  # board
            who_move = int(data.split(b"\r\n")[4])
            end_game_W = int(data.split(b"\r\n")[5])
            end_game_B = int(data.split(b"\r\n")[6])
            check_W = int(data.split(b"\r\n")[7])
            check_B = int(data.split(b"\r\n")[8])

            if board_temp:
                temp = "PROTOCOL01P\r\n" + idsession + "\r\n" + "BOARD\r\n1"
                temp = encryptor.encrypt(temp.encode("utf-8"))
                soc.sendall(temp, True)

                try:
                    data_board = soc.recv_2()
                except:
                    soc.soc.close()
                    window(401)
                    break
                data_board = decryptor.decrypt(data_board[:-4])
                prot = data_board.split(b"\r\n")[0]
                if prot == b"PROTOCOL01P":
                    pass
                else:
                    temp = "ERROR\r\n499"
                    encrypted = encryptor.encrypt(temp.encode("utf-8"))
                    soc.sendall(encrypted, True)
                    soc.soc.close()
                    window(499)
                if b"BOARD" in data_board:
                    bv1 = data_board.split(b"\r\n")[2]
                elif b"ERROR" in data_board:
                    nrerror = data_board.split(b"\r\n")[0]
                    print(nrerror)
                    soc.soc.close()
                    window(1)
                    break
                try:
                    data_board = soc.recv_2()
                except:
                    soc.soc.close()
                    window(401)
                    break
                data_board = decryptor.decrypt(data_board[:-4])
                prot = data_board.split(b"\r\n")[0]
                if prot == b"PROTOCOL01P":
                    pass
                else:
                    temp = "ERROR\r\n499"
                    encrypted = encryptor.encrypt(temp.encode("utf-8"))
                    soc.sendall(encrypted, True)
                    soc.soc.close()
                    window(499)
                if b"BOARD" in data_board:
                    bv2 = data_board.split(b"\r\n")[2]
                elif b"ERROR" in data_board:
                    nrerror = data_board.split(b"\r\n")[0]
                    print(nrerror)
                    soc.soc.close()
                    window(1)
                    break

                board_temp = bv1 + bv2

            y = np.frombuffer(board_temp, dtype=np.int32)
            game_board = y.reshape(8, 8)

            if player_num:
                drawBoard(screen, soc, game_board, selectSq1, player_num, check_W, encryptor, decryptor, idsession)  # DRAW BOARD
            else:
                drawBoard(screen, soc, game_board, selectSq1, player_num, check_B, encryptor, decryptor, idsession)  # DRAW BOARD

            if end_game_W == 1:
                font = game.font.SysFont("Arial", 32, True, False)
                if player_num == 1 and end_game_W == 1:
                    txtOb = font.render("YOU LOSE", 0, game.Color('Black'))
                    txtLoc = game.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - txtOb.get_width() / 2, HEIGHT / 2 - txtOb.get_height() / 2)
                    screen.blit(txtOb, txtLoc)
                    game.time.delay(1000)
                else:
                    game.time.delay(1000)
                    temp = encryptor.encrypt("END\r\n0".encode("utf-8"))
                    soc.sendall(temp, True)
                    window(1)
            if end_game_B == 1:
                font = game.font.SysFont("Arial", 32, True, False)
                if player_num == 0 and end_game_B == 1:
                    txtOb = font.render("YOU LOSE", 0, game.Color('Black'))
                    txtLoc = game.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - txtOb.get_width() / 2, HEIGHT / 2 - txtOb.get_height() / 2)
                    screen.blit(txtOb, txtLoc)
                    game.time.delay(1000)
                else:
                    game.time.delay(1000)
                    temp = encryptor.encrypt("END\r\n0".encode("utf-8"))
                    soc.sendall(temp, True)
                    window(1)

            for x in game.event.get():
                if x.type == game.QUIT:
                    temp = encryptor.encrypt("END\r\n1".encode("utf-8"))
                    soc.sendall(temp, True)
                    game.quit()
                    run = False
                if x.type == game.MOUSEBUTTONDOWN:
                    mouse_loc = game.mouse.get_pos()
                    column = mouse_loc[0] // square_size
                    row = mouse_loc[1] // square_size
                    if who_move == player_num:
                        if selectSq1 == (row, column):
                            selectSq1 = ()
                            selectSq2 = ()
                            click = 0
                        else:
                            selectSq2 = selectSq1
                            if player_num:
                                selectSq1 = (row, column)
                            else:
                                selectSq1 = (7 - row, 7 - column)
                            click += 1
                        if click == 2:
                            temp_pc0 = int.from_bytes(selectSq2, byteorder='big') #tuple to bytes
                            temp_pc1 = int.from_bytes(selectSq1, byteorder='big')
                            temp = "PROTOCOL01P\r\n" + idsession + "\r\n" + "MOVE\r\n" + str(temp_pc0) + "\r\n" + str(temp_pc1)
                            encrypted = encryptor.encrypt(temp.encode("utf-8"))
                            soc.sendall(encrypted, True)

                            data_v1 = soc.recv_2()
                            data_v1 = decryptor.decrypt(data_v1[:-4])

                            prot = data_v1.split(b"\r\n")[0]
                            if prot == b"PROTOCOL01P":
                                pass
                            else:
                                temp = "ERROR\r\n499"
                                encrypted = encryptor.encrypt(temp.encode("utf-8"))
                                soc.sendall(encrypted, True)
                                soc.soc.close()
                                window(499)
                            if b"MOVE" in data_v1:
                                ifmoveMade = data_v1.split(b"\r\n")[2]
                                if ifmoveMade == b"moveMade":
                                    selectSq1 = ()
                                    #selectSq2 = ()
                                    click = 0

                                    drawMove(screen, soc, game_board, clock, player_num, encryptor, decryptor, idsession)
                                else:
                                    selectSq1 = ()
                                    #selectSq2 = ()
                                    click = 0
                            elif b"ERROR" in data_v1:
                                nrerror = data_v1.split(b"\r\n")[0]
                                print(nrerror)
                                soc.soc.close()
                                window(401)
                                break
                    else:
                        font = game.font.SysFont("Arial", 32, True, False)
                        txtOb = font.render("WAIT FOR OPPONENT'S MOVE ", 0, game.Color('Black'))
                        txtLoc = game.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - txtOb.get_width() / 2, HEIGHT / 2 - txtOb.get_height() / 2)
                        screen.blit(txtOb, txtLoc)
                        game.time.delay(600)
            game.display.update()

def menu():
    run = True
    clock = game.time.Clock()

    while run:
        clock.tick(60)
        screen.fill(game.Color("white"))
        font = game.font.SysFont("Arial", 64, False, False)
        txtOb = font.render("PLAY!", 1, game.Color('Black'))
        txtLoc = game.Rect(0, 0, WIDTH, HEIGHT).move(screen.get_width() / 2 - txtOb.get_width() / 2, screen.get_height() / 2 - txtOb.get_height() / 2)
        screen.blit(txtOb, txtLoc)

        game.display.update()

        for x in game.event.get():
            if x.type == game.QUIT:
                game.quit()
                run = False
            if x.type == game.MOUSEBUTTONDOWN:
                run = False
    main()

def window(win):
    run = True
    clock = game.time.Clock()

    while run:
        clock.tick(60)
        screen.fill(game.Color("white"))
        font = game.font.SysFont("Arial", 64, False, False)
        if win == 1:
            txtOb = font.render("YOU WIN!", 1, game.Color('Black'))
        elif win == 0:
            txtOb = font.render("YOU LOSE!", 1, game.Color('Black'))
        elif win == 401:
            txtOb = font.render("ERROR 401!", 1, game.Color('Black'))
        elif win == 402:
            txtOb = font.render("ERROR 402!", 1, game.Color('Black'))
        elif win == 403:
            txtOb = font.render("ERROR 403!", 1, game.Color('Black'))
        elif win == 599:
            txtOb = font.render("ERROR 599!", 1, game.Color('Black'))
        txtLoc = game.Rect(0, 0, WIDTH, HEIGHT).move(screen.get_width() / 2 - txtOb.get_width() / 2, screen.get_height() / 2 - txtOb.get_height() / 2)
        screen.blit(txtOb, txtLoc)

        game.display.update()

        for x in game.event.get():
            if x.type == game.QUIT:
                game.quit()
                run = False
            elif x.type == game.MOUSEBUTTONDOWN:
                run = False
    menu()

if __name__ == "__main__":
    menu()