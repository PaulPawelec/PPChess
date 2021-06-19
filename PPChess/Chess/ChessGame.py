'''
Chess game
'''
import numpy as np

class Move:
    def __init__(self, board, startSq, endSq):
        self.startRow = startSq[0]
        self.startColumn = startSq[1]
        self.endRow = endSq[0]
        self.endColumn = endSq[1]
        self.sqPosStart = board[startSq[0]][startSq[1]]
        self.sqPosEnd = board[endSq[0]][endSq[1]]
        self.PawntoQueen = False
        if (board[self.startRow][self.startColumn] == 16 and self.endRow == 7) or (board[self.startRow][self.startColumn] == 26 and self.endRow == 0):
            self.PawntoQueen = True
        self.moveID = self.startRow * 1 + self.startColumn * 10 + self.endRow * 100 + self.endColumn * 1000

    def __eq__(self, other):
        if isinstance(other, Move):
            return  self.moveID == other.moveID
        return False

class ChessGame:
    def __init__(self, game_id):
        self.id = game_id
        self.game_start = False
        self.board = np.array([
            [15, 14, 13, 12, 11, 13, 14, 15],
            [16, 16, 16, 16, 16, 16, 16, 16],
            [00, 00, 00, 00, 00, 00, 00, 00],
            [00, 00, 00, 00, 00, 00, 00, 00],
            [00, 00, 00, 00, 00, 00, 00, 00],
            [00, 00, 00, 00, 00, 00, 00, 00],
            [26, 26, 26, 26, 26, 26, 26, 26],
            [25, 24, 23, 22, 21, 23, 24, 25]])
        self.who_move = True
        self.who_win = 1
        self.kingCheckW = False
        self.kingCheckB = False
        self.checkMateW = False
        self.checkMateB = False
        self.moves_done = []

    def start(self):
        return self.game_start

    def get_board(self):
        temp_board = self.board.flatten()
        temp_bytes = temp_board.tobytes()
        return temp_bytes

    def makeMove(self, move):
        self.board[move.startRow][move.startColumn] = 00
        self.board[move.endRow][move.endColumn] = move.sqPosStart
        self.moves_done.append(move)
        self.who_move = not self.who_move

        if move.PawntoQueen:
            self.board[move.endRow][move.endColumn] = move.sqPosStart - 4

    def backMove(self):
        if len(self.moves_done) != 0:
            move = self.moves_done.pop()
            self.board[move.startRow][move.startColumn] = move.sqPosStart
            self.board[move.endRow][move.endColumn] = move.sqPosEnd
            self.who_move = not self.who_move

    def getValidMove(self):
        possibleMoves = self.PossibleMoves()

        for x in range(len(possibleMoves) - 1, -1, -1):
            self.makeMove(possibleMoves[x])
            self.who_move = not self.who_move
            if self.who_move:
                if self.Check():
                    possibleMoves.remove(possibleMoves[x])
                    self.kingCheckW = True
                else:
                    self.kingCheckW = False
                    self.kingCheckB = False
            else:
                if self.Check():
                    possibleMoves.remove(possibleMoves[x])
                    self.kingCheckB = True
                else:
                    self.kingCheckW = False
                    self.kingCheckB = False
            self.who_move = not self.who_move
            self.backMove()
        if len(possibleMoves) == 0:
            if self.who_move:
                if self.Check():
                    self.kingCheckW = True
                    self.checkMateW = True
            else:
                if self.Check():
                    self.kingCheckB = True
                    self.checkMateB = True
        else:
            self.checkMateW = False
            self.checkMateB = False

        return possibleMoves

    def find_Sq(self, sq):
        for x in range(8):
            for y in range(8):
                temp_sq = self.board[x][y]
                if temp_sq == sq:
                    return x, y

    def Check(self):
        if self.who_move:
            row, col = self.find_Sq(21)
        else:
            row, col = self.find_Sq(11)
        self.who_move = not self.who_move
        enemyMoves = self.PossibleMoves()
        self.who_move = not self.who_move
        for x in enemyMoves:
            if x.endRow == row and x.endColumn == col:
                return True
        return False

    def PossibleMoves(self):
        moves = []
        for x in range(len(self.board)):
            for y in range(len(self.board[x])):
                turn = self.board[x][y]

                if (int(turn / 10) == 2 and self.who_move) or (int(turn / 10) == 1 and not self.who_move):
                    square = self.board[x][y]
                    if square % 10 == 1:
                        self.PossibleKingMoves(x, y, moves)
                    elif square % 10 == 2:
                        self.PossibleQueenMoves(x, y, moves)
                    elif square % 10 == 3:
                        self.PossibleBishopMoves(x, y, moves)
                    elif square % 10 == 4:
                        self.PossibleKnightMoves(x, y, moves)
                    elif square % 10 == 5:
                        self.PossibleRookMoves(x, y, moves)
                    elif square % 10 == 6:
                        self.PossiblePawnMoves(x, y, moves)
        return moves

    def PossibleKingMoves(self, row, column, moves):
        direction = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1))
        opponent = 1
        if self.who_move:
            opponent = 1
        else:
            opponent = 2
        for x in range(8):
            endRow = row + direction[x][0]
            endColumn = column + direction[x][1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8:
                endSquare = self.board[endRow][endColumn]
                if endSquare == 00:
                    moves.append(Move(self.board, (row, column), (endRow, endColumn)))
                elif int(endSquare / 10) == opponent:
                    moves.append(Move(self.board, (row, column), (endRow, endColumn)))

    def PossibleQueenMoves(self, row, column, moves):
        direction = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1))
        opponent = 1
        if self.who_move:
            opponent = 1
        else:
            opponent = 2
        for direct in direction:
            for x in range(1, 8):
                endRow = row + direct[0] * x
                endColumn = column + direct[1] * x
                if 0 <= endRow < 8 and 0 <= endColumn < 8:
                    endSquare = self.board[endRow][endColumn]
                    if endSquare == 00:
                        moves.append(Move(self.board, (row, column), (endRow, endColumn)))
                    elif int(endSquare / 10) == opponent:
                        moves.append(Move(self.board, (row, column), (endRow, endColumn)))
                        break
                    else:
                        break
                else:
                    break

    def PossibleBishopMoves(self, row, column, moves):
        direction = ((-1, -1), (1, 1), (1, -1), (-1, 1))
        opponent = 1
        if self.who_move:
            opponent = 1
        else:
            opponent = 2
        for direct in direction:
            for x in range(1, 8):
                endRow = row + direct[0] * x
                endColumn = column + direct[1] * x
                if 0 <= endRow < 8 and 0 <= endColumn < 8:
                    endSquare = self.board[endRow][endColumn]
                    if endSquare == 00:
                        moves.append(Move(self.board, (row, column), (endRow, endColumn)))
                    elif int(endSquare / 10) == opponent:
                        moves.append(Move(self.board, (row, column), (endRow, endColumn)))
                        break
                    else:
                        break
                else:
                    break

    def PossibleKnightMoves(self, row, column, moves):
        direction = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, 2), (1, -2), (2, 1), (2, -1))
        opponent = 1
        if self.who_move:
            opponent = 1
        else:
            opponent = 2
        for direct in direction:
            endRow = row + direct[0]
            endColumn = column + direct[1]
            if 0 <= endRow < 8 and 0 <= endColumn < 8:
                endSquare = self.board[endRow][endColumn]
                if endSquare == 00:
                    moves.append(Move(self.board, (row, column), (endRow, endColumn)))
                elif int(endSquare / 10) == opponent:
                    moves.append(Move(self.board, (row, column), (endRow, endColumn)))

    def PossibleRookMoves(self, row, column, moves):
        direction = ((-1, 0), (1, 0), (0, -1), (0, 1))
        opponent = 1
        if self.who_move:
            opponent = 1
        else:
            opponent = 2
        for direct in direction:
            for x in range(1, 8):
                endRow = row + direct[0] * x
                endColumn = column + direct[1] * x
                if 0 <= endRow < 8 and 0 <= endColumn < 8:
                    endSquare = self.board[endRow][endColumn]
                    if endSquare == 00:
                        moves.append(Move(self.board, (row, column), (endRow, endColumn)))
                    elif int(endSquare / 10) == opponent:
                        moves.append(Move(self.board, (row, column), (endRow, endColumn)))
                        break
                    else:
                        break
                else:
                    break


    def PossiblePawnMoves(self, row, column, moves):
        if self.who_move:
            if self.board[row - 1][column] == 00:
                moves.append(Move(self.board, (row, column), (row - 1, column)))
                if row == 6 and self.board[row - 2][column] == 00:
                    moves.append(Move(self.board, (row, column), (row - 2, column)))
            if column - 1 >= 0:
                if int(self.board[row - 1][column - 1] / 10) == 1:
                    moves.append(Move(self.board, (row, column), (row - 1, column - 1)))
            if column + 1 <= 7:
                if int(self.board[row - 1][column + 1] / 10) == 1:
                    moves.append(Move(self.board, (row, column), (row - 1, column + 1)))
        else:
            if self.board[row + 1][column] == 00:
                moves.append(Move(self.board, (row, column), (row + 1, column)))
                if row == 1 and self.board[row + 2][column] == 00:
                    moves.append(Move(self.board, (row, column), (row + 2, column)))
            if column - 1 >= 0:
                if int(self.board[row + 1][column - 1] / 10) == 2:
                    moves.append(Move(self.board, (row, column), (row + 1, column - 1)))
            if column + 1 <= 7:
                if int(self.board[row + 1][column + 1] / 10) == 2:
                    moves.append(Move(self.board, (row, column), (row + 1, column + 1)))