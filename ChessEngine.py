"""
This class is responsible for storing all the info about the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It will also keep a move log.
"""


from shutil import move


class GameState():
    def __init__(self):
        """
        The board is an 8x8 2D list, each element is a string of 2 chars
        The first char represents the color of the piece, 'b' or 'w'
        The second char represents the type of the piece, 'K', 'Q', 'R', 'N', 'B', 'P'
        '--' represents an empty space with no piece
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunction = {'P': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves,
                             'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.stateMate = False  # when there's no valid moves and the king is not in check

    '''
    Takes a Move as a parameter and executes it (does not work for castling, pawn promotion, en passant)
    '''

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = '--'
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        # update king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        self.whiteToMove = not self.whiteToMove  # switch turns

    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            # update king's location if moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            self.whiteToMove = not self.whiteToMove  # switch turns back

    '''
    All moves considering checks
    '''

    def getValidMoves(self):
        # 1. generate all possible moves
        moves = self.getAllPossibleMoves()
        # 2. for each move, make the move
        # go backwards anytime you are iterating to remove elements from list
        for i in range(len(moves) - 1, -1, -1):
            self.makeMove(moves[i])
            # 3. generate all the opponent's moves
            # 4. for each of your opponent's moves, see if they attack your king
            # switch turns back first so inCheck works correctly, as makeMove() changed the turns
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                # 5. if they do attack your king, not a valid move
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:  # checkMate or staleMate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False
        return moves

    '''
    Determine if the current player is under check
    '''

    def inCheck(self):
        kingLocation = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        return self.squareUnderAttack(kingLocation[0], kingLocation[1])

    '''
    Determine if the square (r, c) is under attack
    '''

    def squareUnderAttack(self, r, c):
        # switch to opponent's turn to get opponent's moves
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False

    '''
    All moves not considering checks
    '''

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]  # 'b' or 'w'
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    # get all moves for the piece located at (r, c)
                    self.moveFunction[piece](r, c, moves)
        return moves

    '''
    Get all the pawn moves for the pawn located at (row, col) and add them to the moves list
    '''

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove:  # white pawn moves
            # pawn advances
            if self.board[row - 1][col] == '--':  # 1 square advance
                moves.append(Move((row, col), (row - 1, col), self.board))
                # 2 square advance
                if row == 6 and self.board[row - 2][col] == '--':
                    moves.append(Move((row, col), (row - 2, col), self.board))
            # pawn captures
            if col - 1 >= 0:  # captures to the left
                if self.board[row - 1][col - 1][0] == 'b':
                    moves.append(
                        Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7:  # captures to the right
                if self.board[row - 1][col + 1][0] == 'b':
                    moves.append(
                        Move((row, col), (row - 1, col + 1), self.board))

        else:  # black pawn moves
            # pawn advances
            if self.board[row + 1][col] == '--':  # 1 square advance
                moves.append(Move((row, col), (row + 1, col), self.board))
                # 2 square advance
                if row == 1 and self.board[row + 2][col] == '--':
                    moves.append(Move((row, col), (row + 2, col), self.board))
            # pawn captures
            if col - 1 >= 0:  # captures to the left
                if self.board[row + 1][col - 1][0] == 'w':
                    moves.append(
                        Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:  # captures to the right
                if self.board[row + 1][col + 1][0] == 'w':
                    moves.append(
                        Move((row, col), (row + 1, col + 1), self.board))

    '''
    Get all the rook moves for the rook located at (row, col) and add them to the moves list
    '''

    def getRookMoves(self, row, col, moves):
        # down, up, left, right
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # empty space
                        moves.append(
                            Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece
                        moves.append(
                            Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece
                        break
                else:  # off board
                    break

    '''
    Get all the knight moves for the knight located at (row, col) and add them to the moves list
    '''

    def getKnightMoves(self, row, col, moves):
        directions = ((2, 1), (2, -1), (-2, 1), (-2, -1),
                      (1, 2), (1, -2), (-1, 2), (-1, -2))
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece == '--':  # empty space
                    moves.append(
                        Move((row, col), (endRow, endCol), self.board))
                elif endPiece[0] == enemyColor:  # enemy piece
                    moves.append(
                        Move((row, col), (endRow, endCol), self.board))
                else:  # friendly piece
                    continue
            else:  # off board
                break

    '''
    Get all the bishop moves for the bishop located at (row, col) and add them to the moves list
    '''

    def getBishopMoves(self, row, col, moves):
        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == '--':  # empty space
                        moves.append(
                            Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:  # enemy piece
                        moves.append(
                            Move((row, col), (endRow, endCol), self.board))
                        break
                    else:  # friendly piece
                        break
                else:  # off board
                    break

    '''
    Get all the queen moves for the queen located at (row, col) and add them to the moves list
    '''

    def getQueenMoves(self, row, col, moves):
        self.getBishopMoves(row, col, moves)
        self.getRookMoves(row, col, moves)

    '''
    Get all the king moves for the king located at (row, col) and add them to the moves list
    '''

    def getKingMoves(self, row, col, moves):
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (1, -1), (-1, 1), (1, 1))
        allyColor = 'w' if self.whiteToMove else 'b'

        for i in range(8):
            endRow = row + directions[i][0]
            endCol = col + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally
                    moves.append(
                        Move((row, col), (endRow, endCol), self.board))


class Move():
    ranksToRows = {rank: row for rank, row in zip(
        [str(i) for i in range(1, 9)], range(7, -1, -1))}  # {'1': 7, ... , '8': 0}
    rowsToRanks = {row: rank for rank, row in ranksToRows.items()}
    aToH = list(map(chr, range(97, 105)))
    filesToCols = {file: col for file, col in zip(
        aToH, range(0, 8))}  # {'a': 0, ... , 'h': 7}
    colsToFiles = {col: file for file, col in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * \
            10 + self.endCol  # encapsulating all relevant 4 numbers into an ID

    '''
    Overriding the equals method so that comparing two moves doesn't compare the Move objects
    '''

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
