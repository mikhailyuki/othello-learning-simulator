import src.othellolib as lib


def main():
    board = lib.OthelloBoard()
    game_record = lib.GameRecord()
    ai_black = lib.ArtificialIntelligence(3)
    ai_white = lib.ArtificialIntelligence(2)

    while not board.is_end():
        game_record.write(board)
        board.print_board()
        if board.now_turn:
            _, put = ai_black.nega_alpha(0, board)
            if put != 0:
                board.reverse(put)
        else:
            _, put = ai_white.nega_alpha(0, board)
            if put != 0:
                board.reverse(put)
        board.change_turn()

    game_record.write(board)
    game_record.save()


if __name__ == '__main__':
    main()
