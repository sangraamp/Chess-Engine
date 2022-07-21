"""
This is the main driver file. It is responsible for handling user input and displaying the current GameState object
"""

import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

'''
Initialize a global dictionary of images. This will be called exactly once in the main
'''


def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK",
              "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(
            'images/' + piece + '.png'), (SQ_SIZE, SQ_SIZE))


'''
The main driver for the code. This handles user input and updating the graphics
'''


def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color('white'))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    # flag to ensure we only call getValidMoves() when it is needed as it is expensive
    validMoveMade = False
    loadImages()  # only once (expensive)
    running = True
    sqSelected = ()  # keep track of the last click of the user: tuple (row, col)
    playerClicks = []  # keep track of last two  player clicks: two tuples

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:  # moving the pieces
                location = p.mouse.get_pos()
                c = location[0] // SQ_SIZE
                r = location[1] // SQ_SIZE
                # user clicked on the same square twice (typically done to undo the selection)
                if sqSelected == (r, c):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (r, c)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(
                        playerClicks[0], playerClicks[1], gs.board)
                    if move in validMoves:
                        gs.makeMove(move)
                        validMoveMade = True
                        print(move.getChessNotation())
                        sqSelected = ()  # reset user clicks
                        playerClicks = []
                    else:  # clicked on an invalid square or on a friendly piece
                        # register that square as the new first click
                        playerClicks = [sqSelected]
            # key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move if z is pressed
                    gs.undoMove()
                    validMoveMade = True

        if validMoveMade:
            validMoves = gs.getValidMoves()  # get next set of valid moves
            validMoveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)


'''
Draw the squares on the board
'''


def drawBoard(screen):
    colors = [p.Color('white'), p.Color('gray')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            # light squares have even parity, black squares have odd parity
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(
                c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


'''
Draw the pieces on the board using the current GameState.board
'''


def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], p.Rect(
                    c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == '__main__':
    main()
