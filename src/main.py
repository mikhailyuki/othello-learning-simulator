from typing import List
import logic
import random
import sys
import time


def main(loop_num: int = 1):
    for loop_count in range(loop_num):
        # 盤面のインスタンスを生成
        board = logic.OthelloBoard()
        # 各手番のマス評価値
        black_square_value: List[int] = [0 for _ in range(64)]
        white_square_value: List[int] = [0 for _ in range(64)]
        # 暫定版のためマス評価値は全てランダムで設定
        # for i in range(64):
        #     black_square_value[i] = random.randint(-100, 100)
        #     white_square_value[i] = random.randint(-100, 100)
        # 各手番のAIのインスタンスを生成
        ai_black = logic.ArtificialIntelligence(4, black_square_value)
        ai_white = logic.ArtificialIntelligence(3, white_square_value)
        # 対局のデータ記録のインスタンスを生成
        game_record = logic.GameRecord(board, ai_black, ai_white)

        # 対局
        while not board.is_end():
            # board.print_board()

            if board.now_turn:
                _, put = ai_black.nega_alpha(0, board)
                # put = ai_black.random(board)
                if put != -1:
                    board.reverse(put)
                else:
                    board.pass_turn()
            else:
                _, put = ai_white.nega_alpha(0, board)
                # put = ai_white.random(board)
                if put != -1:
                    board.reverse(put)
                else:
                    board.pass_turn()

            # このターンのデータを記録する
            game_record.write()

        # board.print_board()
        game_record.save()
        print(f'{loop_count + 1}/{loop_num}局目終了')


if __name__ == '__main__':
    # コマンドライン引数を取得
    args = sys.argv
    # 処理時間の計測開始
    start_time = time.time()

    if len(args) > 0:
        if args[1].isdigit():
            main(int(args[1]))
        else:
            main()
    else:
        main()

    # 処理時間の計測終了
    end_time = time.time()
    progress_time = end_time - start_time
    print(f'処理時間:{progress_time}秒')
