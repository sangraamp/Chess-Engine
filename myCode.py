'''
Working but too long (getRookMoves):

        if self.whiteToMove:  # white rook moves
           # rook advances and captures
           while r - 1 >= 0:  # forward
                if self.board[r - 1][c] == '--':  # advance
                    moves.append(Move((row, col), (r - 1, c), self.board))
                    r = r - 1
                elif self.board[r - 1][c][0] == 'b':  # capture
                    moves.append(Move((row, col), (r - 1, c), self.board))
                    break
                else:  # white piece in the way
                    break
            r = row
            while r + 1 <= 7:  # backward
                if self.board[r + 1][c] == '--':  # advance
                    moves.append(Move((row, col), (r + 1, c), self.board))
                    r = r + 1
                elif self.board[r + 1][c][0] == 'b':  # capture
                    moves.append(Move((row, col), (r + 1, c), self.board))
                    break
                else:  # white piece in the way
                    break
            r = row
            while c - 1 >= 0:  # left
                if self.board[r][c - 1] == '--':  # advance
                    moves.append(Move((row, col), (r, c - 1), self.board))
                    c = c - 1
                elif self.board[r][c - 1][0] == 'b':  # capture
                    moves.append(Move((row, col), (r, c - 1), self.board))
                    break
                else:  # white piece in the way
                    break
            c = col
            while c + 1 <= 7:  # right
                if self.board[r][c + 1] == '--':  # advance
                    moves.append(Move((row, col), (r, c + 1), self.board))
                    c = c + 1
                elif self.board[r][c + 1][0] == 'b':  # capture
                    moves.append(Move((row, col), (r, c + 1), self.board))
                    break
                else:  # white piece in the way
                    break
            c = col
'''
