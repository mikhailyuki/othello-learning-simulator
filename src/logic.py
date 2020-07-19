import random
from typing import List
import pandas as pd
import datetime
from collections import deque


class OthelloBoard:
    """
    オセロの盤面情報の保持と各種処理を行うクラス。

    :param my_stone: 自分の石の位置
    :type my_stone: int
    :param your_stone: 相手の石の位置
    :type your_stone: int
    :param now_turn: 現在の手番
    :type now_turn: int
    """

    def __init__(self,
                 my_stone: int = 0x00_00_00_08_10_00_00_00,
                 your_stone: int = 0x00_00_00_10_08_00_00_00,
                 now_turn: bool = True):
        self.my_stone: int = my_stone
        self.your_stone: int = your_stone
        self.now_turn: bool = now_turn
        self.put_list: deque[int] = deque([0])
        self.rev_list: deque[int] = deque([0])

    def can_put(self, put: int) -> bool:
        """
        指定された位置に石を置けるかどうかを判定する関数。

        :param put: 置こうとしている石の位置
        :type put: int
        :return: 指定された位置が合法手であればTrue、そうでなければFalse
        :rtype: bool
        """
        # 合法手の位置を取得
        legal_board: int = self.get_legal_board()

        return put & legal_board == put

    def reverse(self, put: int) -> bool:
        """
        指定された位置に石を置き、盤面の反転処理を行う関数。

        :param put: 石を置く位置
        :type put: int
        :return: 指定された位置が合法手であればTrue、そうでなければFalse
        :rtype: bool
        """
        # 指定された位置が合法手でなければFalseを返す
        if not self.can_put(put):
            return False

        # 反転する石の位置
        rev: int = 0

        for k in range(8):
            mask: int = self.transfer(put, k)
            tmp_rev: int = 0
            while mask & self.your_stone != 0:
                tmp_rev |= mask
                mask = self.transfer(mask, k)
            if mask & self.my_stone != 0:
                rev |= tmp_rev

        # 石を反転
        self.my_stone ^= put | rev
        self.your_stone ^= rev
        # 手番を交代
        self.my_stone, self.your_stone = self.your_stone, self.my_stone
        self.now_turn = not self.now_turn
        # 石を置いた位置を記録
        self.put_list.append(put)
        # 反転した石の位置を記録
        self.rev_list.append(rev)

        return True

    def transfer(self, put: int, k: int) -> int:
        """
        reverse()で反転する石を探索するための関数。

        :param put: 現在着目しているマスの位置
        :type put: int
        :param k: 探索方向
        :type k: int
        :return: 反転する石の位置にビットが立っている整数
        :rtype: int
        """
        if k == 0:
            return (put << 8) & 0x00_ff_ff_ff_ff_ff_ff_00
        elif k == 1:
            return (put << 7) & 0x00_7e_7e_7e_7e_7e_7e_00
        elif k == 2:
            return (put >> 1) & 0x7e_7e_7e_7e_7e_7e_7e_7e
        elif k == 3:
            return (put >> 9) & 0x00_7e_7e_7e_7e_7e_7e_00
        elif k == 4:
            return (put >> 8) & 0x00_ff_ff_ff_ff_ff_ff_00
        elif k == 5:
            return (put >> 7) & 0x00_7e_7e_7e_7e_7e_7e_00
        elif k == 6:
            return (put << 1) & 0x7e_7e_7e_7e_7e_7e_7e_7e
        elif k == 7:
            return (put << 9) & 0x00_7e_7e_7e_7e_7e_7e_00
        else:
            return 0

    def get_stone(self) -> (int, int):
        """
        現在の盤面における石の位置を(黒, 白)の形式で返す。

        :return: 石の位置
        :rtype: (int, int)
        """
        black_stone = self.my_stone if self.now_turn else self.your_stone
        white_stone = self.your_stone if self.now_turn else self.my_stone

        return black_stone, white_stone

    def get_open_num(self) -> int:
        """
        最後に指した手の開放度を返す関数。

        :return: 最後に指した手の開放度
        """
        # 空きマス
        blank_board: int = ~(self.my_stone | self.your_stone) & 0xff_ff_ff_ff_ff_ff_ff_ff
        # 最後に反転した石の位置
        last_rev: int = self.rev_list[-1]
        # 最後に反転した石の周囲の空きマス
        open_board: int = 0

        # 8方向を順に探索
        # 左
        open_board |= blank_board & (last_rev << 1)
        # 右
        open_board |= blank_board & (last_rev >> 1)
        # 上
        open_board |= blank_board & (last_rev << 8)
        # 下
        open_board |= blank_board & (last_rev >> 8)
        # 左上
        open_board |= blank_board & (last_rev << 9)
        # 右上
        open_board |= blank_board & (last_rev << 7)
        # 左下
        open_board |= blank_board & (last_rev >> 7)
        # 右下
        open_board |= blank_board & (last_rev >> 9)

        # 最後に指した手の開放度
        open_num = bin(open_board).count('1')

        return open_num

    def get_legal_board(self, flag: bool = True) -> int:
        """
        現在の盤面における合法手の位置を返す関数。

        :param flag: Trueなら自分の合法手を、Falseなら相手の合法手を返す。
        :type flag: bool
        :return: 合法手の位置
        :rtype: int
        """
        # flagの値によって視点を変える
        my_stone = self.my_stone if flag else self.your_stone
        your_stone = self.your_stone if flag else self.my_stone

        # 左右端の番兵
        horizontal_sentinel: int = your_stone & 0x7e_7e_7e_7e_7e_7e_7e_7e
        # 上下端の番兵
        vertical_sentinel: int = your_stone & 0x00_ff_ff_ff_ff_ff_ff_00
        # 四辺の番兵
        all_side_sentinel: int = your_stone & 0x00_7e_7e_7e_7e_7e_7e_00
        # 空きマス
        blank_board: int = ~(my_stone | your_stone)
        # 隣接マスに相手の石があるかどうかを調べるための一時変数
        tmp: int
        # 合法手
        legal_board: int

        # 8方向を順に探索
        # 左
        tmp = horizontal_sentinel & (my_stone << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        tmp |= horizontal_sentinel & (tmp << 1)
        legal_board = blank_board & (tmp << 1)

        # 右
        tmp = horizontal_sentinel & (my_stone >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        tmp |= horizontal_sentinel & (tmp >> 1)
        legal_board |= blank_board & (tmp >> 1)

        # 上
        tmp = vertical_sentinel & (my_stone << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        tmp |= vertical_sentinel & (tmp << 8)
        legal_board |= blank_board & (tmp << 8)

        # 下
        tmp = vertical_sentinel & (my_stone >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        tmp |= vertical_sentinel & (tmp >> 8)
        legal_board |= blank_board & (tmp >> 8)

        # 左上
        tmp = all_side_sentinel & (my_stone << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        tmp |= all_side_sentinel & (tmp << 9)
        legal_board |= blank_board & (tmp << 9)

        # 右上
        tmp = all_side_sentinel & (my_stone << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        tmp |= all_side_sentinel & (tmp << 7)
        legal_board |= blank_board & (tmp << 7)

        # 左下
        tmp = all_side_sentinel & (my_stone >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        tmp |= all_side_sentinel & (tmp >> 7)
        legal_board |= blank_board & (tmp >> 7)

        # 右下
        tmp = all_side_sentinel & (my_stone >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        tmp |= all_side_sentinel & (tmp >> 9)
        legal_board |= blank_board & (tmp >> 9)

        return legal_board

    def get_legal_list(self, flag: bool = True) -> List[int]:
        """
        現在の盤面における合法手の位置を格納したリストを返す関数。

        :return: 合法手の位置を格納したリスト。Trueなら自分の合法手を、Falseなら相手の合法手を返す。
        :rtype: List[int]
        """
        # 全ての合法手の位置を表すビット
        legal_board: int = self.get_legal_board(flag)
        # 合法手の位置を格納するリスト
        legal_list: List[int] = []
        # マスク用の変数 左上から右下まで順に1ビットずつ遷移していく
        mask: int = 0x80_00_00_00_00_00_00_00
        for i in range(64):
            if legal_board & (mask >> i) != 0:
                legal_list.append(mask >> i)

        return legal_list

    def get_confirm(self, flag: bool = True) -> int:
        """
        四辺上の確定石の位置を返す関数。

        :param flag: Trueなら自分の確定石を、Falseなら相手の確定石を探索する。
        :rtype flag: bool
        :return: 確定石の位置
        :rtype: int
        """
        # 石の位置
        stone: int = self.my_stone if flag else self.your_stone
        # 四辺上の石のみ探索対象とする
        all_side_stone: int = stone & 0xff_81_81_81_81_81_81_ff
        # 探索用の一時変数
        tmp: int
        # 確定石の位置
        confirm: int = 0

        # 上辺と下辺の左端から探索
        tmp = all_side_stone & 0x80_00_00_00_00_00_00_80
        tmp |= all_side_stone & (tmp >> 1)
        tmp |= all_side_stone & (tmp >> 1)
        tmp |= all_side_stone & (tmp >> 1)
        tmp |= all_side_stone & (tmp >> 1)
        tmp |= all_side_stone & (tmp >> 1)
        tmp |= all_side_stone & (tmp >> 1)
        confirm |= tmp

        # 上辺と下辺の右端から探索
        tmp = all_side_stone & 0x01_00_00_00_00_00_00_01
        tmp |= all_side_stone & (tmp << 1)
        tmp |= all_side_stone & (tmp << 1)
        tmp |= all_side_stone & (tmp << 1)
        tmp |= all_side_stone & (tmp << 1)
        tmp |= all_side_stone & (tmp << 1)
        tmp |= all_side_stone & (tmp << 1)
        confirm |= tmp

        # 左辺と右辺の上端から探索
        tmp = all_side_stone & 0x81_00_00_00_00_00_00_00
        tmp |= all_side_stone & (tmp >> 8)
        tmp |= all_side_stone & (tmp >> 8)
        tmp |= all_side_stone & (tmp >> 8)
        tmp |= all_side_stone & (tmp >> 8)
        tmp |= all_side_stone & (tmp >> 8)
        tmp |= all_side_stone & (tmp >> 8)
        confirm |= tmp

        # 左辺と右辺の下端から探索
        tmp = all_side_stone & 0x00_00_00_00_00_00_00_81
        tmp |= all_side_stone & (tmp << 8)
        tmp |= all_side_stone & (tmp << 8)
        tmp |= all_side_stone & (tmp << 8)
        tmp |= all_side_stone & (tmp << 8)
        tmp |= all_side_stone & (tmp << 8)
        tmp |= all_side_stone & (tmp << 8)
        confirm |= tmp

        return confirm

    def print_board(self):
        """
        与えられた盤面をコンソールに出力する関数。
        TODO あくまでCUI用の関数なので削除予定

        """
        # 合法手の位置
        legal_board: int = self.get_legal_board()
        # マスク用の変数 左上から右下まで順に1ビットずつ遷移していく
        mask: int = 0x80_00_00_00_00_00_00_00
        # 黒石と白石の位置
        black_stone: int
        white_stone: int
        # 手番によってmy_stoneとyour_stoneのどちらを参照するかが変わる
        if self.now_turn:
            black_stone = self.my_stone
            white_stone = self.your_stone
        else:
            black_stone = self.your_stone
            white_stone = self.my_stone

        for i in range(8):
            for j in range(8):
                tmp_mask: int = mask >> (i * 8 + j)
                if black_stone & tmp_mask > 0:
                    print('●', end='')
                elif white_stone & tmp_mask > 0:
                    print('○', end='')
                elif legal_board & tmp_mask > 0:
                    print('※', end='')
                else:
                    print('　', end='')
            print('')

    def pass_turn(self):
        """
        手番のパス処理を行う関数。

        """
        # 手番を交代
        self.my_stone, self.your_stone = self.your_stone, self.my_stone
        self.now_turn = not self.now_turn
        # 各dequeには0をpushする
        self.put_list.append(0)
        self.rev_list.append(0)

    def before_turn(self):
        """
        盤面を直前の手番の状態に戻す関数。

        """
        # 1手目の場合処理しない
        if len(self.put_list) == 1:
            return
        # 手番を変える
        self.my_stone, self.your_stone = self.your_stone, self.my_stone
        self.now_turn = not self.now_turn
        # 直前に石を置いた位置
        last_put = self.put_list.pop()
        # 直前に反転した石の位置
        last_rev = self.rev_list.pop()
        self.my_stone ^= last_put | last_rev
        self.your_stone ^= last_rev

    def is_end(self) -> bool:
        """
        終局判定を行う関数。

        :return: 互いに合法手が存在しなければTrueを返す
        :rtype: bool
        """
        flag1 = self.get_legal_board()
        flag2 = self.get_legal_board(False)

        return flag1 == 0 and flag2 == 0

    def judge(self) -> int:
        """
        勝敗判定を行う関数。

        :return: 自分の勝利なら1、相手の勝利なら-1、引き分けなら0を返す
        :rtype: int
        """
        # 石の数
        my_stone_count: int = bin(self.my_stone).count('1')
        your_stone_count: int = bin(self.your_stone).count('1')

        if my_stone_count > your_stone_count:
            return 1
        elif your_stone_count > my_stone_count:
            return -1
        else:
            return 0


class ArtificialIntelligence:
    """
    オセロAIの思考を司るクラス。

    :param think_depth: AIの読みの深さ
    :type think_depth: int
    :param square_value: 各マスの評価値
    :type square_value: List[int]
    :type think_depth: int
    """

    def __init__(self,
                 think_depth: int,
                 square_value: List[int]):
        self.think_depth: int = think_depth
        self.square_value: List[int] = square_value

    def random(self, now_board: 'OthelloBoard') -> int:
        """
        与えられた盤面における合法手からランダムに一手選び、それを返す関数。

        :param now_board: 盤面の情報
        :type now_board: OthelloBoard
        :return: 合法手からランダムに選んだ手(合法手がなければ-1を返す)
        :rtype: int
        """
        # 合法手の位置を格納したリスト
        legal_list: List[int] = now_board.get_legal_list()
        # 合法手がなければ-1を返し、パスとみなす
        if len(legal_list) == 0:
            return -1
        # リストの範囲内でランダムにインデックスを選ぶ
        random_num: int = random.randrange(0, len(legal_list))

        return legal_list[random_num]

    def eval_square(self, now_board: 'OthelloBoard') -> int:
        """
        与えられた盤面のマス評価値の合計を返す関数。

        :param now_board: 盤面の情報
        :type now_board: OthelloBoard
        :return: マス評価値の合計
        :rtype: int
        """
        # マス評価値の合計
        square_value_sum: int = 0
        # ビットマスク用の変数
        mask: int = 0x80_00_00_00_00_00_00_00

        # 石の位置から評価値を算出する
        for i in range(64):
            tmp_mask: int = mask >> i
            if now_board.my_stone & tmp_mask != 0:
                square_value_sum -= self.square_value[i]
            elif now_board.your_stone & tmp_mask != 0:
                square_value_sum += self.square_value[i]

        return square_value_sum

    def eval_board(self, now_board: 'OthelloBoard') -> int:
        """
        与えられた盤面の評価値を返す関数。

        :param now_board: 盤面の情報
        :type now_board: OthelloBoard
        :return: 盤面の評価値
        :rtype: int
        """
        # TODO 暫定版
        # 評価値
        value: int = 0
        # マス評価値の合計を加算
        value += self.eval_square(now_board)

        return value

    def nega_alpha(self,
                   now_depth: int,
                   now_board: 'OthelloBoard',
                   alpha: int = 10**10 * -1,
                   beta: int = 10**10) -> (int, int):
        """
        ネガアルファ法で最善手を探索する関数。

        :param now_depth: 現在の探索の深さ。上限(think_depth)に達したら盤面評価を行う。
        :type now_depth: int
        :param now_board: 現在の盤面。
        :type now_board: OthelloBoard
        :param alpha: 評価値の下限。子ノードから帰ってきた評価値とmaxをとり、betaを超えたら枝刈りする。
        :type alpha: int
        :param beta:評価値の上限。alphaがこの値を超えた時点でこのノードを探索する必要がなくなる。
        :type beta: int
        :return: 評価値と最善手。
        :rtype: (int, int)
        """
        best_put: int = -1

        # 探索木の末端か終局まで到達したら盤面の評価値を返す(前の手番から見た評価値なのでマイナスをかける必要はない)
        if now_depth == self.think_depth or now_board.is_end():
            value: int = self.eval_board(now_board)
            return value, best_put

        # 合法手のリストを取得する
        legal_list: List[int] = now_board.get_legal_list()
        # 合法手が存在しなければパスして次の手番へ
        if len(legal_list) == 0:
            # パス処理をする
            now_board.pass_turn()
            # 子ノードの評価値を再帰で取得する(alphaとbetaの値はそのまま渡す)
            child_value, _ = self.nega_alpha(now_depth + 1, now_board, alpha, beta)
            # 元の盤面に戻す
            now_board.before_turn()
            # alphaの更新を行う
            alpha = max(alpha, child_value)
            return -alpha, best_put

        # 合法手全てに枝を張る
        for legal_put in legal_list:
            # 石の反転処理をする
            now_board.reverse(legal_put)
            # 子ノードの評価値を再帰で取得する
            child_value, _ = self.nega_alpha(now_depth + 1, now_board, -beta, -alpha)
            # 元の盤面に戻す
            now_board.before_turn()
            # 子ノードの評価値がalpha(下限)を超えていればalphaを更新し、現在着目している手を最善手とする
            if child_value > alpha:
                alpha = child_value
                best_put = legal_put
            # alphaがbetaを超えた場合このノードを探索する必要がなくなるため、枝刈りをする
            if alpha >= beta:
                return -alpha, best_put

        # 現在のノードの評価値と最善手を返す
        if now_depth == 0:
            return alpha, best_put
        else:
            return -alpha, best_put


class GameRecord:
    """
    オセロの対局の各種データを記録するためのクラス。

    :param board: 盤面のインスタンス
    :type board: OthelloBoard
    :param ai_black: 黒番のAIのインスタンス
    :type ai_black: ArtificialIntelligence
    :param ai_white: 白番のAIのインスタンス
    :type ai_white: ArtificialIntelligence
    """
    def __init__(self,
                 board: 'OthelloBoard',
                 ai_black: 'ArtificialIntelligence',
                 ai_white: 'ArtificialIntelligence'):
        self.board: 'OthelloBoard' = board
        self.ai_black: 'ArtificialIntelligence' = ai_black
        self.ai_white: 'ArtificialIntelligence' = ai_white
        self.record: List[List[int]] = []
        self.score: List[List[int]] = []

    def write(self):
        """
        現在の盤面のデータを記録する。

        """
        # 石の反転処理やパス処理を行った後に呼び出すことを想定しているので、視点は逆で見る。
        # 自分の石の位置
        my_stone = self.board.your_stone
        # 相手の石の位置
        your_stone = self.board.my_stone
        # 自分の石の数
        my_stone_count: int = bin(my_stone).count('1')
        # 相手の石の数
        your_stone_count: int = bin(your_stone).count('1')
        # 現在のターン数
        turn: int = len(self.record) + 1
        # 石の数の差
        stone_diff: int = my_stone_count - your_stone_count
        # 全マスの評価値の合計
        square_value: int = \
            self.ai_black.eval_square(self.board) if self.board.now_turn else self.ai_white.eval_square(self.board)
        # 自分の合法手の数
        my_legal: int = bin(self.board.get_legal_board(False)).count('1')
        # 相手の合法手の数
        your_legal: int = bin(self.board.get_legal_board()).count('1')
        # 開放度
        open_num: int = self.board.get_open_num()
        # 自分の確定石の数
        my_confirm: int = bin(self.board.get_confirm(False)).count('1')
        # 相手の確定石の数
        your_confirm: int = bin(self.board.get_confirm()).count('1')

        # 各マスの状態を表すリスト 1は黒、-1は白、0は空白を表す
        now_score: List[int] = [0 for _ in range(66)]
        # 現在のターン数を反映
        now_score[0] = turn
        # ビットマスク用の変数
        mask: int = 0x80_00_00_00_00_00_00_00
        for i in range(64):
            if my_stone & (mask >> i) != 0:
                now_score[i + 1] = 1
            elif your_stone & (mask >> i) != 0:
                now_score[i + 1] = -1

        self.record.append([turn, stone_diff, square_value, my_legal, your_legal,
                            open_num, my_confirm, your_confirm, 0])
        self.score.append(now_score)

    def save(self):
        # 最終ターン(0-index)
        last_turn = len(self.record)
        # 対局の結果
        result = self.board.judge()
        for i in range(last_turn):
            if i % 2 == last_turn % 2:
                self.record[i][8] = result
                self.score[i][65] = result
            else:
                self.record[i][8] = result * -1
                self.score[i][65] = result * -1

        # recordの列名
        record_columns = ['turn', 'stone_diff', 'square_value', 'my_legal', 'your_legal',
                          'open_num', 'my_confirm', 'your_confirm', 'winner']
        # scoreの列名
        score_columns = ['turn',
                         'a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1',
                         'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2',
                         'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3',
                         'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4',
                         'a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5',
                         'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6',
                         'a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7',
                         'a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8',
                         'winner']
        # recordをpandas.DataFrameに変換
        df_record = pd.DataFrame(self.record, columns=record_columns).set_index('turn')
        # scoreをpandas.DataFrameに変換
        df_score = pd.DataFrame(self.score, columns=score_columns).set_index('turn')
        # 現在時刻をファイル名に適用する
        file_name = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

        df_record.to_csv(f'../data/record/record_{file_name}.csv')
        df_score.to_csv(f'../data/score/score_{file_name}.csv')
