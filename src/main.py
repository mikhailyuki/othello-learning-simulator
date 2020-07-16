from typing import List
import src.othellolib as lib
import random
import sys


def main(loop_num: int = 1):
    for loop_count in range(loop_num):
        # 盤面のインスタンスを生成
        board = lib.OthelloBoard()
        # 各手番のマス評価値
        black_square_value: List[int] = [0 for _ in range(64)]
        white_square_value: List[int] = [0 for _ in range(64)]
        # 暫定版のためマス評価値は全てランダムで設定
        for i in range(64):
            black_square_value[i] = random.randint(-100, 100)
            white_square_value[i] = random.randint(-100, 100)
        # 各手番のAIのインスタンスを生成
        ai_black = lib.ArtificialIntelligence(3, black_square_value)
        ai_white = lib.ArtificialIntelligence(2, white_square_value)
        # 対局のデータ記録のインスタンスを生成
        game_record = lib.GameRecord(board, ai_black, ai_white)

        # 対局
        while not board.is_end():
            # board.print_board()

            if board.now_turn:
                _, put = ai_black.nega_alpha(0, board)
                if put != -1:
                    board.reverse(put)
            else:
                _, put = ai_white.nega_alpha(0, board)
                if put != -1:
                    board.reverse(put)

            # このターンのデータを記録する
            game_record.write()
            # 手番を交代
            board.change_turn()

        # board.print_board()
        game_record.save()
        print(f'{loop_count + 1}/{loop_num}局目終了')


if __name__ == '__main__':
    # コマンドライン引数を取得
    args = sys.argv

    if len(args) > 0 and args[1].isdigit():
        main(int(args[1]))
    else:
        main()
