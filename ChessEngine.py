"""
This class is responsible for storing all the info about the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It will also keep a move log.
"""


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
        self.inCheck = False
        self.pins = []  # keeps track of locations of pinned pieces
        self.checks = []  # keeps track of locations of pieces attacking the king

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
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        kingLocation = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        kingRow, kingCol = kingLocation
        if self.inCheck:
            if len(self.checks) == 1:  # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # blocking: to block a check, you must move a piece into one of the squares between the enemy piece and the king
                check = self.checks[0]  # check info
                checkRow, checkCol = check[0], check[1]
                # enemy piece causing the check
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []  # squares that pieces can move to
                # special case: if pieceChecking is knight, must capture knight or move king, other pieces can be blocked
                if pieceChecking[1] == 'N':
                    validSquares = [(checkRow, checkCol)]
                else:  # if piece is not a knight, we can block the check as well
                    # generate all squares where pieces can go to block the check
                    for i in range(1, 8):
                        # (check[2], check[3]) is the check direction
                        validSquare = (
                            kingRow + check[2] * i, kingCol + check[3] * i)
                        validSquares.append(validSquare)
                        # reached the piece causing check
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                    # get rid of moves that don't block check or move king
                    # go backwards when removing from a list by iterating through it
                    for i in range(len(moves) - 1, -1, -1):
                        # king not moved so this move must block or capture the pieceChecking
                        if moves[i].pieceMoved[1] != 'K':
                            # move doesn't block or capture pieceChecking
                            if not (moves[i].endRow, moves[i].endCol) in validSquares:
                                moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check, hence all moves allowed
            moves = self.getAllPossibleMoves()

        return moves

    '''
    Returns if a player is in check, a list of pins, a list of checks
    '''

    def checkForPinsAndChecks(self):
        pins = []  # squares where the ally pinned piece is and direction pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        enemyColor = 'b' if self.whiteToMove else 'w'
        allyColor = 'w' if self.whiteToMove else 'b'
        kingLocation = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        startRow, startCol = kingLocation

        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow, endCol = startRow + d[0] * i, startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != 'K':
                        if possiblePin == ():  # 1st allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece along the same direction, so no pin or check possible in this direction
                            break
                    elif endPiece[0] == enemyColor:
                        type = endPiece[1]
                        # Five possibilities here:
                        # 1. orthogonally away from king and piece is a rook
                        # 2. diagonally away from king and piece is a bishop
                        # 3. 1 square away diagonally from king and piece is a pawn
                        # 4. any direction and piece is a queen
                        # 5. any direction 1 square away and piece is a king
                        if (0 <= j < 3 and type == 'R') or (4 <= j < 7 and type == 'B') or (i == 1 and type == 'P' and ((enemyColor == 'w' and 6 <= j <= 7) or (enemyColor == 'b' and 4 <= j <= 5))) or (type == 'Q') or (i == 1 and type == 'K'):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # there is a pin in this direction
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying check
                            break
                else:  # off board
                    break
        # check for knight checks
        knightDirections = ((2, 1), (2, -1), (-2, 1), (-2, -1),
                            (1, 2), (1, -2), (-1, 2), (-1, -2))
        for d in knightDirections:
            endRow, endCol = startRow + d[0], startCol + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                # enemy knight attacking king
                if endPiece[0] == enemyColor and endPiece[1] == 'N':
                    inCheck = True
                    checks.append((endRow, endCol, d[0], d[1]))
                else:
                    break
        return inCheck, pins, checks

    '''
    Determine if the current player is under check
    '''

    '''def inCheck(self):
        kingLocation = self.whiteKingLocation if self.whiteToMove else self.blackKingLocation
        return self.squareUnderAttack(kingLocation[0], kingLocation[1])

    ''
    Determine if the square (r, c) is under attack
    ''

    def squareUnderAttack(self, r, c):
        # switch to opponent's turn to get opponent's moves
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False'''

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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:  # white pawn moves
            # pawn advances
            if self.board[row - 1][col] == '--':  # 1 square advance
                # can move only if not pinned or if pinned, in the pin direction
                if not piecePinned or pinDirection == (-1, 0):
                    moves.append(Move((row, col), (row - 1, col), self.board))
                    # 2 square advance
                    if row == 6 and self.board[row - 2][col] == '--':
                        moves.append(
                            Move((row, col), (row - 2, col), self.board))
            # pawn captures
            if col - 1 >= 0:  # captures to the left
                if self.board[row - 1][col - 1][0] == 'b':
                    # can move only if not pinned or if pinned, in the pin direction
                    if not piecePinned or pinDirection == (-1, -1):
                        moves.append(
                            Move((row, col), (row - 1, col - 1), self.board))
            if col + 1 <= 7:  # captures to the right
                if self.board[row - 1][col + 1][0] == 'b':
                    # can move only if not pinned or if pinned, in the pin direction
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(
                            Move((row, col), (row - 1, col + 1), self.board))

        else:  # black pawn moves
            # pawn advances
            if self.board[row + 1][col] == '--':  # 1 square advance
                # can move only if not pinned or if pinned, in the pin direction
                if not piecePinned or pinDirection == (1, 0):
                    moves.append(Move((row, col), (row + 1, col), self.board))
                    # 2 square advance
                    if row == 1 and self.board[row + 2][col] == '--':
                        moves.append(
                            Move((row, col), (row + 2, col), self.board))
            # pawn captures
            if col - 1 >= 0:  # captures to the left
                if self.board[row + 1][col - 1][0] == 'w':
                    # can move only if not pinned or if pinned, in the pin direction
                    if not piecePinned or pinDirection == (1, -1):
                        moves.append(
                            Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:  # captures to the right
                if self.board[row + 1][col + 1][0] == 'w':
                    # can move only if not pinned or if pinned, in the pin direction
                    if not piecePinned or pinDirection == (1, 1):
                        moves.append(
                            Move((row, col), (row + 1, col + 1), self.board))

    '''
    Get all the rook moves for the rook located at (row, col) and add them to the moves list
    '''

    def getRookMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                # can't remove queen from pin on rook moves, only remove it on bishop moves
                if self.board[row][col][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        # down, up, left, right
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    # add moves if not pinned, and if pinned, can move towards or away from the pin
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
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
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break

        directions = ((2, 1), (2, -1), (-2, 1), (-2, -1),
                      (1, 2), (1, -2), (-1, 2), (-1, -2))
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            endRow = row + d[0]
            endCol = col + d[1]

            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
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
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (1, -1), (-1, 1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'

        for d in directions:
            for i in range(1, 8):
                endRow = row + d[0] * i
                endCol = col + d[1] * i

                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
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
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'

        for i in range(8):
            endRow = row + rowMoves[i]
            endCol = col + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:  # not an ally
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(
                            Move((row, col), (endRow, endCol), self.board))
                    # place back king at original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (row, col)
                    else:
                        self.blackKingLocation = (row, col)


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
