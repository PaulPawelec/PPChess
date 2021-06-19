'''
Server
'''
import socket
import numpy as np
from _thread import *
import ChessGame
import random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

ThreadCount = 0
games_container = {}

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    soc.bind(("localhost", 1791))
except soc.error as err:
    print(str(err))

soc.listen(5)

def recv_2(connection):
    data = b""
    while not b'\r\n\r\n' in data:
        data += connection.recv(1)
    return data

def thread_Client_newport(port, pkstring):
    soc_new = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc_new.bind(("localhost", port))
    soc_new.listen(5)

    client_new, addr_new = soc_new.accept()
    print("Connected: " + addr_new[0])

    client_new.sendall(pkstring + b"\r\n\r\n")

    client_new.close()
    soc_new.close()
    print("Newport end")

def thread_Client(connection, player_num, games_ID):
    global ThreadCount

    recv_data = recv_2(connection)
    if b"HELLO" in recv_data:
        nr_seq = int(recv_data.split(b"\r\n")[1])

    nr_seq += 1
    data = "HELLO\r\n" + str(nr_seq) + "\r\n\r\n"
    connection.sendall(data.encode('utf-8'))

    recv_data = recv_2(connection)
    if b"WAITFORPORT" in recv_data:
        nr_seq_back = int(recv_data.split(b"\r\n")[1])
        if (nr_seq + 1) != nr_seq_back:
            print("ERROR WAIT")
            connection.sendall("402\r\nERROR\r\n\r\n".encode('utf-8'))
            connection.close()
            try:
                del games_container[games_ID]
                print("Closing Game", games_ID)
                print("Connection Lost... " + str(player_num))
                ThreadCount -= 1
                print('Thread Number: ' + str(ThreadCount))
                connection.close()
                print('End: ' + str(player_num))
                return
            except:
                print("Connection Lost... " + str(player_num))
                ThreadCount -= 1
                print('Thread Number: ' + str(ThreadCount))
                connection.close()
                print('End: ' + str(player_num))
                return
    elif b"ERROR" in recv_data:
        nrerror = recv_data.split(b"\r\n")[1]
        print("ERROR:", nrerror)
        try:
            del games_container[games_ID]
            print("Closing Game", games_ID)
            print("Connection Lost... " + str(player_num))
            ThreadCount -= 1
            print('Thread Number: ' + str(ThreadCount))
            connection.close()
            print('End: ' + str(player_num))
            return
        except:
            print("Connection Lost... " + str(player_num))
            ThreadCount -= 1
            print('Thread Number: ' + str(ThreadCount))
            connection.close()
            print('End: ' + str(player_num))
            return

    nr_seq = nr_seq_back + 1
    new_port = random.randint(50000, 65000)
    print("Port: ", new_port)
    data = "PORT\r\n" + str(new_port) + "\r\n" + str(nr_seq) + "\r\n\r\n"
    connection.sendall(data.encode('utf-8')) #send port

    recv_data = recv_2(connection)
    if b"READYPORT" in recv_data:
        nr_seq_back = int(recv_data.split(b"\r\n")[1])
        if (nr_seq + 1) != nr_seq_back:
            print("ERROR WAIT")
            connection.sendall("402\r\nERROR\r\n\r\n".encode('utf-8'))
            connection.close()
            try:
                del games_container[games_ID]
                print("Closing Game", games_ID)
                print("Connection Lost... " + str(player_num))
                ThreadCount -= 1
                print('Thread Number: ' + str(ThreadCount))
                connection.close()
                print('End: ' + str(player_num))
                return
            except:
                print("Connection Lost... " + str(player_num))
                ThreadCount -= 1
                print('Thread Number: ' + str(ThreadCount))
                connection.close()
                print('End: ' + str(player_num))
                return
    elif b"ERROR" in recv_data:
        nrerror = recv_data.split(b"\r\n")[1]
        print("ERROR:", nrerror)
        try:
            del games_container[games_ID]
            print("Closing Game", games_ID)
            print("Connection Lost... " + str(player_num))
            ThreadCount -= 1
            print('Thread Number: ' + str(ThreadCount))
            connection.close()
            print('End: ' + str(player_num))
            return
        except:
            print("Connection Lost... " + str(player_num))
            ThreadCount -= 1
            print('Thread Number: ' + str(ThreadCount))
            connection.close()
            print('End: ' + str(player_num))
            return

    prv_key_serv = RSA.generate(2048)
    pub_key_serv = prv_key_serv.public_key()
    pub_key_serv_str = pub_key_serv.export_key("PEM")

    start_new_thread(thread_Client_newport, (new_port, pub_key_serv_str))

    rec_data = recv_2(connection)
    rec_data = rec_data.decode("utf-8")
    if "ERROR" in rec_data:
        nrerror = recv_data.split(b"\r\n")[1]
        print("ERROR:", nrerror)
        print("Connection Lost! " + str(player_num))
        try:
            del games_container[games_ID]
            print("Closing Game", games_ID)
            print("Connection Lost... " + str(player_num))
            ThreadCount -= 1
            print('Thread Number: ' + str(ThreadCount))
            connection.close()
            print('End: ' + str(player_num))
            return
        except:
            print("Connection Lost... " + str(player_num))
            ThreadCount -= 1
            print('Thread Number: ' + str(ThreadCount))
            connection.close()
            print('End: ' + str(player_num))
            return

    pub_key_clnt_str = rec_data[:-4]
    pub_key_client = RSA.import_key(pub_key_clnt_str)

    decryptor = PKCS1_OAEP.new(prv_key_serv)
    encryptor = PKCS1_OAEP.new(pub_key_client)

    nr_seq = nr_seq_back + 1
    msg = "PLAYERDET\r\n" + str(player_num) + "\r\n" + str(games_ID) + "\r\n" + str(nr_seq) + "\r\n\r\n"
    encrypted = encryptor.encrypt(msg.encode("utf-8"))
    connection.sendall(encrypted + b"\r\n\r\n")

    recv_data = recv_2(connection)
    recv_data = decryptor.decrypt(recv_data[:-4])
    if b"GAME" in recv_data:
        idsession = recv_data.split(b"\r\n")[1]
        nr_seq_back = int(recv_data.split(b"\r\n")[2])
        if (nr_seq + 1) != nr_seq_back:
            print("ERROR GAME")
            connection.close()
    elif b"ERROR" in recv_data:
        nrerror = recv_data.split(b"\r\n")[1]
        print("ERROR:", nrerror)
        try:
            del games_container[games_ID]
            print("Closing Game", games_ID)
            print("Connection Lost... " + str(player_num))
            ThreadCount -= 1
            print('Thread Number: ' + str(ThreadCount))
            connection.close()
            print('End: ' + str(player_num))
            return
        except:
            print("Connection Lost... " + str(player_num))
            ThreadCount -= 1
            print('Thread Number: ' + str(ThreadCount))
            connection.close()
            print('End: ' + str(player_num))
            return

    print("idsession", idsession)

    while True:
        try:
            rec_data = recv_2(connection)
            rec_data = decryptor.decrypt(rec_data[:-4])

            close_game = False

            if games_ID in games_container:
                game_temp = games_container[games_ID]

                prot = rec_data.split(b"\r\n")[0]

                if prot == b"PROTOCOL01P":
                    idsess = rec_data.split(b"\r\n")[1]
                    if idsession == idsess:
                        pass
                    else:
                        msg = encryptor.encrypt("401\r\nERROR".encode("utf-8"))
                        connection.sendall(msg + b"\r\n\r\n")
                        close_game = True
                elif prot == b"END":
                    end = int(rec_data.split(b"\r\n")[1])
                    print("endopp: " + str(end))
                    if end == 1:
                        print("Connection Lost! " + str(player_num))
                        try:
                            del games_container[games_ID]
                            print("Closing Game", games_ID)
                            break
                        except:
                            break
                    elif end == 0:
                        game_temp.who_win = 0
                        print("Connection Lost! " + str(player_num))
                        try:
                            del games_container[games_ID]
                            print("Closing Game", games_ID)
                            break
                        except:
                            break
                    break
                elif prot == b"ERROR":
                    nrerror = rec_data.split(b"\r\n")[1]
                    print("ERROR:", nrerror)
                    close_game = True
                else:
                    break

                if b"INFO" in rec_data:
                    if game_temp.game_start:
                        game_temp.getValidMove()
                        if game_temp.who_move:
                            temp3 = b"1"
                        else:
                            temp3 = b"0"
                        if game_temp.checkMateW:
                            temp4 = b"1"
                        else:
                            temp4 = b"0"
                        if game_temp.checkMateB:
                            temp5 = b"1"
                        else:
                            temp5 = b"0"
                        if game_temp.kingCheckW:
                            temp6 = b"1"
                        else:
                            temp6 = b"0"
                        if game_temp.kingCheckB:
                            temp7 = b"1"
                        else:
                            temp7 = b"0"
                        temp = b"PROTOCOL01P\r\n" + b"INFO\r\n" + b"yes\r\n" + b"1" + b"\r\n" + temp3 + b"\r\n" + temp4 + b"\r\n" + temp5 + b"\r\n" + temp6 + b"\r\n" + temp7
                        temp = encryptor.encrypt(temp)
                        connection.sendall(temp + b"\r\n\r\n")
                    else:
                        temp = b"PROTOCOL01P\r\n" + b"INFO\r\n" + b"no"
                        temp = encryptor.encrypt(temp)
                        connection.sendall(temp + b"\r\n\r\n")
                elif b"BOARD" in rec_data:
                    boardd = game_temp.get_board()
                    temp1 = boardd[:128]
                    temp2 = boardd[128:]

                    temp = b"PROTOCOL01P\r\n" + b"BOARD\r\n" + temp1
                    temp = encryptor.encrypt(temp)
                    connection.sendall(temp + b"\r\n\r\n")

                    temp = b"PROTOCOL01P\r\n" + b"BOARD\r\n" + temp2
                    temp = encryptor.encrypt(temp)
                    connection.sendall(temp + b"\r\n\r\n")
                elif b"DRAWMOVE" in rec_data:
                    draw_move = game_temp.moves_done[-1]
                    sRow = draw_move.startRow
                    sCol = draw_move.startColumn
                    eRow = draw_move.endRow
                    eCol = draw_move.endColumn

                    temp = "PROTOCOL01P\r\n" + "DRAWMOVE\r\n" + str(sRow) + "\r\n" + str(sCol) + "\r\n" + str(eRow) + "\r\n" + str(eCol)
                    temp = encryptor.encrypt(temp.encode('utf-8'))
                    connection.sendall(temp + b"\r\n\r\n")
                elif b"VALIDMOVES" in rec_data:
                    valid_row = int(rec_data.split(b"\r\n")[3])
                    valid_col = int(rec_data.split(b"\r\n")[4])
                    temp = "PROTOCOL01P\r\n" + "VALIDMOVES\r\n"
                    temp2 = ""
                    validMoves = game_temp.getValidMove()

                    validMoves_len = 0
                    for x in validMoves:
                        if x.startRow == valid_row and x.startColumn == valid_col:
                            temp2 = temp2 + str(x.endRow) + "\r\n" + str(x.endColumn) + "\r\n"
                            validMoves_len = validMoves_len + 1

                    temp = temp + str(validMoves_len) + "\r\n" + temp2 + "\r\n"
                    temp = encryptor.encrypt(temp.encode('utf-8'))
                    connection.sendall(temp + b"\r\n\r\n")
                elif b"KINGPOS" in rec_data:
                    side = int(rec_data.split(b"\r\n")[3])
                    if side:
                        kingposx, kingposy = game_temp.find_Sq(21)
                    else:
                        kingposx, kingposy = game_temp.find_Sq(11)
                        kingposx = 7 - kingposx
                        kingposy = 7 - kingposy

                    temp = "PROTOCOL01P\r\n" + "KINGPOS\r\n" + str(kingposx) + "\r\n" + str(kingposy)
                    temp = encryptor.encrypt(temp.encode('utf-8'))
                    connection.sendall(temp + b"\r\n\r\n")
                elif b"MOVE" in rec_data:
                    player_click_row = int(rec_data.split(b"\r\n")[3])
                    player_click_row = tuple(player_click_row.to_bytes(2, byteorder='big')) #bytes to tuple
                    player_click_col = int(rec_data.split(b"\r\n")[4])
                    player_click_col = tuple(player_click_col.to_bytes(2, byteorder='big'))

                    move = ChessGame.Move(game_temp.board, player_click_row, player_click_col)
                    validMoves = game_temp.getValidMove()

                    moveMade = False
                    for y in range(len(validMoves)):
                        if move == validMoves[y]:
                            game_temp.makeMove(validMoves[y])
                            moveMade = True
                            temp = b"PROTOCOL01P\r\n" + b"MOVE\r\nmoveMade"
                            temp = encryptor.encrypt(temp)
                            connection.sendall(temp + b"\r\n\r\n")
                    if not moveMade:
                        temp = b"PROTOCOL01P\r\n" + b"MOVE\r\nmoveNotMade"
                        temp = encryptor.encrypt(temp)
                        connection.sendall(temp + b"\r\n\r\n")
                else:
                    print("Pusto")
                    break

                if close_game:
                    try:
                        del games_container[games_ID]
                        print("Closing Game", games_ID)
                        break
                    except:
                        break
            else:
                end_temp = "PROTOCOL01P\r\n" + "INFO\r\n" + "end\r\n" + str(game_temp.who_win)
                end_temp = encryptor.encrypt(end_temp.encode('utf-8'))
                connection.sendall(end_temp + b"\r\n\r\n")
                print(rec_data)
                print("Nie ma gry")
                break
        except:
            if close_game:
                try:
                    del games_container[games_ID]
                    print("Closing Game", games_ID)
                    break
                except:
                    break
            break

    print("Connection Lost... " + str(player_num))
    ThreadCount -= 1
    print('Thread Number: ' + str(ThreadCount))
    connection.close()
    print('End: ' + str(player_num))

while True:
    print("Server start")
    client, addr = soc.accept()
    print('Connected to: ' + addr[0] + ':' + str(addr[1]))

    games_ID = ThreadCount // 2
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))

    if ThreadCount % 2 == 1:
        print(games_ID)
        games_container[games_ID] = ChessGame.ChessGame(games_ID)
        print("Create Game")
        start_new_thread(thread_Client, (client, 1, games_ID)) #player w
    else:
        print(games_ID)
        games_container[games_ID].game_start = True
        print("Start Game")
        start_new_thread(thread_Client, (client, 0, games_ID)) #player b